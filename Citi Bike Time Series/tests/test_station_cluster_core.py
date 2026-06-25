"""Tests for station-cluster forecasting helper functions."""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import pytest

import citibike_station_cluster_forecast as station


def station_metadata() -> pd.DataFrame:
    """Build a sorted station metadata table for clustering tests."""
    return pd.DataFrame(
        {
            "station_id": ["s1", "s2", "s3", "s4"],
            "station_name": ["Alpha", "Beta", "Gamma", "Delta"],
            "latitude": [40.70, 40.71, 40.78, 40.79],
            "longitude": [-74.00, -74.01, -73.95, -73.96],
            "annual_starts": [1000, 800, 600, 400],
        }
    )


def station_panel(days: int = 80) -> pd.DataFrame:
    """Build a deterministic segment panel with all ridge features."""
    hours = pd.date_range("2024-01-01", periods=days * 24, freq="h")
    rows = []
    for segment_id, label, kind, offset in [
        ("system_total", "System total", "system", 1000),
        ("cluster_01", "Cluster 01 - Alpha area", "station_cluster", 120),
    ]:
        rides = (
            offset
            + hours.hour.to_numpy() * 3
            + hours.dayofweek.to_numpy() * 5
            + np.arange(len(hours)) % 11
        )
        for hour, ride_count in zip(hours, rides):
            rows.append(
                {
                    "hour": hour,
                    "segment_id": segment_id,
                    "segment_label": label,
                    "segment_type": kind,
                    "rides": float(ride_count),
                    "annual_segment_starts": float(rides.sum()),
                    "segment_rank": 0 if segment_id == "system_total" else 1,
                    "share_of_system_starts": 1.0
                    if segment_id == "system_total"
                    else 0.12,
                    "temperature_2m": 12.0 + hour.hour / 24,
                    "precipitation": 0.2 if hour.hour == 8 else 0.0,
                    "snowfall": 0.0,
                    "wind_speed_10m": 8.0,
                    "weather_code": 1.0,
                    "is_precip_int": 1 if hour.hour == 8 else 0,
                    "is_snow_int": 0,
                    "temperature_below_comfort": 0.0,
                    "temperature_above_comfort": 0.0,
                    "event_intensity": 0.0,
                    "is_major_event_int": 0,
                    "is_event_peak_hour_int": 0,
                    "is_holiday_eve_int": 0,
                    "is_holiday_window_int": 0,
                    "event_names": "",
                    "event_types": "",
                    "event_windows": "",
                }
            )
    return station.add_forecast_features(
        station.add_calendar_columns(pd.DataFrame(rows))
    )


def metrics_for_lift() -> pd.DataFrame:
    """Build complete model metrics for lift and priority tests."""
    rows = []
    for segment_id, label, kind, base in [
        ("system_total", "System total", "system", 700.0),
        ("cluster_01", "Cluster 01 - Alpha area", "station_cluster", 70.0),
    ]:
        for model, mae in [
            ("previous_day", base + 80),
            ("previous_week", base + 60),
            ("calendar_lag_ridge", base + 30),
            ("weather_event_ridge", base),
        ]:
            rows.append(
                {
                    "segment_id": segment_id,
                    "segment_label": label,
                    "segment_type": kind,
                    "model": model,
                    "model_label": station.label_model(model),
                    "origins": 2,
                    "holdout_hours": 48,
                    "mean_actual": base * 2,
                    "total_actual": base * 48,
                    "mae": mae,
                    "rmse": mae * 1.2,
                    "mape": 0.1,
                    "wape": 0.15,
                    "median_origin_mae": mae,
                    "origin_wins": 1 if model == "weather_event_ridge" else 0,
                    "origin_win_rate": 0.5 if model == "weather_event_ridge" else 0,
                }
            )
    return pd.DataFrame(rows)


