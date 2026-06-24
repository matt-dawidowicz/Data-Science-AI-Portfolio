"""Build a multi-month Citi Bike time-series proof layer.

The original showcase is intentionally scoped to January 2024. This script is
the stronger proof path: it streams multiple public Citi Bike monthly archives,
aggregates trip starts to an hourly panel, and evaluates leakage-aware rolling
forecast origins across a longer calendar span.

Raw archives are cached under ``work/data/multi_month`` and ignored by Git. The
portable portfolio artifacts are written under ``outputs/``.
"""

from __future__ import annotations

import argparse
import calendar
import html
import json
import math
import shutil
import textwrap
import urllib.request
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
DATA_DIR = WORK_DIR / "data" / "multi_month"
OUT_DIR = ROOT / "outputs"
CHART_DIR = OUT_DIR / "charts"

DEFAULT_START_MONTH = "2024-01"
DEFAULT_END_MONTH = "2024-12"
BASE_ARCHIVE_URL = "https://s3.amazonaws.com/tripdata"
USER_AGENT = "codex-citibike-multi-month-proof/1.0"

REGRESSION_FEATURES = [
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "is_weekend_int",
    "is_federal_holiday_int",
    "days_since_start",
    "lag_24h",
    "lag_168h",
    "rolling_24h_prior_day",
    "rolling_168h_prior_day",
]

MODEL_LABELS = {
    "previous_day": "Previous day",
    "previous_week": "Previous week",
    "hour_of_day_profile": "Hour-of-day profile",
    "weekday_hour_profile": "Weekday/hour profile",
    "seasonal_lag_blend": "Seasonal lag blend",
    "calendar_lag_ridge": "Calendar + lag ridge",
}

FONT_FAMILY = ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
    "blue": "#5477C4",
    "blue_light": "#A3BEFA",
    "gold": "#FFE15B",
    "gold_dark": "#736422",
    "orange": "#F0986E",
    "orange_dark": "#804126",
    "olive": "#71B436",
    "olive_dark": "#386411",
    "pink": "#F390CA",
    "pink_dark": "#8A3A6F",
}


@dataclass(frozen=True)
class MonthArchive:
    """Resolved Citi Bike archive metadata for one YYYY-MM source month."""

    month: str
    url: str
    path: Path


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the multi-month proof layer."""
    parser = argparse.ArgumentParser(
        description="Build the multi-month Citi Bike proof layer."
    )
    parser.add_argument(
        "--start-month", default=DEFAULT_START_MONTH, help="Inclusive YYYY-MM month."
    )
    parser.add_argument(
        "--end-month", default=DEFAULT_END_MONTH, help="Inclusive YYYY-MM month."
    )
    parser.add_argument(
        "--origin-step-days",
        type=int,
        default=7,
        help="Days between rolling forecast origins. Weekly is the default portfolio setting.",
    )
    parser.add_argument(
        "--horizon-hours",
        type=int,
        default=24,
        help="Forecast horizon scored from each origin.",
    )
    parser.add_argument(
        "--min-train-days",
        type=int,
        default=60,
        help="Minimum history before the first rolling forecast origin.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use only already-cached archives and fail if a month is missing.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the multi-month proof pipeline and write portfolio artifacts."""
    args = parse_args()
    prepare_dirs()

    months = month_range(args.start_month, args.end_month)
    archives = [archive_for_month(month) for month in months]
    for archive in archives:
        ensure_archive(archive, skip_download=args.skip_download)

    monthly_summaries, hourly = build_multi_month_hourly_panel(archives)
    hourly = add_forecast_features(hourly)
    metrics, origin_metrics, scored = build_rolling_backtests(
        hourly,
        horizon_hours=args.horizon_hours,
        min_train_days=args.min_train_days,
        origin_step_days=args.origin_step_days,
    )
    summary = build_summary(
        hourly=hourly,
        monthly_summaries=monthly_summaries,
        metrics=metrics,
        origin_metrics=origin_metrics,
        scored=scored,
        args=args,
    )

    chart_paths = build_charts(
        hourly, monthly_summaries, metrics, origin_metrics, scored
    )
    write_outputs(
        hourly, monthly_summaries, metrics, origin_metrics, scored, summary, chart_paths
    )


