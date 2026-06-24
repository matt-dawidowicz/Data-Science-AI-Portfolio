"""Tests for the full-year Citi Bike proof helpers."""

from __future__ import annotations

import argparse
import math

import numpy as np
import pandas as pd
import pytest

import citibike_multi_month_proof as multi


def hourly_frame(days: int = 80) -> pd.DataFrame:
    """Build a deterministic hourly demand panel for rolling tests."""
    hours = pd.date_range("2024-01-01", periods=days * 24, freq="h")
    frame = pd.DataFrame(
        {
            "hour": hours,
            "rides": (
                500
                + hours.hour.to_numpy() * 9
                + hours.dayofweek.to_numpy() * 13
                + np.arange(len(hours)) % 17
            ).astype(float),
        }
    )
    return multi.add_forecast_features(multi.add_calendar_columns(frame))


def test_month_archives_dates_and_calendar_features() -> None:
    """Validate month utilities and holiday-aware calendar fields."""
    assert multi.month_range("2024-01", "2024-03") == [
        "2024-01",
        "2024-02",
        "2024-03",
    ]
    with pytest.raises(ValueError):
        multi.month_range("2024-03", "2024-01")

    archive = multi.archive_for_month("2024-02")
    assert archive.month == "2024-02"
    assert archive.url.endswith("202402-citibike-tripdata.zip")
    assert archive.path.name == "202402-citibike-tripdata.zip"

    assert multi.nth_weekday(2024, 1, multi.calendar.MONDAY, 3).day == 15
    assert multi.last_weekday(2024, 5, multi.calendar.MONDAY).day == 27
    holidays = multi.federal_holiday_dates(2024, 2024)
    assert "2024-01-01" in holidays and "2024-11-28" in holidays

    hourly = multi.add_calendar_columns(
        pd.DataFrame({"hour": pd.to_datetime(["2024-01-01 01:00", "2024-01-02 01:00"])})
    )
    assert bool(hourly.loc[0, "is_federal_holiday"]) is True
    assert bool(hourly.loc[1, "is_federal_holiday"]) is False


def test_forecast_features_models_scoring_and_aggregation() -> None:
    """Exercise leakage-aware features, forecasts, scoring, and aggregation."""
    hourly = hourly_frame()
    assert {"lag_24h", "lag_168h", "rolling_24h_prior_day"} <= set(hourly.columns)
    assert hourly.loc[24, "lag_24h"] == hourly.loc[0, "rides"]

    hourly_by_hour = hourly.set_index("hour")["rides"]
    previous = multi.forecast_from_previous(
        hourly_by_hour, hourly.loc[24:25, "hour"], 24
    )
    assert previous.iloc[0] == hourly.loc[0, "rides"]
    assert (
        multi.forecast_from_hour_profile(hourly.iloc[:24], hourly.iloc[24:26])
        .notna()
        .all()
    )

    fallback_test = pd.DataFrame({"day_of_week": [6], "hour_of_day": [23]}, index=[99])
    assert (
        multi.forecast_from_calendar_profile(hourly.iloc[:24], fallback_test)
        .notna()
        .all()
    )

    insufficient = multi.forecast_from_calendar_lag_ridge(
        hourly.head(30), hourly.iloc[30:32]
    )
    assert insufficient.isna().all()
    ridge = multi.forecast_from_calendar_lag_ridge(
        hourly.iloc[:600], hourly.iloc[600:624]
    )
    assert ridge.notna().all()

    empty_score = multi.score_forecast(pd.DataFrame())
    assert empty_score["n"] == 0 and math.isnan(empty_score["mae"])
    scored = pd.DataFrame(
        {
            "origin": [pd.Timestamp("2024-03-01")] * 4,
            "model": ["a", "a", "b", "b"],
            "actual": [10.0, 20.0, 10.0, 20.0],
            "forecast": [11.0, 18.0, 10.0, 20.0],
        }
    )
    scored["error"] = scored["actual"] - scored["forecast"]
    scored["abs_error"] = scored["error"].abs()
    origin_metrics = pd.DataFrame(
        {
            "origin": [pd.Timestamp("2024-03-01"), pd.Timestamp("2024-03-01")],
            "model": ["a", "b"],
            "mae": [1.5, 1.0],
        }
    )
    metrics = multi.aggregate_model_metrics(scored, origin_metrics)
    assert metrics.iloc[0]["model"] == "b"
    assert metrics.loc[metrics["model"] == "b", "origin_wins"].iloc[0] == 1
    assert multi.aggregate_model_metrics(pd.DataFrame(), pd.DataFrame()).empty

    rolling_metrics, rolling_origin, rolling_scored = multi.build_rolling_backtests(
        hourly,
        horizon_hours=24,
        min_train_days=60,
        origin_step_days=7,
    )
    assert not rolling_metrics.empty
    assert not rolling_origin.empty
    assert not rolling_scored.empty

    edge_hourly = hourly_frame(days=3)
    edge_hourly = edge_hourly[edge_hourly["hour"] != pd.Timestamp("2024-01-02 05:00")]
    edge_metrics, edge_origin, edge_scored = multi.build_rolling_backtests(
        edge_hourly,
        horizon_hours=24,
        min_train_days=1,
        origin_step_days=1,
    )
    assert not edge_metrics.empty
    assert not edge_origin.empty
    assert not edge_scored.empty


