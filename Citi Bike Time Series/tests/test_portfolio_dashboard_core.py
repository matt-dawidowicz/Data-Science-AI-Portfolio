"""Tests for portfolio dashboard, simulator, and explainability helpers."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

import citibike_portfolio_dashboard as dashboard


def lift_table() -> pd.DataFrame:
    """Build a compact station-cluster lift table for tests."""
    return pd.DataFrame(
        {
            "segment_id": ["system_total", "cluster_01", "cluster_02"],
            "segment_label": [
                "System total",
                "Cluster 01 - Alpha area",
                "Cluster 02 - Beta area",
            ],
            "mae_previous_week": [100.0, 20.0, 10.0],
            "mae_calendar_lag_ridge": [80.0, 16.0, 12.0],
            "mae_weather_event_ridge": [72.0, 12.0, 11.0],
            "mae_lift_pct_vs_previous_week": [0.28, 0.40, -0.10],
        }
    )


def priorities_table() -> pd.DataFrame:
    """Build a compact capacity-priority table for tests."""
    return pd.DataFrame(
        {
            "segment_id": ["cluster_01", "cluster_02"],
            "cluster_label": ["Cluster 01 - Alpha area", "Cluster 02 - Beta area"],
            "annual_starts": [1000.0, 250.0],
            "mae": [12.0, 11.0],
            "rmse": [15.0, 14.0],
            "wape": [0.12, 0.22],
            "capacity_planning_use": [
                "Use as a rebalancing watchlist signal.",
                "Monitor before replacing the baseline.",
            ],
        }
    )


def metrics_table() -> pd.DataFrame:
    """Build a compact model metrics table for tests."""
    rows = []
    for segment_id, segment_label, base in [
        ("system_total", "System total", 100.0),
        ("cluster_01", "Cluster 01 - Alpha area", 20.0),
        ("cluster_02", "Cluster 02 - Beta area", 12.0),
        ("cluster_03", "Cluster 03 - Gamma area", 10.0),
    ]:
        for model, label, multiplier in [
            ("weather_event_ridge", "Weather/event ridge", 0.72),
            ("calendar_lag_ridge", "Calendar + lag ridge", 0.80),
            ("previous_week", "Previous week", 1.00),
            ("previous_day", "Previous day", 1.12),
        ]:
            rows.append(
                {
                    "segment_id": segment_id,
                    "segment_label": segment_label,
                    "model": model,
                    "model_label": label,
                    "mae": base * multiplier,
                    "rmse": base * multiplier * 1.2,
                    "wape": multiplier / 5,
                }
            )
    return pd.DataFrame(rows)


def test_load_artifacts_and_json_validation(tmp_path) -> None:
    """Load required dashboard artifacts and reject malformed source JSON."""
    (tmp_path / "station_cluster_forecast_summary.json").write_text(
        json.dumps({"station_clusters": 2}), encoding="utf-8"
    )
    (tmp_path / "multi_month_proof_summary.json").write_text(
        json.dumps({"months": 12}), encoding="utf-8"
    )
    metrics_table().to_csv(tmp_path / "station_cluster_model_metrics.csv", index=False)
    lift_table().to_csv(tmp_path / "station_cluster_model_lift.csv", index=False)
    priorities_table().to_csv(
        tmp_path / "station_cluster_capacity_priorities.csv", index=False
    )

    artifacts = dashboard.load_artifacts(tmp_path)
    assert artifacts["station_summary"] == {"station_clusters": 2}
    assert len(artifacts["metrics"]) == 16

    (tmp_path / "station_cluster_forecast_summary.json").write_text(
        json.dumps([1, 2, 3]), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        dashboard.load_artifacts(tmp_path)

    (tmp_path / "station_cluster_forecast_summary.json").unlink()
    with pytest.raises(FileNotFoundError):
        dashboard.load_artifacts(tmp_path)


def test_feature_family_lift_and_column_guards() -> None:
    """Explain feature-family value with out-of-sample model comparisons."""
    feature_lift = dashboard.build_feature_family_lift(lift_table())
    assert feature_lift["feature_family"].tolist() == [
        "Calendar and lag features",
        "Weather and event features",
    ]
    assert feature_lift.loc[0, "segments_improved"] == 2
    assert feature_lift.loc[1, "segments_improved"] == 3
    assert "every evaluated segment" in feature_lift.loc[1, "interpretation"]
    assert dashboard.feature_family_interpretation("Test", 0, 0) == (
        "No evaluated segments were available."
    )
    assert "most evaluated" in dashboard.feature_family_interpretation("Test", 2, 3)
    assert "some segments" in dashboard.feature_family_interpretation("Test", 1, 3)
    assert "did not improve" in dashboard.feature_family_interpretation("Test", 0, 3)

    with pytest.raises(KeyError):
        dashboard.build_feature_family_lift(pd.DataFrame({"segment_label": []}))
    with pytest.raises(ValueError, match="no evaluated segments"):
        dashboard.build_feature_family_lift(lift_table().iloc[0:0])
    with pytest.raises(ValueError, match="nonnumeric"):
        dashboard.build_feature_family_lift(
            lift_table().assign(mae_previous_week=["bad", 1, 2])
        )
    with pytest.raises(ValueError, match="duplicate segment_id"):
        dashboard.build_feature_family_lift(
            pd.concat([lift_table(), lift_table().iloc[[0]]], ignore_index=True)
        )
    with pytest.raises(ValueError, match="negative"):
        dashboard.build_feature_family_lift(lift_table().assign(mae_previous_week=-1))

    zero_baseline_lift = lift_table().assign(
        mae_previous_week=0.0, mae_calendar_lag_ridge=0.0
    )
    zero_lift = dashboard.build_feature_family_lift(zero_baseline_lift)
    assert zero_lift.loc[0, "weighted_lift_pct"] == 0.0
    assert zero_lift.loc[0, "mean_lift_pct"] == 0.0


def test_decision_simulator_scores_tiers_and_actions() -> None:
    """Build scenario rows and classify operating-review priority."""
    scenarios = [
        dashboard.Scenario("base", "Base", 1.0, 0.0, 0.0, 0.55),
        dashboard.Scenario("event", "Event", 1.1, 0.1, 0.2, 0.45),
    ]
    simulator = dashboard.build_decision_simulator(
        priorities_table(), lift_table(), scenarios=scenarios, panel_hours=744
    )
    assert set(simulator["scenario"]) == {"base", "event"}
    assert simulator.iloc[0]["scenario"] == "base"
    for scenario in scenarios:
        scenario_rows = simulator[simulator["scenario"] == scenario.name]
        assert (
            scenario_rows.iloc[0]["risk_score"] >= scenario_rows.iloc[-1]["risk_score"]
        )
    assert simulator.loc[
        simulator["cluster_label"] == "Cluster 01 - Alpha area",
        "expected_hourly_starts",
    ].iloc[0] == pytest.approx(1000 / 744)
    assert (
        "Pre-review capacity"
        in simulator.loc[
            simulator["priority_tier"] == "High", "recommended_action"
        ].iloc[0]
    )
    assert dashboard.priority_tier(0.60, 0.55) == "High"
    assert dashboard.priority_tier(0.40, 0.55) == "Medium"
    assert dashboard.priority_tier(0.20, 0.55) == "Monitor"
    assert "Monitor against" in dashboard.recommended_action("Medium", scenarios[0])
    assert "watchlist" in dashboard.recommended_action("Monitor", scenarios[0])

    score = dashboard.scenario_risk_score(
        annual_starts=1000,
        max_annual=1000,
        wape=0.2,
        max_wape=0.2,
        mae=20,
        max_mae=20,
        lift_pct=0.1,
        scenario=scenarios[1],
    )
    assert 0 < score <= 1
    priorities_with_stale_lift = priorities_table().assign(
        mae_lift_pct_vs_previous_week=[-99.0, -99.0]
    )
    stale_simulator = dashboard.build_decision_simulator(
        priorities_with_stale_lift,
        lift_table(),
        scenarios=scenarios,
        panel_hours=744,
    )
    assert stale_simulator.loc[
        stale_simulator["cluster_label"] == "Cluster 01 - Alpha area",
        "lift_vs_previous_week",
    ].iloc[0] == pytest.approx(0.40)
    assert dashboard.build_decision_simulator(
        priorities_table().iloc[0:0],
        lift_table(),
        scenarios=scenarios,
        panel_hours=744,
    ).empty
    with pytest.raises(ValueError, match="positive integer"):
        dashboard.build_decision_simulator(
            priorities_table(),
            lift_table(),
            scenarios=scenarios,
            panel_hours=0,
        )
    with pytest.raises(ValueError, match="positive integer"):
        dashboard.build_decision_simulator(
            priorities_table(),
            lift_table(),
            scenarios=scenarios,
            panel_hours=True,
        )
    with pytest.raises(KeyError):
        dashboard.build_decision_simulator(
            priorities_table().drop(columns=["wape"]),
            lift_table(),
            scenarios=scenarios,
            panel_hours=744,
        )
    with pytest.raises(ValueError, match="Duplicate simulator"):
        dashboard.build_decision_simulator(
            priorities_table().iloc[0:0],
            lift_table(),
            scenarios=[
                dashboard.Scenario("dup", "One", 1.0, 0.0, 0.0, 0.5),
                dashboard.Scenario("dup", "Two", 1.0, 0.0, 0.0, 0.5),
            ],
            panel_hours=744,
        )


def test_decision_simulator_relationship_guards() -> None:
    """Reject duplicate, missing, and malformed simulator source relationships."""
    scenarios = [dashboard.Scenario("base", "Base", 1.0, 0.0, 0.0, 0.55)]

    with pytest.raises(ValueError, match="duplicate segment_id"):
        dashboard.build_decision_simulator(
            priorities_table(),
            pd.concat([lift_table(), lift_table().iloc[[1]]], ignore_index=True),
            scenarios=scenarios,
            panel_hours=744,
        )
    with pytest.raises(ValueError, match="duplicate segment_id"):
        dashboard.build_decision_simulator(
            pd.concat(
                [priorities_table(), priorities_table().iloc[[0]]],
                ignore_index=True,
            ),
            lift_table(),
            scenarios=scenarios,
            panel_hours=744,
        )
    with pytest.raises(ValueError, match="missing lift rows"):
        dashboard.build_decision_simulator(
            priorities_table(),
            lift_table()[lift_table()["segment_id"] != "cluster_02"],
            scenarios=scenarios,
            panel_hours=744,
        )
    with pytest.raises(ValueError, match="blank, padded, or non-string"):
        dashboard.build_decision_simulator(
            priorities_table().assign(cluster_label=["", "Cluster 02"]),
            lift_table(),
            scenarios=scenarios,
            panel_hours=744,
        )


def test_dashboard_kpis_rendering_and_formatters() -> None:
    """Render the dashboard and validate formatting helpers."""
    simulator = dashboard.build_decision_simulator(
        priorities_table(),
        lift_table(),
        scenarios=dashboard.DEFAULT_SCENARIOS[:1],
        panel_hours=744,
    )
    kpis = dashboard.select_dashboard_kpis(
        {"station_clusters": 2, "weather_event_mean_mae": 99},
        {
            "months": 12,
            "hourly_observations": 8784,
            "best_model": {"model_label": "Calendar + lag ridge"},
        },
        metrics_table(),
        simulator,
    )
    assert kpis["weather_event_mae"] == 72.0
    assert kpis["best_full_year_model"] == "Calendar + lag ridge"
    assert kpis["high_alerts"] >= 0
    fallback_kpis = dashboard.select_dashboard_kpis(
        {"station_clusters": 2, "weather_event_mean_mae": 99},
        {"best_model": "calendar_lag_ridge"},
        metrics_table().iloc[0:0],
        pd.DataFrame(),
    )
    assert fallback_kpis["weather_event_mae"] == 99
    assert fallback_kpis["best_full_year_model"] == "n/a"
    assert (
        dashboard.panel_hours_from_summary({"hourly_observations_per_segment": 744})
        == 744
    )
    with pytest.raises(KeyError):
        dashboard.panel_hours_from_summary({})
    with pytest.raises(ValueError):
        dashboard.panel_hours_from_summary({"hourly_observations_per_segment": 0})
    with pytest.raises(ValueError):
        dashboard.panel_hours_from_summary({"hourly_observations_per_segment": True})
    with pytest.raises(ValueError):
        dashboard.panel_hours_from_summary({"hourly_observations_per_segment": 744.5})
    with pytest.raises(ValueError):
        dashboard.panel_hours_from_summary({"hourly_observations_per_segment": "bad"})

    comparison = dashboard.prepare_model_comparison(metrics_table())
    assert comparison["segment_id"].nunique() == 4
    assert comparison.iloc[0]["segment_id"] == "system_total"
    assert set(comparison["model"]) == set(dashboard.MODEL_COMPARISON_MODELS)
    assert dashboard.segment_sort_key("system_total") == (0, "system_total")
    assert dashboard.segment_sort_key("cluster_01") == (1, "000001")
    assert dashboard.segment_sort_key("cluster_2") < dashboard.segment_sort_key(
        "cluster_10"
    )
    assert dashboard.segment_sort_key("custom_segment") == (2, "custom_segment")
    with pytest.raises(KeyError):
        dashboard.prepare_model_comparison(pd.DataFrame({"segment_id": []}))
    with pytest.raises(ValueError, match="no rows"):
        dashboard.prepare_model_comparison(metrics_table().assign(model="previous_day"))
    with pytest.raises(ValueError, match="duplicate segment/model"):
        dashboard.prepare_model_comparison(
            pd.concat([metrics_table(), metrics_table().iloc[[0]]], ignore_index=True)
        )
    with pytest.raises(ValueError, match="missing dashboard model"):
        dashboard.prepare_model_comparison(
            metrics_table().drop(metrics_table().index[0])
        )
    with pytest.raises(ValueError, match="system_total"):
        dashboard.prepare_model_comparison(
            metrics_table()[metrics_table()["segment_id"] != "system_total"]
        )
    with pytest.raises(ValueError, match="negative"):
        dashboard.prepare_model_comparison(metrics_table().assign(mae=-1.0))

    html = dashboard.render_html_report(
        station_summary={"station_clusters": 2},
        multi_month_summary={
            "months": 12,
            "hourly_observations": 8784,
            "best_model": {"model_label": "Calendar + lag ridge"},
        },
        metrics=metrics_table(),
        lift=lift_table(),
        priorities=priorities_table(),
        feature_lift=dashboard.build_feature_family_lift(lift_table()),
        simulator=simulator,
    )
    assert "Citi Bike Time Series Portfolio Dashboard" in html
    assert "data-scenario-button" in html
    assert "station_cluster_model_lift.png" in html
    assert html.endswith("\n")

    assert "data-scenario-row" in dashboard.simulator_table_html(simulator)
    assert "No simulator rows" in dashboard.simulator_table_html(pd.DataFrame())
    assert "data-scenario-button" in dashboard.scenario_buttons(simulator)
    assert dashboard.scenario_buttons(pd.DataFrame()) == ""
    hostile_simulator = simulator.assign(priority_tier=['High" onmouseover="x'] * 2)
    hostile_html = dashboard.simulator_table_html(hostile_simulator)
    assert 'class="tier-monitor"' in hostile_html
    assert dashboard.priority_tier_class("High") == "tier-high"
    assert "12.3%" in dashboard.table_html(
        pd.DataFrame({"share": [0.123]}),
        columns=["share"],
        rename={"share": "Share"},
        formatters={"Share": dashboard.fmt_percent},
    )
    assert dashboard.strip_trailing_whitespace("a  \n") == "a\n"
    assert dashboard.fmt_number(np.nan) == "n/a"
    assert dashboard.fmt_number(1234.56, digits=1) == "1,234.6"
    assert dashboard.fmt_percent(np.nan) == "n/a"
    assert dashboard.fmt_percent(0.125) == "12.5%"
    assert dashboard.fmt_signed_percent(np.nan) == "n/a"
    assert dashboard.fmt_signed_percent(-0.125) == "-12.5%"
    assert dashboard.safe_ratio(1, 0) == 0.0
    assert dashboard.safe_ratio(1, 4) == 0.25
    assert dashboard.coerce_float(np.nan, default=7.0) == 7.0
    assert dashboard.preview_values(range(7), limit=2) == "0, 1, ... (+5 more)"


def test_dashboard_source_and_scenario_validation() -> None:
    """Reject invalid simulator source values and scenario settings."""
    valid = dashboard.Scenario("valid", "Valid", 1.0, 0.0, 0.0, 0.5)
    assert dashboard.validate_scenarios([valid]) == [valid]

    invalid_scenarios = [
        None,
        [],
        [object()],
        [dashboard.Scenario("", "Blank name", 1.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario(" padded ", "Padded name", 1.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario(None, "Bad name", 1.0, 0.0, 0.0, 0.5)],
        [
            dashboard.Scenario("dup", "One", 1.0, 0.0, 0.0, 0.5),
            dashboard.Scenario("dup", "Two", 1.0, 0.0, 0.0, 0.5),
        ],
        [dashboard.Scenario("blank_label", "", 1.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("padded_label", " Padded", 1.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("none_label", None, 1.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("bad_multiplier", "Bad", 0.0, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("bad_weather", "Bad", 1.0, -0.1, 0.0, 0.5)],
        [dashboard.Scenario("bad_event", "Bad", 1.0, 0.0, -0.1, 0.5)],
        [dashboard.Scenario("bad_threshold", "Bad", 1.0, 0.0, 0.0, 1.1)],
        [dashboard.Scenario("not_finite", "Bad", np.inf, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("bool_value", "Bad", True, 0.0, 0.0, 0.5)],
        [dashboard.Scenario("string_value", "Bad", "bad", 0.0, 0.0, 0.5)],
    ]
    for scenarios in invalid_scenarios:
        with pytest.raises(ValueError):
            dashboard.validate_scenarios(scenarios)

    source = priorities_table().assign(mae_lift_pct_vs_previous_week=[0.1, 0.2])
    dashboard.validate_numeric_columns(
        source,
        ["annual_starts", "mae", "wape", "mae_lift_pct_vs_previous_week"],
        source_name="test source",
    )
    dashboard.validate_nonnegative_columns(
        source, ["annual_starts", "mae", "wape"], source_name="test source"
    )

    with pytest.raises(ValueError, match="nonnumeric"):
        dashboard.validate_numeric_columns(
            source.assign(mae=["bad", 1.0]), ["mae"], source_name="test source"
        )
    with pytest.raises(ValueError, match="negative"):
        dashboard.validate_nonnegative_columns(
            source.assign(wape=[-0.1, 0.2]), ["wape"], source_name="test source"
        )
    with pytest.raises(ValueError, match="finite number"):
        dashboard.validate_finite_number(np.inf, field="bad.field")

    with pytest.raises(ValueError, match="nonnumeric"):
        dashboard.build_decision_simulator(
            priorities_table(),
            lift_table().assign(mae_lift_pct_vs_previous_week=["bad", "bad", "bad"]),
            scenarios=[valid],
            panel_hours=744,
        )