def prepare_dirs() -> None:
    """Create local work, output, and chart directories."""
    for path in [WORK_DIR, DATA_DIR, OUT_DIR, CHART_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def month_range(start_month: str, end_month: str) -> list[str]:
    """Return inclusive YYYY-MM month labels between two bounds."""
    start = pd.Period(start_month, freq="M")
    end = pd.Period(end_month, freq="M")
    if end < start:
        raise ValueError("end-month must be greater than or equal to start-month")
    return [str(month) for month in pd.period_range(start, end, freq="M")]


def archive_for_month(month: str) -> MonthArchive:
    """Build the expected Citi Bike archive URL and cache path for a month."""
    compact = month.replace("-", "")
    filename = f"{compact}-citibike-tripdata.zip"
    return MonthArchive(
        month=month,
        url=f"{BASE_ARCHIVE_URL}/{filename}",
        path=DATA_DIR / filename,
    )


def ensure_archive(archive: MonthArchive, *, skip_download: bool) -> None:
    """Ensure one monthly Citi Bike archive exists and is a valid ZIP."""
    if archive.path.exists() and archive.path.stat().st_size > 1_000_000:
        if zipfile.is_zipfile(archive.path):
            return
        archive.path.unlink()

    if skip_download:
        raise FileNotFoundError(
            f"Missing cached archive for {archive.month}: {archive.path}"
        )

    print(f"Downloading {archive.url}")
    request = urllib.request.Request(archive.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        with archive.path.open("wb") as handle:
            shutil.copyfileobj(response, handle)

    if not zipfile.is_zipfile(archive.path):
        raise RuntimeError(f"Downloaded file is not a valid zip: {archive.path}")


def get_csv_names(zip_path: Path) -> list[str]:
    """Return sorted CSV member names from a Citi Bike ZIP archive."""
    with zipfile.ZipFile(zip_path) as zf:
        csv_names = sorted(
            name for name in zf.namelist() if name.lower().endswith(".csv")
        )
    if not csv_names:
        raise RuntimeError(f"No CSV files found inside {zip_path}")
    return csv_names


def get_csv_header(zip_path: Path, csv_name: str) -> list[str]:
    """Return the header row for one CSV member inside an archive."""
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(csv_name) as raw:
            return raw.readline().decode("utf-8-sig").strip().split(",")


def build_multi_month_hourly_panel(
    archives: list[MonthArchive],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stream archives into monthly summaries and a continuous hourly panel."""
    hourly_counter: Counter[pd.Timestamp] = Counter()
    station_counter: Counter[str] = Counter()
    monthly_rows: list[dict[str, object]] = []

    for archive in archives:
        rows_total = 0
        rows_valid = 0
        first_started: pd.Timestamp | None = None
        last_started: pd.Timestamp | None = None

        for csv_name in get_csv_names(archive.path):
            header = set(get_csv_header(archive.path, csv_name))
            required = {"started_at", "ended_at"}
            missing = required.difference(header)
            if missing:
                raise RuntimeError(
                    f"{archive.path.name}:{csv_name} is missing columns: {sorted(missing)}"
                )

            optional = {"start_station_id", "start_station_name"}
            usecols = sorted(required.union(optional.intersection(header)))
            with zipfile.ZipFile(archive.path) as zf:
                with zf.open(csv_name) as raw:
                    reader = pd.read_csv(
                        raw,
                        usecols=usecols,
                        dtype={column: "string" for column in usecols},
                        chunksize=350_000,
                    )
                    for chunk in reader:
                        rows_total += len(chunk)
                        chunk["started_at"] = pd.to_datetime(
                            chunk["started_at"], errors="coerce"
                        )
                        chunk["ended_at"] = pd.to_datetime(
                            chunk["ended_at"], errors="coerce"
                        )
                        duration = (
                            chunk["ended_at"] - chunk["started_at"]
                        ).dt.total_seconds() / 60
                        valid = (
                            chunk["started_at"].notna()
                            & chunk["ended_at"].notna()
                            & duration.between(1, 240)
                        )
                        chunk = chunk.loc[valid].copy()
                        rows_valid += len(chunk)
                        if chunk.empty:
                            continue

                        current_first = chunk["started_at"].min()
                        current_last = chunk["started_at"].max()
                        first_started = (
                            current_first
                            if first_started is None
                            else min(first_started, current_first)
                        )
                        last_started = (
                            current_last
                            if last_started is None
                            else max(last_started, current_last)
                        )

                        hourly_counter.update(
                            chunk["started_at"].dt.floor("h").value_counts().to_dict()
                        )
                        if (
                            "start_station_id" in chunk.columns
                            and "start_station_name" in chunk.columns
                        ):
                            station_key = (
                                chunk["start_station_id"].fillna("unknown").astype(str)
                                + " | "
                                + chunk["start_station_name"]
                                .fillna("unknown")
                                .astype(str)
                            )
                            station_counter.update(station_key)

        monthly_rows.append(
            {
                "month": archive.month,
                "source_url": archive.url,
                "archive_file": archive.path.name,
                "archive_size_mb": round(archive.path.stat().st_size / 1_000_000, 2),
                "rows_total": rows_total,
                "rows_valid": rows_valid,
                "valid_rate": rows_valid / rows_total if rows_total else np.nan,
                "first_started_at": str(first_started),
                "last_started_at": str(last_started),
            }
        )

    if not hourly_counter:
        raise RuntimeError("No valid trips found after filtering.")

    first_month = pd.Period(archives[0].month, freq="M")
    last_month = pd.Period(archives[-1].month, freq="M")
    first_hour = first_month.to_timestamp()
    last_hour = last_month.to_timestamp(how="end").floor("h")
    full_hours = pd.date_range(first_hour, last_hour, freq="h")

    hourly = pd.DataFrame({"hour": full_hours})
    hourly["rides"] = hourly["hour"].map(
        lambda value: int(hourly_counter.get(value, 0))
    )
    hourly = add_calendar_columns(hourly)

    monthly_summaries = pd.DataFrame(monthly_rows)
    monthly_summaries["valid_rides_in_fixed_window"] = (
        hourly.assign(month=hourly["hour"].dt.to_period("M").astype(str))
        .groupby("month")["rides"]
        .sum()
        .reindex(monthly_summaries["month"])
        .to_numpy()
    )
    if station_counter:
        top_station_rows = pd.DataFrame(
            station_counter.most_common(25), columns=["station_id_name", "rides"]
        )
        top_station_rows.to_csv(OUT_DIR / "multi_month_top_stations.csv", index=False)

    return monthly_summaries, hourly


def add_calendar_columns(hourly: pd.DataFrame) -> pd.DataFrame:
    """Add reusable calendar fields to an hourly demand panel."""
    frame = hourly.copy()
    frame["date"] = frame["hour"].dt.date.astype(str)
    frame["month"] = frame["hour"].dt.to_period("M").astype(str)
    frame["day_name"] = frame["hour"].dt.day_name()
    frame["day_of_week"] = frame["hour"].dt.dayofweek
    frame["hour_of_day"] = frame["hour"].dt.hour
    frame["day_of_year"] = frame["hour"].dt.dayofyear
    frame["is_weekend"] = frame["day_of_week"].isin([5, 6])
    holidays = federal_holiday_dates(
        frame["hour"].dt.year.min(), frame["hour"].dt.year.max()
    )
    frame["is_federal_holiday"] = frame["date"].isin(holidays)
    return frame


def federal_holiday_dates(start_year: int, end_year: int) -> set[str]:
    """Return U.S. federal holiday dates for an inclusive year span."""
    dates: set[str] = set()
    for year in range(int(start_year), int(end_year) + 1):
        fixed = [(1, 1), (6, 19), (7, 4), (11, 11), (12, 25)]
        dates.update(f"{year}-{month:02d}-{day:02d}" for month, day in fixed)
        dates.add(str(nth_weekday(year, 1, calendar.MONDAY, 3).date()))
        dates.add(str(nth_weekday(year, 2, calendar.MONDAY, 3).date()))
        dates.add(str(last_weekday(year, 5, calendar.MONDAY).date()))
        dates.add(str(nth_weekday(year, 9, calendar.MONDAY, 1).date()))
        dates.add(str(nth_weekday(year, 10, calendar.MONDAY, 2).date()))
        dates.add(str(nth_weekday(year, 11, calendar.THURSDAY, 4).date()))
    return dates


def nth_weekday(year: int, month: int, weekday: int, n: int) -> pd.Timestamp:
    """Return the nth weekday date within a month."""
    first = pd.Timestamp(year=year, month=month, day=1)
    offset = (weekday - first.weekday()) % 7
    return first + pd.Timedelta(days=offset + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> pd.Timestamp:
    """Return the final weekday date within a month."""
    last_day = calendar.monthrange(year, month)[1]
    last = pd.Timestamp(year=year, month=month, day=last_day)
    offset = (last.weekday() - weekday) % 7
    return last - pd.Timedelta(days=offset)


def add_forecast_features(hourly: pd.DataFrame) -> pd.DataFrame:
    """Add lag, rolling, and cyclical features for model backtesting."""
    frame = hourly.copy().sort_values("hour").reset_index(drop=True)
    rides = frame["rides"].astype(float)
    frame["hour_sin"] = np.sin(2 * np.pi * frame["hour_of_day"] / 24)
    frame["hour_cos"] = np.cos(2 * np.pi * frame["hour_of_day"] / 24)
    frame["dow_sin"] = np.sin(2 * np.pi * frame["day_of_week"] / 7)
    frame["dow_cos"] = np.cos(2 * np.pi * frame["day_of_week"] / 7)
    frame["month_number"] = frame["hour"].dt.month
    frame["month_sin"] = np.sin(2 * np.pi * frame["month_number"] / 12)
    frame["month_cos"] = np.cos(2 * np.pi * frame["month_number"] / 12)
    frame["is_weekend_int"] = frame["is_weekend"].astype(int)
    frame["is_federal_holiday_int"] = frame["is_federal_holiday"].astype(int)
    frame["days_since_start"] = (
        frame["hour"] - frame["hour"].min()
    ).dt.total_seconds() / 86_400
    frame["lag_24h"] = rides.shift(24)
    frame["lag_168h"] = rides.shift(168)

    # For a 24-hour forecast origin, these rolling features are anchored one
    # day back. They do not peek into the forecast horizon.
    frame["rolling_24h_prior_day"] = rides.shift(24).rolling(24, min_periods=12).mean()
    frame["rolling_168h_prior_day"] = (
        rides.shift(24).rolling(168, min_periods=72).mean()
    )
    return frame


def build_rolling_backtests(
    hourly: pd.DataFrame,
    *,
    horizon_hours: int,
    min_train_days: int,
    origin_step_days: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Score forecast models across leakage-aware rolling origins."""
    hourly_by_hour = hourly.set_index("hour")["rides"].astype(float)
    first_origin = (
        hourly["hour"].min() + pd.Timedelta(days=min_train_days)
    ).normalize()
    last_origin = hourly["hour"].max() - pd.Timedelta(hours=horizon_hours - 1)
    origins = pd.date_range(
        first_origin, last_origin.normalize(), freq=f"{origin_step_days}D"
    )

    scored_rows: list[dict[str, object]] = []
    origin_rows: list[dict[str, object]] = []

    for origin in origins:
        train = hourly[hourly["hour"] < origin].copy()
        test = hourly[
            (hourly["hour"] >= origin)
            & (hourly["hour"] < origin + pd.Timedelta(hours=horizon_hours))
        ].copy()
        if len(train) < min_train_days * 24 or len(test) != horizon_hours:
            continue

        forecasts = {
            "previous_day": forecast_from_previous(hourly_by_hour, test["hour"], 24),
            "previous_week": forecast_from_previous(hourly_by_hour, test["hour"], 168),
            "hour_of_day_profile": forecast_from_hour_profile(train, test),
            "weekday_hour_profile": forecast_from_calendar_profile(train, test),
        }
        forecasts["seasonal_lag_blend"] = (
            0.65 * forecasts["weekday_hour_profile"] + 0.35 * forecasts["previous_week"]
        )
        forecasts["calendar_lag_ridge"] = forecast_from_calendar_lag_ridge(train, test)

        for model, forecast in forecasts.items():
            scored = pd.DataFrame(
                {
                    "origin": origin,
                    "hour": test["hour"].to_numpy(),
                    "model": model,
                    "actual": test["rides"].astype(float).to_numpy(),
                    "forecast": forecast.to_numpy(dtype=float),
                }
            ).dropna()
            if scored.empty:
                continue

            scored["error"] = scored["actual"] - scored["forecast"]
            scored["abs_error"] = scored["error"].abs()
            scored_rows.extend(scored.to_dict("records"))
            origin_rows.append(
                {"origin": origin, "model": model, **score_forecast(scored)}
            )

    scored_df = pd.DataFrame(scored_rows)
    origin_metrics = pd.DataFrame(origin_rows)
    aggregate_metrics = aggregate_model_metrics(scored_df, origin_metrics)
    return aggregate_metrics, origin_metrics, scored_df


def forecast_from_previous(
    hourly_by_hour: pd.Series, hours: pd.Series, lag: int
) -> pd.Series:
    """Forecast demand by copying demand from a prior fixed-hour lag."""
    return pd.Series(
        [hourly_by_hour.get(hour - pd.Timedelta(hours=lag), np.nan) for hour in hours],
        index=hours.index,
        dtype=float,
    )


def forecast_from_hour_profile(train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    """Forecast demand from the training-set average by hour of day."""
    profile = train.groupby("hour_of_day")["rides"].mean()
    global_mean = float(train["rides"].mean())
    return test["hour_of_day"].map(profile).fillna(global_mean).astype(float)


def forecast_from_calendar_profile(
    train: pd.DataFrame, test: pd.DataFrame
) -> pd.Series:
    """Forecast demand from the training-set weekday and hour profile."""
    calendar_profile = train.groupby(["day_of_week", "hour_of_day"])["rides"].mean()
    hour_profile = train.groupby("hour_of_day")["rides"].mean()
    global_mean = float(train["rides"].mean())
    forecasts = []
    for row in test.itertuples(index=False):
        forecasts.append(
            float(
                calendar_profile.get(
                    (row.day_of_week, row.hour_of_day),
                    hour_profile.get(row.hour_of_day, global_mean),
                )
            )
        )
    return pd.Series(forecasts, index=test.index, dtype=float)


def forecast_from_calendar_lag_ridge(
    train: pd.DataFrame, test: pd.DataFrame
) -> pd.Series:
    """Forecast demand with a ridge model using calendar and lag features."""
    usable_train = train.dropna(subset=REGRESSION_FEATURES + ["rides"]).copy()
    usable_test = test.dropna(subset=REGRESSION_FEATURES).copy()
    predictions = pd.Series(np.nan, index=test.index, dtype=float)
    if len(usable_train) < max(240, len(REGRESSION_FEATURES) * 20) or usable_test.empty:
        return predictions

    x_train = usable_train[REGRESSION_FEATURES].to_numpy(dtype=float)
    y_train = usable_train["rides"].to_numpy(dtype=float)
    means = x_train.mean(axis=0)
    stds = x_train.std(axis=0)
    stds[stds == 0] = 1.0
    x_scaled = (x_train - means) / stds
    x_design = np.column_stack([np.ones(len(x_scaled)), x_scaled])

    alpha = 25.0
    penalty = np.eye(x_design.shape[1])
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(
        x_design.T @ x_design + alpha * penalty, x_design.T @ y_train
    )

    x_test = usable_test[REGRESSION_FEATURES].to_numpy(dtype=float)
    x_test_scaled = (x_test - means) / stds
    test_design = np.column_stack([np.ones(len(x_test_scaled)), x_test_scaled])
    predictions.loc[usable_test.index] = np.maximum(0, test_design @ beta)
    return predictions


def score_forecast(scored: pd.DataFrame) -> dict[str, float]:
    """Calculate accuracy metrics for one scored forecast slice."""
    if scored.empty:
        return {"n": 0, "mae": np.nan, "rmse": np.nan, "mape": np.nan}
    error = scored["actual"] - scored["forecast"]
    denom = scored["actual"].replace(0, np.nan)
    return {
        "n": int(len(scored)),
        "mae": float(error.abs().mean()),
        "rmse": float(math.sqrt((error**2).mean())),
        "mape": float((error.abs() / denom).dropna().mean()),
    }


def aggregate_model_metrics(
    scored: pd.DataFrame, origin_metrics: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate scored rows into model-level validation metrics."""
    if scored.empty:
        return pd.DataFrame()

    winners = pd.DataFrame()
    if not origin_metrics.empty:
        winner_idx = origin_metrics.groupby("origin")["mae"].idxmin()
        winners = (
            origin_metrics.loc[winner_idx].groupby("model").size().rename("origin_wins")
        )

    rows = []
    for model, part in scored.groupby("model"):
        metrics = score_forecast(part)
        origin_part = origin_metrics[origin_metrics["model"] == model]
        rows.append(
            {
                "model": model,
                "model_label": label_model(model),
                "origins": int(part["origin"].nunique()),
                "holdout_hours": int(len(part)),
                "mean_actual": float(part["actual"].mean()),
                "median_origin_mae": float(origin_part["mae"].median())
                if not origin_part.empty
                else np.nan,
                "origin_wins": int(winners.get(model, 0)) if not winners.empty else 0,
                **metrics,
            }
        )

    metrics_df = pd.DataFrame(rows).sort_values(["mae", "rmse"]).reset_index(drop=True)
    total_origins = metrics_df["origins"].max()
    metrics_df["origin_win_rate"] = (
        metrics_df["origin_wins"] / total_origins if total_origins else 0.0
    )
    return metrics_df


def label_model(model: object) -> str:
    """Return a readable label for a forecast model identifier."""
    return MODEL_LABELS.get(str(model), str(model).replace("_", " ").title())


def build_summary(
    *,
    hourly: pd.DataFrame,
    monthly_summaries: pd.DataFrame,
    metrics: pd.DataFrame,
    origin_metrics: pd.DataFrame,
    scored: pd.DataFrame,
    args: argparse.Namespace,
) -> dict[str, object]:
    """Build the JSON summary for the multi-month proof layer."""
    daily = hourly.groupby("date", as_index=False)["rides"].sum()
    best = metrics.iloc[0].to_dict() if not metrics.empty else {}
    summary = {
        "title": "Citi Bike Multi-Month Forecast Proof",
        "start_month": args.start_month,
        "end_month": args.end_month,
        "months": int(len(monthly_summaries)),
        "first_hour": str(hourly["hour"].min()),
        "last_hour": str(hourly["hour"].max()),
        "hourly_observations": int(len(hourly)),
        "missing_hours": int(
            len(
                pd.date_range(
                    hourly["hour"].min(), hourly["hour"].max(), freq="h"
                ).difference(hourly["hour"])
            )
        ),
        "total_fixed_window_rides": int(hourly["rides"].sum()),
        "average_daily_rides": float(daily["rides"].mean()),
        "average_hourly_rides": float(hourly["rides"].mean()),
        "peak_hour": str(hourly.loc[hourly["rides"].idxmax(), "hour"]),
        "peak_hour_rides": int(hourly["rides"].max()),
        "rows_total": int(monthly_summaries["rows_total"].sum()),
        "rows_valid": int(monthly_summaries["rows_valid"].sum()),
        "valid_rate": float(
            monthly_summaries["rows_valid"].sum()
            / monthly_summaries["rows_total"].sum()
        ),
        "origin_step_days": int(args.origin_step_days),
        "horizon_hours": int(args.horizon_hours),
        "min_train_days": int(args.min_train_days),
        "rolling_origins": int(origin_metrics["origin"].nunique())
        if not origin_metrics.empty
        else 0,
        "scored_holdout_rows": int(len(scored)),
        "best_model": best,
    }
    return make_json_safe(summary)


def make_json_safe(value: object) -> object:
    """Convert NumPy, pandas, and timestamp values into JSON-safe values."""
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat(sep=" ")
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if pd.isna(value) if not isinstance(value, (str, bytes)) else False:
        return None
    return value


def use_chart_theme() -> None:
    """Apply the shared visual theme for Matplotlib charts."""
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "savefig.facecolor": TOKENS["surface"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "axes.spines.top": False,
            "axes.spines.right": False,
        },
    )


def add_chart_header(
    fig: plt.Figure,
    ax: plt.Axes,
    title: str,
    subtitle: str,
    *,
    title_width: int = 82,
    subtitle_width: int = 116,
) -> None:
    """Add a consistent title and subtitle treatment to a chart."""
    title = textwrap.fill(title, width=title_width, break_long_words=False)
    subtitle = textwrap.fill(subtitle, width=subtitle_width, break_long_words=False)
    fig.subplots_adjust(top=0.84)
    left = ax.get_position().x0
    fig.text(
        left,
        0.985,
        title,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="semibold",
        color=TOKENS["ink"],
    )
    fig.text(
        left,
        0.93,
        subtitle,
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
    )
    sns.despine(ax=ax)


def format_date_axis(ax: plt.Axes) -> None:
    """Format a chart x-axis for compact dates."""
    locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def save_chart(fig: plt.Figure, filename: str) -> Path:
    """Save a chart image to the project chart directory."""
    path = CHART_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def build_charts(
    hourly: pd.DataFrame,
    monthly_summaries: pd.DataFrame,
    metrics: pd.DataFrame,
    origin_metrics: pd.DataFrame,
    scored: pd.DataFrame,
) -> list[Path]:
    """Render the multi-month proof charts."""
    use_chart_theme()
    chart_paths = [
        plot_multi_month_daily_demand(hourly),
        plot_monthly_volume(monthly_summaries),
        plot_model_mae(metrics),
        plot_origin_mae(origin_metrics, metrics),
    ]
    if not scored.empty and not metrics.empty:
        chart_paths.append(plot_forecast_example(scored, metrics))
    return chart_paths


def plot_multi_month_daily_demand(hourly: pd.DataFrame) -> Path:
    """Plot daily demand with short and medium rolling averages."""
    daily = hourly.groupby("date", as_index=False)["rides"].sum()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["rolling_7d"] = daily["rides"].rolling(7, min_periods=3).mean()
    daily["rolling_28d"] = daily["rides"].rolling(28, min_periods=10).mean()

    fig, ax = plt.subplots(figsize=(11, 5.2))
    sns.lineplot(
        data=daily,
        x="date",
        y="rides",
        ax=ax,
        color="#C5CAD3",
        linewidth=0.7,
        label="Daily rides",
    )
    sns.lineplot(
        data=daily,
        x="date",
        y="rolling_7d",
        ax=ax,
        color=TOKENS["blue_light"],
        linewidth=1.0,
        label="7-day average",
    )
    sns.lineplot(
        data=daily,
        x="date",
        y="rolling_28d",
        ax=ax,
        color=TOKENS["blue"],
        linewidth=1.2,
        label="28-day average",
    )
    format_date_axis(ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1000:.0f}k"))
    ax.set_xlabel("")
    ax.set_ylabel("Trip starts")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=3)
    add_chart_header(
        fig,
        ax,
        "Longer coverage shows level shifts that one month cannot prove",
        "Daily Citi Bike starts with 7-day and 28-day smoothing. The raw line stays visible for volatility.",
    )
    return save_chart(fig, "multi_month_daily_demand.png")


def plot_monthly_volume(monthly_summaries: pd.DataFrame) -> Path:
    """Plot fixed-window trip volume by source month."""
    plot_df = monthly_summaries.copy()
    plot_df["month_start"] = pd.to_datetime(plot_df["month"] + "-01")
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    sns.barplot(
        data=plot_df,
        x="month_start",
        y="valid_rides_in_fixed_window",
        ax=ax,
        color=TOKENS["olive"],
        edgecolor=TOKENS["olive_dark"],
        linewidth=1.0,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Trip starts")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x / 1_000_000:.1f}M")
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    add_chart_header(
        fig,
        ax,
        "Monthly volume creates a stronger seasonality proof",
        "Fixed-window valid trip starts by month. This is the basic coverage check before modeling.",
    )
    return save_chart(fig, "multi_month_monthly_volume.png")


def plot_model_mae(metrics: pd.DataFrame) -> Path:
    """Plot aggregate model MAE from rolling validation."""
    plot_df = metrics.sort_values("mae", ascending=True).copy()
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    sns.barplot(
        data=plot_df,
        x="mae",
        y="model_label",
        ax=ax,
        color=TOKENS["gold"],
        edgecolor=TOKENS["gold_dark"],
        linewidth=1.0,
    )
    for patch, value in zip(ax.patches, plot_df["mae"]):
        ax.text(
            patch.get_width() + max(plot_df["mae"].max() * 0.01, 20),
            patch.get_y() + patch.get_height() / 2,
            f"{value:,.0f}",
            va="center",
            fontsize=8,
            color=TOKENS["ink"],
        )
    ax.set_xlabel("Mean absolute error, rides per hour")
    ax.set_ylabel("")
    ax.set_xlim(0, plot_df["mae"].max() * 1.18)
    add_chart_header(
        fig,
        ax,
        "Rolling validation compares transparent baselines with one stronger model",
        "Lower MAE is better. Every origin trains only on hours before the forecast start.",
    )
    return save_chart(fig, "multi_month_model_mae.png")


def plot_origin_mae(origin_metrics: pd.DataFrame, metrics: pd.DataFrame) -> Path:
    """Plot validation error over rolling forecast origins."""
    models = metrics.sort_values("mae")["model"].head(4).tolist()
    plot_df = origin_metrics[origin_metrics["model"].isin(models)].copy()
    plot_df["model_label"] = plot_df["model"].map(label_model)
    fig, ax = plt.subplots(figsize=(11, 5.2))
    sns.lineplot(
        data=plot_df,
        x="origin",
        y="mae",
        hue="model_label",
        ax=ax,
        linewidth=1.0,
    )
    format_date_axis(ax)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("")
    ax.set_ylabel("MAE")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False, ncol=2)
    add_chart_header(
        fig,
        ax,
        "Origin-level error shows whether performance is stable or fragile",
        "Each point is a 24-hour forecast origin. A good portfolio model should survive bad weeks.",
    )
    return save_chart(fig, "multi_month_origin_mae.png")


def plot_forecast_example(scored: pd.DataFrame, metrics: pd.DataFrame) -> Path:
    """Plot one concrete holdout forecast trace for the best model."""
    best_model = str(metrics.iloc[0]["model"])
    origin = scored["origin"].max()
    plot_df = scored[
        (scored["origin"] == origin) & (scored["model"] == best_model)
    ].copy()

    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    sns.lineplot(
        data=plot_df,
        x="hour",
        y="actual",
        ax=ax,
        color=TOKENS["blue"],
        linewidth=1.3,
        label="Actual",
    )
    sns.lineplot(
        data=plot_df,
        x="hour",
        y="forecast",
        ax=ax,
        color=TOKENS["orange"],
        linewidth=1.3,
        linestyle="--",
        label=label_model(best_model),
    )
    format_date_axis(ax)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("")
    ax.set_ylabel("Trip starts")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=2)
    add_chart_header(
        fig,
        ax,
        "The final scored origin gives reviewers a concrete forecast trace",
        f"Best aggregate model on the final 24-hour scored origin: {label_model(best_model)}.",
    )
    return save_chart(fig, "multi_month_forecast_example.png")


def write_outputs(
    hourly: pd.DataFrame,
    monthly_summaries: pd.DataFrame,
    metrics: pd.DataFrame,
    origin_metrics: pd.DataFrame,
    scored: pd.DataFrame,
    summary: dict[str, object],
    chart_paths: list[Path],
) -> None:
    """Write CSV, JSON, chart, and HTML outputs for the proof layer."""
    daily = hourly.groupby("date", as_index=False)["rides"].sum()
    hourly.to_csv(OUT_DIR / "multi_month_hourly_profile.csv", index=False)
    daily.to_csv(OUT_DIR / "multi_month_daily_profile.csv", index=False)
    monthly_summaries.to_csv(OUT_DIR / "multi_month_source_inventory.csv", index=False)
    metrics.to_csv(OUT_DIR / "multi_month_model_metrics.csv", index=False)
    origin_metrics.to_csv(OUT_DIR / "multi_month_origin_metrics.csv", index=False)
    scored.to_csv(OUT_DIR / "multi_month_backtest_scored.csv", index=False)
    with (OUT_DIR / "multi_month_proof_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2)
    report = strip_trailing_whitespace(
        render_html_report(
            summary, monthly_summaries, metrics, origin_metrics, chart_paths
        )
    )
    (OUT_DIR / "multi_month_proof.html").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Report written to {OUT_DIR / 'multi_month_proof.html'}")


def strip_trailing_whitespace(text: str) -> str:
    """Remove trailing whitespace while preserving a final newline."""
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def render_html_report(
    summary: dict[str, object],
    monthly_summaries: pd.DataFrame,
    metrics: pd.DataFrame,
    origin_metrics: pd.DataFrame,
    chart_paths: list[Path],
) -> str:
    """Render the multi-month proof layer as standalone HTML."""
    best = summary.get("best_model", {})
    if not isinstance(best, dict):
        best = {}
    chart_blocks = "\n".join(
        f"""
        <figure>
          <img src="charts/{html.escape(path.name)}" alt="{html.escape(path.stem.replace("_", " "))}">
          <figcaption>{html.escape(chart_caption(path.name))}</figcaption>
        </figure>
        """
        for path in chart_paths
    )
    metric_table = table_html(
        metrics,
        columns=[
            "model_label",
            "origins",
            "holdout_hours",
            "mean_actual",
            "mae",
            "rmse",
            "mape",
            "origin_win_rate",
        ],
        rename={
            "model_label": "Model",
            "origins": "Origins",
            "holdout_hours": "Holdout Hours",
            "mean_actual": "Mean Actual",
            "mae": "MAE",
            "rmse": "RMSE",
            "mape": "MAPE",
            "origin_win_rate": "Origin Win Rate",
        },
        formatters={
            "Mean Actual": fmt_number,
            "MAE": fmt_number,
            "RMSE": fmt_number,
            "MAPE": fmt_percent,
            "Origin Win Rate": fmt_percent,
        },
    )
    monthly_table = table_html(
        monthly_summaries,
        columns=[
            "month",
            "rows_valid",
            "valid_rides_in_fixed_window",
            "valid_rate",
            "archive_size_mb",
        ],
        rename={
            "month": "Month",
            "rows_valid": "Valid Rows",
            "valid_rides_in_fixed_window": "Fixed-Window Rides",
            "valid_rate": "Valid Rate",
            "archive_size_mb": "Archive MB",
        },
        formatters={
            "Valid Rows": fmt_number,
            "Fixed-Window Rides": fmt_number,
            "Valid Rate": fmt_percent,
            "Archive MB": lambda value: fmt_number(value, digits=1),
        },
    )
    best_label = html.escape(
        str(best.get("model_label", label_model(best.get("model", ""))))
    )
    best_mae = fmt_number(best.get("mae", np.nan))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(summary["title"]))}</title>
  <style>
    :root {{
      --surface: #FCFCFD;
      --panel: #FFFFFF;
      --ink: #1F2430;
      --muted: #6F768A;
      --grid: #E6E8F0;
      --accent: #5477C4;
      --warm: #F0986E;
    }}
    body {{
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font-family: Aptos, Inter, "Segoe UI", Arial, sans-serif;
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 40px 20px 72px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(32px, 5vw, 50px);
      line-height: 1.03;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 36px 0 12px;
      font-size: 24px;
      line-height: 1.2;
    }}
    p, li {{
      color: var(--muted);
      font-size: 16px;
      line-height: 1.62;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0 32px;
    }}
    .kpi {{
      background: var(--panel);
      border: 1px solid var(--grid);
      border-radius: 8px;
      padding: 16px;
    }}
    .kpi strong {{
      display: block;
      font-size: 24px;
      line-height: 1.1;
      margin-bottom: 8px;
    }}
    .kpi span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .callout {{
      border-left: 4px solid var(--warm);
      background: #FFEDDE;
      border-radius: 6px;
      padding: 14px 16px;
    }}
    figure {{
      margin: 24px 0;
    }}
    figure img {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid var(--grid);
      border-radius: 8px;
      background: var(--panel);
    }}
    figcaption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--grid);
      border-radius: 8px;
      overflow: hidden;
      font-size: 14px;
      margin: 14px 0 24px;
    }}
    .data-table th, .data-table td {{
      border-bottom: 1px solid var(--grid);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    .data-table th {{
      background: #F4F5F7;
      color: var(--ink);
    }}
    .data-table tr:last-child td {{
      border-bottom: 0;
    }}
    @media (max-width: 760px) {{
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpis {{ grid-template-columns: 1fr; }}
      .data-table {{ font-size: 12px; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{html.escape(str(summary["title"]))}</h1>
    <p>
      This report upgrades the original January-only showcase into a longer
      rolling-validation proof. It keeps the target simple and auditable:
      valid Citi Bike trip starts per hour.
    </p>
  </header>

  <section class="kpis">
    <div class="kpi"><strong>{fmt_number(summary["months"])}</strong><span>months profiled</span></div>
    <div class="kpi"><strong>{fmt_number(summary["hourly_observations"])}</strong><span>hourly observations</span></div>
    <div class="kpi"><strong>{fmt_number(summary["rolling_origins"])}</strong><span>rolling origins</span></div>
    <div class="kpi"><strong>{best_mae}</strong><span>best MAE, rides/hour</span></div>
  </section>

  <section>
    <h2>What changed from the first showcase</h2>
    <p class="callout">
      The project now has a stronger proof layer: multiple months of public
      archives, a complete hourly panel, weekly rolling 24-hour forecast
      origins, transparent baselines, and one regularized calendar-lag model.
      The best aggregate model in this run is <strong>{best_label}</strong>.
    </p>
  </section>

  <section>
    <h2>Coverage and validation charts</h2>
    {chart_blocks}
  </section>

  <section>
    <h2>Rolling model comparison</h2>
    {metric_table}
  </section>

  <section>
    <h2>Monthly source inventory</h2>
    {monthly_table}
  </section>

  <section>
    <h2>Honest limits</h2>
    <ul>
      <li>Trip starts are modeled, not live bike inventory or station capacity.</li>
      <li>Station names and IDs still need a dedicated station-metadata audit before station-level forecasts.</li>
      <li>The ridge model is intentionally simple. It proves feature discipline, not best-possible forecast accuracy.</li>
      <li>External events and weather are not yet used in the multi-month model.</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def table_html(
    df: pd.DataFrame,
    *,
    columns: list[str],
    rename: dict[str, str],
    formatters: dict[str, object],
) -> str:
    """Render selected DataFrame columns as a styled HTML table."""
    display = df.loc[:, columns].rename(columns=rename)
    return display.to_html(
        index=False,
        escape=True,
        border=0,
        classes="data-table",
        formatters=formatters,
    )


def fmt_number(value: object, digits: int = 0) -> str:
    """Format a number for compact report tables."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value):,.{digits}f}"


def fmt_percent(value: object, digits: int = 1) -> str:
    """Format a decimal ratio as a percentage string."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def chart_caption(filename: str) -> str:
    """Return the report caption for a generated chart filename."""
    captions = {
        "multi_month_daily_demand.png": "Daily demand over the longer panel, with smoothing to show level shifts.",
        "multi_month_monthly_volume.png": "Monthly fixed-window valid trip starts, used as the coverage sanity check.",
        "multi_month_model_mae.png": "Aggregate rolling-origin MAE by model. Lower is better.",
        "multi_month_origin_mae.png": "Origin-level MAE for the leading models, showing stability over time.",
        "multi_month_forecast_example.png": "Final scored 24-hour origin for the best aggregate model.",
    }
    return captions.get(
        filename, filename.replace("_", " ").replace(".png", "").title()
    )


if __name__ == "__main__":
    main()