def test_summary_json_formatting_and_tables() -> None:
    """Check summary generation and report utility helpers."""
    hourly = hourly_frame(days=4)
    monthly = pd.DataFrame(
        {
            "month": ["2024-01"],
            "rows_total": [100],
            "rows_valid": [95],
            "valid_rides_in_fixed_window": [int(hourly["rides"].sum())],
            "valid_rate": [0.95],
            "archive_size_mb": [1.25],
        }
    )
    metrics = pd.DataFrame(
        {
            "model": ["calendar_lag_ridge"],
            "model_label": ["Calendar + lag ridge"],
            "mae": [10.0],
        }
    )
    origin = pd.DataFrame({"origin": [pd.Timestamp("2024-03-01")]})
    summary = multi.build_summary(
        hourly=hourly,
        monthly_summaries=monthly,
        metrics=metrics,
        origin_metrics=origin,
        scored=pd.DataFrame({"x": [1, 2]}),
        args=argparse.Namespace(
            start_month="2024-01",
            end_month="2024-01",
            origin_step_days=7,
            horizon_hours=24,
            min_train_days=60,
        ),
    )
    assert summary["best_model"]["model"] == "calendar_lag_ridge"
    assert summary["valid_rate"] == 0.95

    empty_summary = multi.build_summary(
        hourly=hourly,
        monthly_summaries=monthly,
        metrics=pd.DataFrame(),
        origin_metrics=pd.DataFrame(),
        scored=pd.DataFrame(),
        args=argparse.Namespace(
            start_month="2024-01",
            end_month="2024-01",
            origin_step_days=7,
            horizon_hours=24,
            min_train_days=60,
        ),
    )
    assert empty_summary["best_model"] == {}
    assert empty_summary["rolling_origins"] == 0

    assert multi.label_model("unknown_model") == "Unknown Model"
    assert multi.strip_trailing_whitespace("a  \n") == "a\n"
    assert multi.fmt_number(np.nan) == "n/a"
    assert multi.fmt_number(1234.5, digits=1) == "1,234.5"
    assert multi.fmt_percent(np.nan) == "n/a"
    assert multi.fmt_percent(0.125) == "12.5%"
    assert "Daily demand" in multi.chart_caption("multi_month_daily_demand.png")
    assert multi.chart_caption("custom_chart.png") == "Custom Chart"

    converted = multi.make_json_safe(
        {
            "list": [np.int64(2)],
            "tuple": (np.int64(1),),
            "stamp": pd.Timestamp("2024-01-01"),
            "float": np.float64(2.5),
            "bool": np.bool_(False),
            "missing": np.nan,
        }
    )
    assert converted == {
        "list": [2],
        "tuple": [1],
        "stamp": "2024-01-01 00:00:00",
        "float": 2.5,
        "bool": False,
        "missing": None,
    }

    html = multi.table_html(
        monthly,
        columns=["month", "rows_valid", "valid_rate"],
        rename={"month": "Month", "rows_valid": "Rows", "valid_rate": "Valid Rate"},
        formatters={"Valid Rate": multi.fmt_percent},
    )
    assert "95.0%" in html