def test_station_ids_clustering_palettes_and_dates() -> None:
    """Validate station keys, clustering, palettes, and calendar utilities."""
    normalized = station.normalize_station_id(
        pd.Series([" 123.0 ", "unknown", None, "bike-1"])
    )
    assert normalized.tolist() == ["123", pd.NA, pd.NA, "bike-1"]

    assert pd.isna(normalized.iloc[1])

    assignments, summary = station.build_station_clusters(
        station_metadata(),
        total_system_rides=10_000,
        top_stations=4,
        cluster_count=2,
    )
    assert len(assignments) == 4
    assert summary["segment_type"].eq("station_cluster").all()
    assert summary["share_of_system_starts"].sum() == pytest.approx(0.28)
    with pytest.raises(RuntimeError):
        station.build_station_clusters(
            station_metadata().head(1),
            total_system_rides=10,
            top_stations=1,
            cluster_count=2,
        )

    labels = station.weighted_kmeans(
        np.array([[40.70, -74.0], [40.71, -74.0], [40.80, -73.9]]),
        np.array([10.0, 9.0, 1.0]),
        2,
    )
    assert set(labels) <= {0, 1}
    assert len(labels) == 3

    palette = station.cluster_palette([f"cluster_{idx:02d}" for idx in range(1, 7)])
    edge_palette = station.cluster_edge_palette(palette)
    assert palette["cluster_06"] == station.COLOR_FAMILIES["blue"]["light"]
    assert edge_palette["cluster_01"] == station.COLOR_FAMILIES["blue"]["dark"]

    assert station.month_range("2024-01", "2024-02") == ["2024-01", "2024-02"]
    with pytest.raises(ValueError):
        station.month_range("2024-03", "2024-01")
    archive = station.archive_for_month("2024-01")
    assert archive.url.endswith("202401-citibike-tripdata.zip")
    assert station.nth_weekday(2024, 1, station.calendar.MONDAY, 3).day == 15
    assert station.last_weekday(2024, 5, station.calendar.MONDAY).day == 27


def test_events_model_panel_features_and_forecasts() -> None:
    """Exercise event expansion, model-panel joins, and station forecasts."""
    holidays = station.federal_holiday_rows(2024)
    assert any(row["event_name"] == "Thanksgiving Day" for row in holidays)
    assert station.major_nyc_event_rows(2023) == []
    events = station.build_event_calendar(start_year=2024, end_year=2024)
    assert {"lead_day", "event_day", "lag_day"} <= set(events["event_window"])

    hours = pd.DataFrame(
        {
            "hour": pd.to_datetime(
                ["2024-12-31 20:00", "2024-12-30 10:00", "2024-01-03 12:00"]
            )
        }
    )
    hours["date"] = hours["hour"].dt.date.astype(str)
    hours["hour_of_day"] = hours["hour"].dt.hour
    event_features = station.build_hourly_event_features(hours, events)
    assert event_features.loc[0, "is_event_peak_hour_int"] == 1
    assert event_features.loc[1, "event_names"] == "New Year's Eve"
    assert event_features.loc[2, "event_intensity"] == 0

    raw_panel = pd.DataFrame(
        {
            "hour": pd.date_range("2024-01-01", periods=30, freq="h").tolist() * 2,
            "segment_id": ["system_total"] * 30 + ["cluster_01"] * 30,
            "segment_label": ["System total"] * 30 + ["Cluster 01 - Alpha area"] * 30,
            "segment_type": ["system"] * 30 + ["station_cluster"] * 30,
            "rides": list(range(100, 130)) + list(range(10, 40)),
        }
    )
    cluster_summary = pd.DataFrame(
        {
            "segment_id": ["cluster_01"],
            "annual_starts": [1000],
            "share_of_system_starts": [0.1],
            "rank": [1],
        }
    )
    weather = pd.DataFrame(
        {
            "hour": pd.date_range("2024-01-01", periods=30, freq="h"),
            "temperature_2m": 10.0,
            "precipitation": 0.0,
            "snowfall": 0.0,
            "wind_speed_10m": 5.0,
            "weather_code": 1.0,
            "is_precip_int": 0,
            "is_snow_int": 0,
            "temperature_below_comfort": 2.0,
            "temperature_above_comfort": 0.0,
            "weather_missing_int": 0,
        }
    )
    model_panel = station.build_model_panel(raw_panel, cluster_summary, weather, events)
    assert {"lag_24h", "event_intensity", "share_of_system_starts"} <= set(
        model_panel.columns
    )
    assert (
        model_panel.loc[model_panel["segment_id"] == "system_total", "segment_rank"]
        .eq(0)
        .all()
    )

    panel = station_panel()
    hourly_by_hour = panel[panel["segment_id"] == "cluster_01"].set_index("hour")[
        "rides"
    ]
    previous = station.forecast_from_previous(
        hourly_by_hour,
        panel[panel["segment_id"] == "cluster_01"].iloc[24:26]["hour"],
        24,
    )
    assert previous.iloc[0] == hourly_by_hour.iloc[0]
    assert (
        station.forecast_from_ridge(
            panel.head(30), panel.iloc[30:32], station.BASE_REGRESSION_FEATURES
        )
        .isna()
        .all()
    )
    ridge = station.forecast_from_ridge(
        panel[panel["segment_id"] == "cluster_01"].iloc[:800],
        panel[panel["segment_id"] == "cluster_01"].iloc[800:824],
        station.WEATHER_EVENT_FEATURES,
    )
    assert ridge.notna().all()

    metrics, origin_metrics, scored = station.build_rolling_backtests(
        panel,
        horizon_hours=24,
        min_train_days=60,
        origin_step_days=7,
    )
    assert not metrics.empty
    assert not origin_metrics.empty
    assert not scored.empty

    edge_panel = station_panel(days=3)
    edge_panel = edge_panel[
        ~(
            (edge_panel["segment_id"] == "cluster_01")
            & (edge_panel["hour"] == pd.Timestamp("2024-01-02 05:00"))
        )
    ]
    edge_metrics, edge_origin, edge_scored = station.build_rolling_backtests(
        edge_panel,
        horizon_hours=24,
        min_train_days=1,
        origin_step_days=1,
    )
    assert not edge_metrics.empty
    assert not edge_origin.empty
    assert not edge_scored.empty


