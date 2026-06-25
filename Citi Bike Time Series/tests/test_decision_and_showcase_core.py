"""Tests for decision-report and time-series showcase helpers."""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

import citibike_decision_report as decision
import citibike_time_series_showcase as showcase


def hourly_showcase_frame(days: int = 31) -> pd.DataFrame:
    """Build a deterministic hourly frame with weather columns."""
    hours = pd.date_range("2024-01-01", periods=days * 24, freq="h")
    rides = (
        200
        + hours.hour.to_numpy() * 4
        + hours.dayofweek.to_numpy() * 7
        + np.sin(np.arange(len(hours)) / 12) * 5
    )
    return pd.DataFrame(
        {
            "hour": hours,
            "date": hours.normalize(),
            "rides": rides.astype(float),
            "day_of_week": hours.dayofweek,
            "day_name": hours.day_name(),
            "hour_of_day": hours.hour,
            "is_weekend": hours.dayofweek >= 5,
            "temperature_c": np.linspace(-5, 10, len(hours)),
            "precipitation_mm": np.where(hours.hour == 8, 0.1, 0.0),
            "snowfall_cm": np.where(hours.day == 3, 0.2, 0.0),
            "wind_speed_kmh": np.linspace(3, 16, len(hours)),
        }
    )


def write_decision_inputs(
    output_dir,
    *,
    profile: dict | None = None,
    forecast: pd.DataFrame | None = None,
    top_stations: pd.DataFrame | None = None,
    anomalies: pd.DataFrame | None = None,
) -> None:
    """Write a complete, deterministic decision-report input fixture."""
    output_dir.mkdir()
    profile = profile or {
        "rush_vs_off_hour_ratio": 2.2,
        "weekend_vs_weekday_ratio": 0.8,
        "summary": {
            "total_rides": 100_000,
            "hourly_points": 744,
            "average_daily_rides": 3200,
            "average_hourly_rides": 135,
            "peak_hour_rides": 600,
            "peak_hour": "2024-01-04 08:00:00",
        },
    }
    forecast = (
        forecast
        if forecast is not None
        else pd.DataFrame(
            {
                "model": ["calendar_profile", "previous_day", "previous_week"],
                "mae": [80.0, 100.0, 120.0],
                "rmse": [95.0, 115.0, 130.0],
                "mape": [0.10, 0.12, 0.14],
                "mean_actual": [150.0, 150.0, 150.0],
            }
        )
    )
    top_stations = (
        top_stations
        if top_stations is not None
        else pd.DataFrame(
            {
                "station": ["A&B Station", "Second Station"],
                "rides": [1000, 800],
                "share_of_valid_trips": [0.10, 0.08],
            }
        )
    )
    anomalies = (
        anomalies
        if anomalies is not None
        else pd.DataFrame(
            {
                "hour": ["2024-01-05 17:00:00"],
                "absolute_gap": [42],
            }
        )
    )
    (output_dir / "profile_summary.json").write_text(
        json.dumps(profile), encoding="utf-8"
    )
    forecast.to_csv(output_dir / "forecast_backtest_metrics.csv", index=False)
    top_stations.to_csv(output_dir / "top_stations.csv", index=False)
    anomalies.to_csv(output_dir / "anomaly_hours.csv", index=False)
    pd.DataFrame({"kind": ["member"], "share": [1.0]}).to_csv(
        output_dir / "member_mix.csv", index=False
    )
    pd.DataFrame({"kind": ["classic"], "share": [1.0]}).to_csv(
        output_dir / "bike_mix.csv", index=False
    )


