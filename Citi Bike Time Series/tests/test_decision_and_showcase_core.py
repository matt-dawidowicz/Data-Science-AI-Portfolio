"""Tests for decision-report and time-series showcase helpers."""

from __future__ import annotations

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


def test_decision_formatting_tables_and_input_loading(tmp_path, monkeypatch) -> None:
    """Check decision-report formatters, HTML escaping, and input loading."""
    assert decision.fmt_int(1234.5) == "1,234"
    assert decision.fmt_k(1_500_000) == "1.50M"
    assert decision.fmt_k(12_300) == "12.3k"
    assert decision.fmt_k(42) == "42"
    assert decision.fmt_pct(0.1234, 2) == "12.34%"
    assert decision.fmt_num(1234.567, 2) == "1,234.57"

    table = decision.table_html(
        pd.DataFrame({"name": ["A&B"], "value": ["<tag>"]}),
        ["name", "value"],
        ["Name", "Value"],
    )
    assert "&amp;" in table and "&lt;tag&gt;" in table

    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    (output_dir / "profile_summary.json").write_text(
        '{"summary": {"valid": 1}}', encoding="utf-8"
    )
    for filename in [
        "forecast_backtest_metrics.csv",
        "top_stations.csv",
        "anomaly_hours.csv",
        "member_mix.csv",
        "bike_mix.csv",
    ]:
        (output_dir / filename).write_text("col\n1\n", encoding="utf-8")
    monkeypatch.setattr(decision, "PROFILE_DIR", output_dir)
    loaded = decision.load_inputs()
    assert loaded["summary"] == {"valid": 1}
    assert loaded["forecast"].loc[0, "col"] == 1


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