def test_station_metrics_lift_priorities_summary_and_formatters() -> None:
    """Validate station metrics, lift, priority, summary, and formatting helpers."""
    assert station.score_forecast(pd.DataFrame())["n"] == 0
    scored = pd.DataFrame(
        {
            "segment_id": ["cluster_01"] * 4,
            "segment_label": ["Cluster 01 - Alpha area"] * 4,
            "segment_type": ["station_cluster"] * 4,
            "origin": [pd.Timestamp("2024-03-01")] * 4,
            "model": [
                "previous_week",
                "previous_week",
                "weather_event_ridge",
                "weather_event_ridge",
            ],
            "model_label": [
                "Previous week",
                "Previous week",
                "Weather/event ridge",
                "Weather/event ridge",
            ],
            "actual": [10.0, 20.0, 10.0, 20.0],
            "forecast": [12.0, 18.0, 11.0, 19.0],
        }
    )
    scored["error"] = scored["actual"] - scored["forecast"]
    scored["abs_error"] = scored["error"].abs()
    origin = pd.DataFrame(
        {
            "segment_id": ["cluster_01", "cluster_01"],
            "segment_label": ["Cluster 01 - Alpha area"] * 2,
            "segment_type": ["station_cluster"] * 2,
            "origin": [pd.Timestamp("2024-03-01")] * 2,
            "model": ["previous_week", "weather_event_ridge"],
            "model_label": ["Previous week", "Weather/event ridge"],
            "mae": [2.0, 1.0],
        }
    )
    aggregate = station.aggregate_model_metrics(scored, origin)
    assert (
        aggregate.loc[aggregate["model"] == "weather_event_ridge", "origin_wins"].iloc[
            0
        ]
        == 1
    )
    assert station.aggregate_model_metrics(pd.DataFrame(), pd.DataFrame()).empty

    metrics = metrics_for_lift()
    lift = station.build_model_lift(metrics)
    assert station.build_model_lift(pd.DataFrame()).empty
    assert (
        lift.loc[lift["segment_id"] == "cluster_01", "best_model"].iloc[0]
        == "weather_event_ridge"
    )
    zero_baseline_metrics = metrics.copy()
    zero_baseline_metrics.loc[
        (zero_baseline_metrics["segment_id"] == "cluster_01")
        & (zero_baseline_metrics["model"] == "previous_week"),
        "mae",
    ] = 0.0
    zero_lift = station.build_model_lift(zero_baseline_metrics)
    assert (
        zero_lift.loc[
            zero_lift["segment_id"] == "cluster_01",
            "mae_lift_pct_vs_previous_week",
        ].iloc[0]
        == 0.0
    )
    with pytest.raises(KeyError, match="missing required columns"):
        station.build_model_lift(metrics.drop(columns=["wape"]))
    with pytest.raises(ValueError, match="duplicate segment/model"):
        station.build_model_lift(pd.concat([metrics, metrics.iloc[[0]]]))
    with pytest.raises(ValueError, match="missing required model"):
        station.build_model_lift(
            metrics[
                ~(
                    (metrics["segment_id"] == "cluster_01")
                    & (metrics["model"] == "previous_week")
                )
            ]
        )
    with pytest.raises(ValueError, match="invalid values"):
        station.build_model_lift(metrics.assign(mae=np.inf))
    with pytest.raises(ValueError, match="negative"):
        station.build_model_lift(metrics.assign(mae=-1.0))

    cluster_summary = pd.DataFrame(
        {
            "segment_id": ["cluster_01"],
            "cluster_id": ["cluster_01"],
            "cluster_label": ["Cluster 01 - Alpha area"],
            "annual_starts": [1000],
            "station_count": [2],
            "center_latitude": [40.7],
            "center_longitude": [-74.0],
            "top_station": ["Alpha"],
            "share_of_system_starts": [0.1],
            "rank": [1],
            "segment_label": ["Cluster 01 - Alpha area"],
            "segment_type": ["station_cluster"],
        }
    )
    priorities = station.build_capacity_priorities(cluster_summary, metrics, lift)
    assert "rebalancing watchlist" in priorities.loc[0, "capacity_planning_use"]

    assert "Needs more validation" in station.capacity_planning_use(pd.Series({}))
    assert "secondary planning" in station.capacity_planning_use(
        pd.Series(
            {
                "mae_lift_pct_vs_previous_week": 0.01,
                "mae_lift_pct_vs_calendar_lag_ridge": 0.01,
            }
        )
    )
    assert "monitor before replacing" in station.capacity_planning_use(
        pd.Series(
            {
                "mae_lift_pct_vs_previous_week": 0.0,
                "mae_lift_pct_vs_calendar_lag_ridge": -0.01,
            }
        )
    )

    assert station.label_model("custom_model") == "Custom Model"
    strong = station.recommendation_text(
        lift[lift["segment_type"] == "station_cluster"], {}
    )
    assert "rebalancing planning layer" in strong
    weak_lift = lift.copy()
    weak_lift["mae_lift_pct_vs_calendar_lag_ridge"] = -0.1
    assert "capacity planning" in station.recommendation_text(
        weak_lift[weak_lift["segment_type"] == "station_cluster"], {}
    )
    weak_lift["mae_lift_pct_vs_previous_week"] = -0.1
    assert "diagnostics" in station.recommendation_text(
        weak_lift[weak_lift["segment_type"] == "station_cluster"], {}
    )

    summary = station.build_summary(
        args=argparse.Namespace(
            start_month="2024-01",
            end_month="2024-12",
            top_stations=2,
            horizon_hours=24,
            origin_step_days=7,
            min_train_days=60,
        ),
        monthly_summaries=pd.DataFrame(
            {
                "rows_total": [100],
                "rows_valid": [90],
                "rows_valid_fixed_window": [85],
                "rows_with_station_id": [80],
            }
        ),
        system_hourly=pd.DataFrame({"rides": [1, 2, 3]}),
        station_metadata=station_metadata(),
        cluster_summary=cluster_summary,
        panel=station_panel(days=2),
        weather=pd.DataFrame({"weather_missing_int": [0, 1]}),
        event_calendar=pd.DataFrame({"date": ["2024-01-01", "2024-01-02"]}),
        metrics=metrics,
        lift=lift,
        priorities=priorities,
    )
    assert summary["decision"] == "Rebalancing and station-capacity planning"
    assert summary["station_id_coverage"] == pytest.approx(80 / 85)
    assert station.safe_divide(1, 0) == 0.0
    assert station.safe_divide(3, 2) == 1.5

    converted = station.make_json_safe(
        {
            "stamp": pd.Timestamp("2024-01-01"),
            "items": (np.int64(1),),
            "list": [np.float64(2.5), np.bool_(True)],
            "missing": np.nan,
        }
    )
    assert converted == {
        "stamp": "2024-01-01 00:00:00",
        "items": [1],
        "list": [2.5, True],
        "missing": None,
    }
    assert station.strip_trailing_whitespace("x  \n") == "x\n"
    assert station.fmt_number(np.nan) == "n/a"
    assert station.fmt_number(1234.5, digits=1) == "1,234.5"
    assert station.fmt_percent(np.nan) == "n/a"
    assert station.fmt_percent(0.2) == "20.0%"
    assert station.fmt_signed_percent(np.nan) == "n/a"
    assert station.fmt_signed_percent(-0.125) == "-12.5%"
    assert "Station clusters" in station.chart_caption("station_cluster_map.png")
    assert station.chart_caption("custom_chart.png") == "Custom Chart"
    html = station.table_html(
        pd.DataFrame({"value": [0.2]}),
        columns=["value"],
        rename={"value": "Value"},
        formatters={"Value": station.fmt_percent},
    )
    assert "20.0%" in html