def test_decision_formatting_tables_and_input_loading(tmp_path, monkeypatch) -> None:
    """Check decision-report formatters, HTML escaping, and input loading."""
    assert decision.fmt_int(1234.5) == "1,234"
    assert decision.fmt_k(1_500_000) == "1.50M"
    assert decision.fmt_k(12_300) == "12.3k"
    assert decision.fmt_k(42) == "42"
    assert decision.fmt_pct(0.1234, 2) == "12.34%"
    assert decision.fmt_num(1234.567, 2) == "1,234.57"
    assert decision.fmt_int(np.nan) == "n/a"
    assert decision.fmt_k(np.nan) == "n/a"
    assert decision.fmt_pct(np.nan) == "n/a"
    assert decision.fmt_num(np.nan) == "n/a"

    table = decision.table_html(
        pd.DataFrame({"name": ["A&B"], "value": ["<tag>"]}),
        ["name", "value"],
        ["Name", "Value"],
    )
    assert "&amp;" in table and "&lt;tag&gt;" in table
    with pytest.raises(ValueError, match="same length"):
        decision.table_html(pd.DataFrame({"name": ["A"]}), ["name"], ["Name", "Extra"])
    with pytest.raises(KeyError, match="missing required columns"):
        decision.table_html(pd.DataFrame({"name": ["A"]}), ["missing"], ["Missing"])

    output_dir = tmp_path / "outputs"
    write_decision_inputs(output_dir)
    monkeypatch.setattr(decision, "PROFILE_DIR", output_dir)
    loaded = decision.load_inputs()
    assert loaded["summary"]["hourly_points"] == 744
    assert loaded["forecast"].loc[0, "model"] == "calendar_profile"


