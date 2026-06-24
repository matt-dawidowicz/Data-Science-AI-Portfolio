"""Tests for the January profile helper functions."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

import citibike_time_series_profile as profile


def hourly_profile_frame(days: int = 31) -> pd.DataFrame:
    """Build a deterministic January-like hourly panel."""
    hours = pd.date_range("2024-01-01", periods=days * 24, freq="h")
    frame = pd.DataFrame(
        {
            "hour": hours,
            "rides": 100
            + hours.hour * 5
            + hours.dayofweek * 10
            + np.arange(len(hours)) % 7,
            "date": hours.date.astype(str),
            "day_of_week": hours.dayofweek,
            "day_name": hours.day_name(),
            "hour_of_day": hours.hour,
            "is_weekend": hours.dayofweek >= 5,
            "temperature_c": np.linspace(-2, 8, len(hours)),
            "precipitation_mm": np.where(hours.hour == 8, 0.2, 0.0),
            "snowfall_cm": 0.0,
            "wind_speed_kmh": np.linspace(4, 12, len(hours)),
        }
    )
    return frame


def test_share_frame_seasonality_anomalies_and_formatters() -> None:
    """Validate small table helpers and seasonal diagnostics."""
    share = profile.counter_to_share_frame(
        profile.Counter({"member": 8, "casual": 2}), "rider_type", 10
    )
    assert share.to_dict("records")[0] == {
        "rider_type": "member",
        "rides": 8,
        "share": 0.8,
    }
    empty_share = profile.counter_to_share_frame(profile.Counter({"x": 1}), "kind", 0)
    assert empty_share.loc[0, "share"] == 0

    hourly = hourly_profile_frame()
    seasonality = profile.build_seasonality(hourly)
    assert {"day_of_week", "day_name", "hour_of_day", "rides"} <= set(
        seasonality.columns
    )

    anomaly_source = hourly.copy()
    anomaly_source.loc[5, "rides"] = 10_000
    anomalies = profile.detect_anomalies(anomaly_source)
    assert len(anomalies) == 20
    assert {"expected_profile_rides", "absolute_gap", "robust_z"} <= set(
        anomalies.columns
    )

    rows = profile.table_rows(
        [{"name": "A&B", "share": 0.125, "rides": 1234, "score": 1.25}],
        ["name", "share", "rides", "score"],
    )
    assert "&amp;" in rows and "12.5%" in rows and "1,234" in rows
    assert "calendar_profile" in profile.forecast_rows_html(
        [{"model": "calendar_profile", "mae": 1, "rmse": 2, "mape": 0.25}]
    )
    assert profile.format_int(1234.4) == "1,234"


def test_profile_forecast_scoring_and_payload() -> None:
    """Exercise scoring, holdout forecasting, and JSON-safe payload assembly."""
    hourly = hourly_profile_frame()
    metrics, scored, best_model, interval = profile.run_forecast_backtest(hourly)
    assert set(metrics["model"]) == {
        "previous_day",
        "previous_week",
        "calendar_profile",
    }
    assert not scored.empty
    assert best_model in set(metrics["model"])
    assert interval[0] <= interval[1]

    score = profile.score_model(
        "demo", pd.Series([10.0, 20.0]), pd.Series([12.0, 18.0])
    )
    assert score["n"] == 2
    assert score["mae"] == 2
    assert score["rmse"] == 2
    assert math.isclose(score["mape"], 0.15)

    payload = profile.build_report_payload(
        summary={"rows_valid": np.int64(3)},
        hourly=hourly,
        top_stations=pd.DataFrame({"station": ["A"], "rides": [10]}),
        member_mix=pd.DataFrame(
            {"rider_type": ["member"], "rides": [8], "share": [0.8]}
        ),
        bike_mix=pd.DataFrame({"bike_type": ["classic"], "rides": [8], "share": [0.8]}),
        anomalies=pd.DataFrame({"hour": [hourly.loc[0, "hour"]], "rides": [1]}),
        forecast_results=metrics,
        best_model=best_model,
        weather_loaded=True,
    )
    assert payload["weather_loaded"] is True
    assert payload["summary"]["rows_valid"] == 3
    assert payload["weather_correlations"]["temperature_c"] is not None

    converted = profile.make_json_safe(
        {
            "stamp": pd.Timestamp("2024-01-01 01:00"),
            "number": np.float64(1.5),
            "flag": np.bool_(True),
            "missing": np.nan,
            "items": (np.int64(2),),
        }
    )
    assert converted == {
        "stamp": "2024-01-01 01:00:00",
        "number": 1.5,
        "flag": True,
        "missing": None,
        "items": [2],
    }