def test_decision_report_source_validation_and_generation(
    tmp_path, monkeypatch
) -> None:
    """Reject malformed report inputs and render clear output for valid inputs."""
    output_dir = tmp_path / "valid_outputs"
    write_decision_inputs(output_dir)
    monkeypatch.setattr(decision, "PROFILE_DIR", output_dir)
    monkeypatch.setattr(decision, "REPORT_PATH", output_dir / "decision_report.html")
    monkeypatch.setattr(
        decision, "SOURCE_NOTES_PATH", output_dir / "decision_report_source_notes.md"
    )

    decision.build_report()
    assert "A&amp;B Station" in (output_dir / "decision_report.html").read_text(
        encoding="utf-8"
    )
    assert "calendar_profile" in (
        output_dir / "decision_report_source_notes.md"
    ).read_text(encoding="utf-8")
    assert decision.safe_improvement(0, 5) == 0.0
    assert (
        decision.required_model_row(
            pd.DataFrame({"model": ["previous_day"], "mae": [1]}), "previous_day"
        )["mae"]
        == 1
    )

    bad_json_dir = tmp_path / "bad_json"
    write_decision_inputs(bad_json_dir)
    (bad_json_dir / "profile_summary.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(decision, "PROFILE_DIR", bad_json_dir)
    with pytest.raises(ValueError, match="JSON object"):
        decision.load_inputs()

    bad_summary_dir = tmp_path / "bad_summary"
    write_decision_inputs(
        bad_summary_dir,
        profile={
            "rush_vs_off_hour_ratio": 2.2,
            "weekend_vs_weekday_ratio": 0.8,
            "summary": [],
        },
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", bad_summary_dir)
    with pytest.raises(ValueError, match="summary"):
        decision.load_inputs()

    missing_key_dir = tmp_path / "missing_key"
    write_decision_inputs(
        missing_key_dir,
        profile={
            "rush_vs_off_hour_ratio": 2.2,
            "summary": {
                "total_rides": 100_000,
                "hourly_points": 744,
                "average_daily_rides": 3200,
                "average_hourly_rides": 135,
                "peak_hour_rides": 600,
                "peak_hour": "2024-01-04 08:00:00",
            },
        },
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", missing_key_dir)
    with pytest.raises(KeyError, match="missing required keys"):
        decision.load_inputs()

    missing_model_dir = tmp_path / "missing_model"
    write_decision_inputs(
        missing_model_dir,
        forecast=pd.DataFrame(
            {
                "model": ["calendar_profile", "previous_day"],
                "mae": [80.0, 100.0],
                "rmse": [95.0, 115.0],
                "mape": [0.10, 0.12],
                "mean_actual": [150.0, 150.0],
            }
        ),
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", missing_model_dir)
    with pytest.raises(ValueError, match="previous_week"):
        decision.build_report()

    duplicate_model_dir = tmp_path / "duplicate_model"
    write_decision_inputs(
        duplicate_model_dir,
        forecast=pd.DataFrame(
            {
                "model": [
                    "calendar_profile",
                    "previous_day",
                    "previous_day",
                    "previous_week",
                ],
                "mae": [80.0, 100.0, 101.0, 120.0],
                "rmse": [95.0, 115.0, 116.0, 130.0],
                "mape": [0.10, 0.12, 0.13, 0.14],
                "mean_actual": [150.0, 150.0, 150.0, 150.0],
            }
        ),
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", duplicate_model_dir)
    with pytest.raises(ValueError, match="duplicate"):
        decision.build_report()

    missing_column_dir = tmp_path / "missing_column"
    write_decision_inputs(missing_column_dir)
    pd.DataFrame({"model": ["previous_day"], "mae": [1.0]}).to_csv(
        missing_column_dir / "forecast_backtest_metrics.csv", index=False
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", missing_column_dir)
    with pytest.raises(KeyError, match="missing required columns"):
        decision.load_inputs()

    invalid_numeric_dir = tmp_path / "invalid_numeric"
    write_decision_inputs(
        invalid_numeric_dir,
        forecast=pd.DataFrame(
            {
                "model": ["calendar_profile", "previous_day", "previous_week"],
                "mae": [80.0, np.inf, 120.0],
                "rmse": [95.0, 115.0, 130.0],
                "mape": [0.10, 0.12, 0.14],
                "mean_actual": [150.0, 150.0, 150.0],
            }
        ),
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", invalid_numeric_dir)
    with pytest.raises(ValueError, match="nonnumeric or missing"):
        decision.build_report()

    empty_anomaly_dir = tmp_path / "empty_anomaly"
    write_decision_inputs(
        empty_anomaly_dir,
        anomalies=pd.DataFrame(columns=["hour", "absolute_gap"]),
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", empty_anomaly_dir)
    with pytest.raises(ValueError, match="anomaly_hours.csv has no rows"):
        decision.build_report()

    bad_profile_dir = tmp_path / "bad_profile"
    write_decision_inputs(
        bad_profile_dir,
        profile={
            "rush_vs_off_hour_ratio": "bad",
            "weekend_vs_weekday_ratio": 0.8,
            "summary": {
                "total_rides": 100_000,
                "hourly_points": 744,
                "average_daily_rides": 3200,
                "average_hourly_rides": 135,
                "peak_hour_rides": 600,
                "peak_hour": "2024-01-04 08:00:00",
            },
        },
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", bad_profile_dir)
    with pytest.raises(ValueError, match="rush_vs_off_hour_ratio"):
        decision.build_report()

    infinite_profile_dir = tmp_path / "infinite_profile"
    write_decision_inputs(
        infinite_profile_dir,
        profile={
            "rush_vs_off_hour_ratio": np.inf,
            "weekend_vs_weekday_ratio": 0.8,
            "summary": {
                "total_rides": 100_000,
                "hourly_points": 744,
                "average_daily_rides": 3200,
                "average_hourly_rides": 135,
                "peak_hour_rides": 600,
                "peak_hour": "2024-01-04 08:00:00",
            },
        },
    )
    monkeypatch.setattr(decision, "PROFILE_DIR", infinite_profile_dir)
    with pytest.raises(ValueError, match="rush_vs_off_hour_ratio"):
        decision.build_report()


def test_showcase_formatters_loading_and_validation(tmp_path, monkeypatch) -> None:
    """Validate showcase formatters and CSV profile loading guardrails."""
    assert showcase.label_model("previous_day") == "Previous day"
    assert showcase.label_model("custom_model") == "Custom Model"
    assert showcase.fmt_number(np.nan) == "n/a"
    assert showcase.fmt_number(1234) == "1,234"
    assert showcase.fmt_number(1234.567, digits=1) == "1,234.6"
    assert showcase.fmt_percent(np.nan) == "n/a"
    assert showcase.fmt_percent(0.125) == "12.5%"

    csv_path = tmp_path / "hourly_profile.csv"
    hourly_showcase_frame(days=1).sample(frac=1, random_state=1).to_csv(
        csv_path, index=False
    )
    monkeypatch.setattr(showcase, "HOURLY_CSV", csv_path)
    loaded = showcase.load_hourly_profile()
    assert loaded["hour"].is_monotonic_increasing
    assert loaded["rides"].dtype.kind == "f"

    missing_path = tmp_path / "missing.csv"
    monkeypatch.setattr(showcase, "HOURLY_CSV", missing_path)
    with pytest.raises(FileNotFoundError):
        showcase.load_hourly_profile()

    bad_path = tmp_path / "bad.csv"
    bad_path.write_text("hour,date,rides\n2024-01-01,2024-01-01,1\n", encoding="utf-8")
    monkeypatch.setattr(showcase, "HOURLY_CSV", bad_path)
    with pytest.raises(ValueError, match="missing required columns"):
        showcase.load_hourly_profile()


def test_showcase_metrics_forecasts_and_tables() -> None:
    """Exercise showcase diagnostics, rolling baselines, and HTML table helpers."""
    hourly = hourly_showcase_frame()
    index = showcase.validate_hourly_index(
        pd.concat([hourly, hourly.iloc[[0]]], ignore_index=True)
    )
    assert index["duplicate_hours"] == 1
    assert index["missing_hours"] == 0

    assert math.isnan(showcase.safe_mape(pd.Series([0]), pd.Series([1])))
    score_empty = showcase.score_forecast(pd.Series([np.nan]), pd.Series([1]))
    assert score_empty["n"] == 0 and math.isnan(score_empty["mae"])
    score = showcase.score_forecast(pd.Series([10.0, 20.0]), pd.Series([8.0, 22.0]))
    assert score["mae"] == 2

    assert showcase.classify_lag(1) == "short lag"
    assert showcase.classify_lag(168) == "weekly seasonal lag"
    assert showcase.classify_lag(24) == "daily seasonal lag"
    assert showcase.classify_lag(5) == "other lag"

    autocorr = showcase.build_autocorrelation_profile(hourly, max_lag=24)
    assert len(autocorr) == 24
    lag_corr = showcase.build_lag_feature_correlations(hourly)
    assert {"feature", "concept", "correlation_with_rides"} <= set(lag_corr.columns)

    hourly_by_hour = hourly.set_index("hour")["rides"]
    previous = showcase.forecast_from_previous(
        hourly_by_hour, hourly.loc[24:25, "hour"], 24
    )
    assert previous.iloc[0] == hourly.loc[0, "rides"]
    train = hourly.iloc[:24]
    test = hourly.iloc[24:26].copy()
    assert len(showcase.forecast_from_hour_profile(train, test)) == 2
    fallback_test = pd.DataFrame({"day_of_week": [6], "hour_of_day": [23]}, index=[99])
    assert showcase.forecast_from_calendar_profile(train, fallback_test).notna().all()

    rolling_metrics, origin_metrics, scored = showcase.build_rolling_backtests(hourly)
    assert not rolling_metrics.empty
    assert not origin_metrics.empty
    assert not scored.empty

    short_metrics, short_origin, short_scored = showcase.build_rolling_backtests(
        hourly.head(48)
    )
    assert short_metrics.empty and short_origin.empty and short_scored.empty
    incomplete = hourly[
        ~(
            (hourly["hour"] == pd.Timestamp("2024-01-15 05:00"))
            | (hourly["hour"] > pd.Timestamp("2024-01-16"))
        )
    ]
    skip_metrics, skip_origin, skip_scored = showcase.build_rolling_backtests(
        incomplete
    )
    assert skip_metrics.empty and skip_origin.empty and skip_scored.empty

    components = showcase.build_decomposition_components(hourly)
    coverage = showcase.build_showcase_coverage()
    metrics = showcase.build_showcase_metrics(
        hourly,
        showcase.validate_hourly_index(hourly),
        showcase.build_autocorrelation_profile(hourly),
        lag_corr,
        rolling_metrics,
        components,
    )
    assert not coverage.empty
    assert "best_rolling_backtest_model" in set(metrics["measure"])

    table = showcase.table_html(
        pd.DataFrame({"a": [1], "b": [0.25]}),
        columns=["a", "b"],
        rename={"a": "A", "b": "B"},
        formatters={"b": lambda value: f"{value:.0%}"},
    )
    assert "25%" in table
    labeled = showcase.rolling_metrics_for_report(
        pd.DataFrame({"model": ["previous_day"], "mae": [1.0]})
    )
    assert labeled.loc[0, "model"] == "Previous day"
