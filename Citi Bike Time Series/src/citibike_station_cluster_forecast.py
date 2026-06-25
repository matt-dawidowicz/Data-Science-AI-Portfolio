"""Forecast Citi Bike demand for stable station clusters.

This is the operational upgrade after the full-year proof layer. It streams the
same public Citi Bike monthly archives, builds stable station groups from
station IDs plus observed station metadata, joins full-year weather and public
calendar/event features, and evaluates whether a weather/event ridge model
beats transparent baselines in rolling validation.

Raw archives and weather JSON are cached under ``work/data`` and ignored by
Git. Portfolio-ready artifacts are written under ``outputs/``.
"""

from __future__ import annotations

import argparse
import calendar
import html
import json
import math
import shutil
import textwrap
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
DATA_DIR = WORK_DIR / "data" / "multi_month"
WEATHER_DIR = WORK_DIR / "data" / "weather"
OUT_DIR = ROOT / "outputs"
CHART_DIR = OUT_DIR / "charts"

DEFAULT_START_MONTH = "2024-01"
DEFAULT_END_MONTH = "2024-12"
BASE_ARCHIVE_URL = "https://s3.amazonaws.com/tripdata"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
USER_AGENT = "codex-citibike-station-cluster-forecast/1.0"
NYC_LATITUDE = 40.7128
NYC_LONGITUDE = -74.0060

BASE_REGRESSION_FEATURES = [
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

WEATHER_EVENT_FEATURES = BASE_REGRESSION_FEATURES + [
    "temperature_2m",
    "precipitation",
    "snowfall",
    "wind_speed_10m",
    "weather_code",
    "is_precip_int",
    "is_snow_int",
    "temperature_below_comfort",
    "temperature_above_comfort",
    "event_intensity",
    "is_major_event_int",
    "is_event_peak_hour_int",
    "is_holiday_eve_int",
    "is_holiday_window_int",
]

MODEL_LABELS = {
    "previous_day": "Previous day",
    "previous_week": "Previous week",
    "calendar_lag_ridge": "Calendar + lag ridge",
    "weather_event_ridge": "Weather/event ridge",
}
MODEL_LIFT_REQUIRED_MODELS = [
    "previous_week",
    "calendar_lag_ridge",
    "weather_event_ridge",
]

FONT_FAMILY = ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]
MONO_FONT_FAMILY = ["SF Mono", "Menlo", "Consolas", "DejaVu Sans Mono", "monospace"]

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}

NEUTRAL_MARKS = {
    "open": TOKENS["panel"],
    "xlight": "#F4F5F7",
    "light": "#E2E5EA",
    "base": "#C5CAD3",
    "mid": "#7A828F",
    "dark": "#464C55",
}

COLOR_FAMILIES = {
    "blue": {
        "open": TOKENS["panel"],
        "xlight": "#EAF1FE",
        "light": "#CEDFFE",
        "base": "#A3BEFA",
        "mid": "#5477C4",
        "dark": "#2E4780",
    },
    "gold": {
        "open": TOKENS["panel"],
        "xlight": "#FFF4C2",
        "light": "#FFEA8F",
        "base": "#FFE15B",
        "mid": "#B8A037",
        "dark": "#736422",
    },
    "orange": {
        "open": TOKENS["panel"],
        "xlight": "#FFEDDE",
        "light": "#FFBDA1",
        "base": "#F0986E",
        "mid": "#CC6F47",
        "dark": "#804126",
    },
    "olive": {
        "open": TOKENS["panel"],
        "xlight": "#D8ECBD",
        "light": "#BEEB96",
        "base": "#A3D576",
        "mid": "#71B436",
        "dark": "#386411",
    },
    "pink": {
        "open": TOKENS["panel"],
        "xlight": "#FCDAD6",
        "light": "#F5BACC",
        "base": "#F390CA",
        "mid": "#BD569B",
        "dark": "#8A3A6F",
    },
}

CLUSTER_FAMILIES = ["blue", "gold", "olive", "pink", "orange", "blue"]


@dataclass(frozen=True)
class MonthArchive:
    """Resolved Citi Bike archive metadata for one YYYY-MM source month."""

    month: str
    url: str
    path: Path


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the station-cluster forecast build."""
    parser = argparse.ArgumentParser(
        description="Build station-cluster Citi Bike forecasts with weather/event features."
    )
    parser.add_argument(
        "--start-month", default=DEFAULT_START_MONTH, help="Inclusive YYYY-MM month."
    )
    parser.add_argument(
        "--end-month", default=DEFAULT_END_MONTH, help="Inclusive YYYY-MM month."
    )
    parser.add_argument(
        "--top-stations",
        type=int,
        default=120,
        help="Number of highest-volume station IDs to cluster.",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=6,
        help="Number of deterministic geographic station clusters.",
    )
    parser.add_argument(
        "--origin-step-days",
        type=int,
        default=7,
        help="Days between rolling forecast origins.",
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
        help="Use only already-cached Citi Bike archives and fail if a month is missing.",
    )
    parser.add_argument(
        "--skip-weather-download",
        action="store_true",
        help="Use only already-cached Open-Meteo weather JSON and fail if it is missing.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full station-cluster forecasting artifact pipeline."""
    args = parse_args()
    prepare_dirs()

    months = month_range(args.start_month, args.end_month)
    archives = [archive_for_month(month) for month in months]
    for archive in archives:
        ensure_archive(archive, skip_download=args.skip_download)

    monthly_summaries, system_hourly, station_metadata = build_station_metadata(
        archives
    )
    assignments, cluster_summary = build_station_clusters(
        station_metadata,
        total_system_rides=int(system_hourly["rides"].sum()),
        top_stations=args.top_stations,
        cluster_count=args.clusters,
    )
    cluster_hourly = build_cluster_hourly_panel(archives, assignments, system_hourly)
    weather = load_weather_panel(
        start_date=months[0] + "-01",
        end_date=str(pd.Period(months[-1], freq="M").to_timestamp(how="end").date()),
        skip_download=args.skip_weather_download,
    )
    event_calendar = build_event_calendar(
        start_year=pd.Period(months[0], freq="M").year,
        end_year=pd.Period(months[-1], freq="M").year,
    )
    panel = build_model_panel(cluster_hourly, cluster_summary, weather, event_calendar)
    metrics, origin_metrics, scored = build_rolling_backtests(
        panel,
        horizon_hours=args.horizon_hours,
        min_train_days=args.min_train_days,
        origin_step_days=args.origin_step_days,
    )
    if metrics.empty:
        raise RuntimeError(
            "No rolling validation metrics were produced. Increase the date range "
            "or reduce --min-train-days/--horizon-hours before building the report."
        )
    lift = build_model_lift(metrics)
    priorities = build_capacity_priorities(cluster_summary, metrics, lift)
    summary = build_summary(
        args=args,
        monthly_summaries=monthly_summaries,
        system_hourly=system_hourly,
        station_metadata=station_metadata,
        cluster_summary=cluster_summary,
        panel=panel,
        weather=weather,
        event_calendar=event_calendar,
        metrics=metrics,
        lift=lift,
        priorities=priorities,
    )
    chart_paths = build_charts(
        assignments, cluster_summary, metrics, lift, scored, priorities
    )
    write_outputs(
        monthly_summaries=monthly_summaries,
        station_metadata=station_metadata,
        assignments=assignments,
        cluster_summary=cluster_summary,
        panel=panel,
        weather=weather,
        event_calendar=event_calendar,
        metrics=metrics,
        origin_metrics=origin_metrics,
        scored=scored,
        lift=lift,
        priorities=priorities,
        summary=summary,
        chart_paths=chart_paths,
    )


def prepare_dirs() -> None:
    """Create local cache and output directories used by the pipeline."""
    for path in [WORK_DIR, DATA_DIR, WEATHER_DIR, OUT_DIR, CHART_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def month_range(start_month: str, end_month: str) -> list[str]:
    """Return inclusive YYYY-MM month labels between two calendar bounds."""
    start = pd.Period(start_month, freq="M")
    end = pd.Period(end_month, freq="M")
    if end < start:
        raise ValueError("end-month must be greater than or equal to start-month")
    return [str(month) for month in pd.period_range(start, end, freq="M")]


def archive_for_month(month: str) -> MonthArchive:
    """Resolve the public Citi Bike archive URL and local cache path."""
    compact = month.replace("-", "")
    filename = f"{compact}-citibike-tripdata.zip"
    return MonthArchive(
        month=month,
        url=f"{BASE_ARCHIVE_URL}/{filename}",
        path=DATA_DIR / filename,
    )


def ensure_archive(archive: MonthArchive, *, skip_download: bool) -> None:
    """Ensure one Citi Bike monthly archive exists and is a valid ZIP file."""
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
    """List CSV members inside a Citi Bike monthly archive."""
    with zipfile.ZipFile(zip_path) as zf:
        csv_names = sorted(
            name for name in zf.namelist() if name.lower().endswith(".csv")
        )
    if not csv_names:
        raise RuntimeError(f"No CSV files found inside {zip_path}")
    return csv_names


def get_csv_header(zip_path: Path, csv_name: str) -> list[str]:
    """Read the header row for one archived CSV member."""
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(csv_name) as raw:
            return raw.readline().decode("utf-8-sig").strip().split(",")


def build_station_metadata(
    archives: list[MonthArchive],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stream archives into monthly quality, system hourly, and station tables."""
    hourly_counter: Counter[pd.Timestamp] = Counter()
    station_counter: Counter[str] = Counter()
    station_name_counter: dict[str, Counter[str]] = defaultdict(Counter)
    station_lat_sum: Counter[str] = Counter()
    station_lng_sum: Counter[str] = Counter()
    station_coord_count: Counter[str] = Counter()
    station_months: dict[str, set[str]] = defaultdict(set)
    station_first: dict[str, pd.Timestamp] = {}
    station_last: dict[str, pd.Timestamp] = {}
    monthly_rows: list[dict[str, object]] = []

    for archive in archives:
        print(f"Scanning station metadata from {archive.path.name}")
        month = pd.Period(archive.month, freq="M")
        window_start = month.to_timestamp()
        window_end = (month + 1).to_timestamp()
        rows_total = 0
        rows_valid = 0
        rows_valid_fixed_window = 0
        rows_with_station_id = 0
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

            optional = {
                "start_station_id",
                "start_station_name",
                "start_lat",
                "start_lng",
            }
            usecols = sorted(required.union(optional.intersection(header)))
            dtype = {column: "string" for column in usecols}
            with zipfile.ZipFile(archive.path) as zf:
                with zf.open(csv_name) as raw:
                    reader = pd.read_csv(
                        raw, usecols=usecols, dtype=dtype, chunksize=400_000
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

                        chunk = chunk[
                            (chunk["started_at"] >= window_start)
                            & (chunk["started_at"] < window_end)
                        ].copy()
                        rows_valid_fixed_window += len(chunk)
                        if chunk.empty:
                            continue

                        hourly_counter.update(
                            chunk["started_at"].dt.floor("h").value_counts().to_dict()
                        )
                        if "start_station_id" not in chunk.columns:
                            continue

                        chunk["station_id"] = normalize_station_id(
                            chunk["start_station_id"]
                        )
                        station_mask = chunk["station_id"].notna()
                        rows_with_station_id += int(station_mask.sum())
                        if not station_mask.any():
                            continue

                        station_part = chunk.loc[station_mask].copy()
                        station_counts = station_part["station_id"].value_counts()
                        station_counter.update(station_counts.to_dict())

                        if "start_station_name" in station_part.columns:
                            station_part["station_name"] = (
                                station_part["start_station_name"]
                                .fillna("unknown")
                                .astype("string")
                                .str.strip()
                                .replace("", "unknown")
                            )
                            name_counts = (
                                station_part.groupby(
                                    ["station_id", "station_name"], dropna=False
                                )
                                .size()
                                .rename("rides")
                                .reset_index()
                            )
                            for row in name_counts.itertuples(index=False):
                                station_name_counter[str(row.station_id)][
                                    str(row.station_name)
                                ] += int(row.rides)

                        if {"start_lat", "start_lng"}.issubset(station_part.columns):
                            station_part["start_lat"] = pd.to_numeric(
                                station_part["start_lat"], errors="coerce"
                            )
                            station_part["start_lng"] = pd.to_numeric(
                                station_part["start_lng"], errors="coerce"
                            )
                            coord_part = station_part[
                                station_part["start_lat"].between(40.0, 41.1)
                                & station_part["start_lng"].between(-74.6, -73.4)
                            ]
                            coord_summary = (
                                coord_part.groupby("station_id")
                                .agg(
                                    lat_sum=("start_lat", "sum"),
                                    lng_sum=("start_lng", "sum"),
                                    coord_rows=("start_lat", "count"),
                                )
                                .reset_index()
                            )
                            for row in coord_summary.itertuples(index=False):
                                station_id = str(row.station_id)
                                station_lat_sum[station_id] += float(row.lat_sum)
                                station_lng_sum[station_id] += float(row.lng_sum)
                                station_coord_count[station_id] += int(row.coord_rows)

                        station_time = (
                            station_part.groupby("station_id")["started_at"]
                            .agg(["min", "max"])
                            .reset_index()
                        )
                        for row in station_time.itertuples(index=False):
                            station_id = str(row.station_id)
                            station_months[station_id].add(archive.month)
                            station_first[station_id] = min(
                                station_first.get(station_id, row.min), row.min
                            )
                            station_last[station_id] = max(
                                station_last.get(station_id, row.max), row.max
                            )

        monthly_rows.append(
            {
                "month": archive.month,
                "source_url": archive.url,
                "archive_file": archive.path.name,
                "archive_size_mb": round(archive.path.stat().st_size / 1_000_000, 2),
                "rows_total": rows_total,
                "rows_valid": rows_valid,
                "rows_valid_fixed_window": rows_valid_fixed_window,
                "rows_with_station_id": rows_with_station_id,
                "valid_rate": rows_valid / rows_total if rows_total else np.nan,
                "station_id_coverage": rows_with_station_id / rows_valid_fixed_window
                if rows_valid_fixed_window
                else np.nan,
                "first_started_at": str(first_started),
                "last_started_at": str(last_started),
            }
        )

    if not hourly_counter:
        raise RuntimeError("No valid trips found after filtering.")
    if not station_counter:
        raise RuntimeError("No station IDs found in the valid trip rows.")

    first_month = pd.Period(archives[0].month, freq="M")
    last_month = pd.Period(archives[-1].month, freq="M")
    full_hours = pd.date_range(
        first_month.to_timestamp(),
        last_month.to_timestamp(how="end").floor("h"),
        freq="h",
    )
    system_hourly = pd.DataFrame({"hour": full_hours})
    system_hourly["rides"] = system_hourly["hour"].map(
        lambda value: int(hourly_counter.get(value, 0))
    )

    rows = []
    for station_id, rides in station_counter.items():
        coord_rows = int(station_coord_count.get(station_id, 0))
        name_counts = station_name_counter.get(station_id, Counter())
        station_name = name_counts.most_common(1)[0][0] if name_counts else "unknown"
        rows.append(
            {
                "station_id": station_id,
                "station_name": station_name,
                "annual_starts": int(rides),
                "months_active": int(len(station_months.get(station_id, set()))),
                "first_started_at": station_first.get(station_id),
                "last_started_at": station_last.get(station_id),
                "latitude": float(station_lat_sum[station_id] / coord_rows)
                if coord_rows
                else np.nan,
                "longitude": float(station_lng_sum[station_id] / coord_rows)
                if coord_rows
                else np.nan,
                "coordinate_rows": coord_rows,
            }
        )

    station_metadata = pd.DataFrame(rows).sort_values("annual_starts", ascending=False)
    system_total = int(system_hourly["rides"].sum())
    station_metadata["share_of_system_starts"] = (
        station_metadata["annual_starts"] / system_total if system_total else np.nan
    )
    station_metadata = station_metadata.reset_index(drop=True)
    monthly_summaries = pd.DataFrame(monthly_rows)
    monthly_summaries["valid_rides_in_fixed_window"] = (
        system_hourly.assign(month=system_hourly["hour"].dt.to_period("M").astype(str))
        .groupby("month")["rides"]
        .sum()
        .reindex(monthly_summaries["month"])
        .to_numpy()
    )
    return monthly_summaries, system_hourly, station_metadata


def normalize_station_id(values: pd.Series) -> pd.Series:
    """Normalize station IDs while preserving them as stable string keys."""
    normalized = values.fillna("").astype("string").str.strip()
    normalized = normalized.str.replace(r"\.0$", "", regex=True)
    normalized = normalized.mask(
        normalized.str.lower().isin({"", "nan", "none", "null", "<na>", "unknown"})
    )
    return normalized


def build_station_clusters(
    station_metadata: pd.DataFrame,
    *,
    total_system_rides: int,
    top_stations: int,
    cluster_count: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assign high-volume stations to deterministic geographic demand clusters."""
    candidates = station_metadata[
        station_metadata["latitude"].notna() & station_metadata["longitude"].notna()
    ].head(top_stations)
    if len(candidates) < 2:
        raise RuntimeError(
            "Not enough station metadata with coordinates to build clusters."
        )

    cluster_count = max(1, min(cluster_count, len(candidates)))
    coordinates = candidates[["latitude", "longitude"]].to_numpy(dtype=float)
    weights = candidates["annual_starts"].to_numpy(dtype=float)
    raw_labels = weighted_kmeans(coordinates, weights, cluster_count)
    assignments = candidates.copy()
    assignments["raw_cluster"] = raw_labels

    cluster_volume = (
        assignments.groupby("raw_cluster")["annual_starts"]
        .sum()
        .sort_values(ascending=False)
    )
    cluster_id_map = {
        raw_cluster: f"cluster_{rank:02d}"
        for rank, raw_cluster in enumerate(cluster_volume.index, start=1)
    }
    assignments["cluster_id"] = assignments["raw_cluster"].map(cluster_id_map)
    top_names = (
        assignments.sort_values(
            ["cluster_id", "annual_starts"], ascending=[True, False]
        )
        .groupby("cluster_id")["station_name"]
        .first()
        .to_dict()
    )
    assignments["cluster_label"] = assignments["cluster_id"].map(
        lambda value: f"{value.replace('_', ' ').title()} - {top_names[value]} area"
    )
    assignments = assignments.drop(columns=["raw_cluster"]).sort_values(
        ["cluster_id", "annual_starts"], ascending=[True, False]
    )

    cluster_summary = (
        assignments.groupby(["cluster_id", "cluster_label"], as_index=False)
        .agg(
            annual_starts=("annual_starts", "sum"),
            station_count=("station_id", "count"),
            center_latitude=("latitude", "mean"),
            center_longitude=("longitude", "mean"),
            top_station=("station_name", "first"),
        )
        .sort_values("annual_starts", ascending=False)
        .reset_index(drop=True)
    )
    cluster_summary["share_of_system_starts"] = (
        cluster_summary["annual_starts"] / total_system_rides
    )
    cluster_summary["rank"] = np.arange(1, len(cluster_summary) + 1)
    cluster_summary["segment_id"] = cluster_summary["cluster_id"]
    cluster_summary["segment_label"] = cluster_summary["cluster_label"]
    cluster_summary["segment_type"] = "station_cluster"
    return assignments, cluster_summary


def weighted_kmeans(
    coordinates: np.ndarray, weights: np.ndarray, cluster_count: int
) -> np.ndarray:
    """Cluster station coordinates with ride-volume weights."""
    scaled = coordinates.copy()
    mean_lat = float(np.average(scaled[:, 0], weights=weights))
    scaled[:, 1] = scaled[:, 1] * math.cos(math.radians(mean_lat))

    centers = [scaled[int(np.argmax(weights))]]
    while len(centers) < cluster_count:
        center_matrix = np.vstack(centers)
        distances = (
            ((scaled[:, None, :] - center_matrix[None, :, :]) ** 2)
            .sum(axis=2)
            .min(axis=1)
        )
        next_idx = int(np.argmax(distances * np.sqrt(weights)))
        centers.append(scaled[next_idx])
    centers_array = np.vstack(centers)

    labels = np.zeros(len(scaled), dtype=int)
    for _ in range(50):
        distances = ((scaled[:, None, :] - centers_array[None, :, :]) ** 2).sum(axis=2)
        new_labels = distances.argmin(axis=1)
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        for idx in range(cluster_count):
            mask = labels == idx
            if mask.any():
                centers_array[idx] = np.average(
                    scaled[mask], axis=0, weights=weights[mask]
                )
    return labels


def build_cluster_hourly_panel(
    archives: list[MonthArchive],
    assignments: pd.DataFrame,
    system_hourly: pd.DataFrame,
) -> pd.DataFrame:
    """Count hourly starts for the system total and each station cluster."""
    station_to_cluster = assignments.set_index("station_id")["cluster_id"].to_dict()
    cluster_to_label = assignments.set_index("cluster_id")["cluster_label"].to_dict()
    cluster_hour_counter: Counter[tuple[str, pd.Timestamp]] = Counter()

    for archive in archives:
        print(f"Counting cluster-hour demand from {archive.path.name}")
        month = pd.Period(archive.month, freq="M")
        window_start = month.to_timestamp()
        window_end = (month + 1).to_timestamp()
        for csv_name in get_csv_names(archive.path):
            header = set(get_csv_header(archive.path, csv_name))
            required = {"started_at", "ended_at", "start_station_id"}
            missing = required.difference(header)
            if missing:
                raise RuntimeError(
                    f"{archive.path.name}:{csv_name} is missing columns: {sorted(missing)}"
                )

            usecols = sorted(required)
            dtype = {column: "string" for column in usecols}
            with zipfile.ZipFile(archive.path) as zf:
                with zf.open(csv_name) as raw:
                    reader = pd.read_csv(
                        raw, usecols=usecols, dtype=dtype, chunksize=500_000
                    )
                    for chunk in reader:
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
                        if chunk.empty:
                            continue

                        chunk = chunk[
                            (chunk["started_at"] >= window_start)
                            & (chunk["started_at"] < window_end)
                        ].copy()
                        if chunk.empty:
                            continue

                        chunk["station_id"] = normalize_station_id(
                            chunk["start_station_id"]
                        )
                        chunk["cluster_id"] = chunk["station_id"].map(
                            station_to_cluster
                        )
                        cluster_part = chunk[chunk["cluster_id"].notna()].copy()
                        if cluster_part.empty:
                            continue

                        cluster_part["hour"] = cluster_part["started_at"].dt.floor("h")
                        grouped = (
                            cluster_part.groupby(["cluster_id", "hour"])
                            .size()
                            .rename("rides")
                            .reset_index()
                        )
                        for row in grouped.itertuples(index=False):
                            cluster_hour_counter[(str(row.cluster_id), row.hour)] += (
                                int(row.rides)
                            )

    full_hours = system_hourly["hour"]
    rows: list[dict[str, object]] = []
    for row in system_hourly.itertuples(index=False):
        rows.append(
            {
                "segment_id": "system_total",
                "segment_label": "System total",
                "segment_type": "system",
                "hour": row.hour,
                "rides": int(row.rides),
            }
        )

    for cluster_id in sorted(assignments["cluster_id"].unique()):
        label = cluster_to_label[cluster_id]
        for hour in full_hours:
            rows.append(
                {
                    "segment_id": cluster_id,
                    "segment_label": label,
                    "segment_type": "station_cluster",
                    "hour": hour,
                    "rides": int(cluster_hour_counter.get((cluster_id, hour), 0)),
                }
            )

    return pd.DataFrame(rows)


def load_weather_panel(
    *, start_date: str, end_date: str, skip_download: bool
) -> pd.DataFrame:
    """Load or download hourly Open-Meteo weather for the model window."""
    cache_path = WEATHER_DIR / f"open_meteo_nyc_{start_date}_{end_date}.json"
    if not cache_path.exists():
        if skip_download:
            raise FileNotFoundError(
                f"Missing cached Open-Meteo weather file: {cache_path}"
            )
        params = {
            "latitude": NYC_LATITUDE,
            "longitude": NYC_LONGITUDE,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "precipitation",
                    "snowfall",
                    "wind_speed_10m",
                    "weather_code",
                ]
            ),
            "timezone": "America/New_York",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        }
        url = OPEN_METEO_ARCHIVE_URL + "?" + urllib.parse.urlencode(params)
        print(f"Downloading Open-Meteo weather: {url}")
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read().decode("utf-8")
        cache_path.write_text(payload, encoding="utf-8")

    data = json.loads(cache_path.read_text(encoding="utf-8"))
    hourly = data.get("hourly", {})
    if not hourly or "time" not in hourly:
        raise RuntimeError(f"Open-Meteo response missing hourly data: {cache_path}")

    weather = pd.DataFrame(hourly)
    weather["hour"] = pd.to_datetime(weather["time"], errors="coerce")
    weather = weather.dropna(subset=["hour"]).drop(columns=["time"])
    numeric_columns = [
        "temperature_2m",
        "precipitation",
        "snowfall",
        "wind_speed_10m",
        "weather_code",
    ]
    for column in numeric_columns:
        weather[column] = pd.to_numeric(weather[column], errors="coerce")

    # Timezone-local historical APIs can produce ambiguous local labels around
    # daylight saving transitions. Collapse duplicates deterministically and
    # keep a missing flag before filling model features.
    weather = weather.groupby("hour", as_index=False)[numeric_columns].mean()
    full_hours = pd.date_range(
        pd.Timestamp(start_date),
        pd.Timestamp(end_date) + pd.Timedelta(hours=23),
        freq="h",
    )
    weather = pd.DataFrame({"hour": full_hours}).merge(weather, on="hour", how="left")
    weather["weather_missing_int"] = (
        weather[numeric_columns].isna().any(axis=1).astype(int)
    )
    weather[numeric_columns] = weather[numeric_columns].interpolate(
        limit_direction="both"
    )
    weather["is_precip_int"] = (weather["precipitation"].fillna(0) > 0).astype(int)
    weather["is_snow_int"] = (weather["snowfall"].fillna(0) > 0).astype(int)
    weather["temperature_below_comfort"] = np.maximum(
        0, 12 - weather["temperature_2m"].fillna(12)
    )
    weather["temperature_above_comfort"] = np.maximum(
        0, weather["temperature_2m"].fillna(21) - 24
    )
    return weather


def build_event_calendar(*, start_year: int, end_year: int) -> pd.DataFrame:
    """Build date-windowed holiday and public-event features."""
    rows: list[dict[str, object]] = []
    for year in range(start_year, end_year + 1):
        rows.extend(federal_holiday_rows(year))
        rows.extend(major_nyc_event_rows(year))

    events = pd.DataFrame(rows)
    events["date"] = pd.to_datetime(events["date"]).dt.date.astype(str)
    events = events.drop_duplicates(["date", "event_name", "event_type"]).sort_values(
        "date"
    )

    window_rows: list[dict[str, object]] = []
    for row in events.itertuples(index=False):
        event_date = pd.Timestamp(row.date)
        for offset, window_name, intensity_multiplier in [
            (-1, "lead_day", 0.35),
            (0, "event_day", 1.0),
            (1, "lag_day", 0.25),
        ]:
            window_rows.append(
                {
                    "date": str((event_date + pd.Timedelta(days=offset)).date()),
                    "event_name": row.event_name,
                    "event_type": row.event_type,
                    "event_window": window_name,
                    "event_intensity": float(row.event_weight) * intensity_multiplier,
                    "is_federal_holiday": bool(row.is_federal_holiday),
                    "is_major_event": bool(row.is_major_event),
                }
            )

    return pd.DataFrame(window_rows).sort_values(
        ["date", "event_intensity"], ascending=[True, False]
    )


def federal_holiday_rows(year: int) -> list[dict[str, object]]:
    """Return federal holiday rows for one calendar year."""
    holidays = [
        (pd.Timestamp(year=year, month=1, day=1), "New Year's Day"),
        (nth_weekday(year, 1, calendar.MONDAY, 3), "Martin Luther King Jr. Day"),
        (nth_weekday(year, 2, calendar.MONDAY, 3), "Presidents' Day"),
        (last_weekday(year, 5, calendar.MONDAY), "Memorial Day"),
        (pd.Timestamp(year=year, month=6, day=19), "Juneteenth"),
        (pd.Timestamp(year=year, month=7, day=4), "Independence Day"),
        (nth_weekday(year, 9, calendar.MONDAY, 1), "Labor Day"),
        (
            nth_weekday(year, 10, calendar.MONDAY, 2),
            "Indigenous Peoples' Day / Columbus Day",
        ),
        (pd.Timestamp(year=year, month=11, day=11), "Veterans Day"),
        (nth_weekday(year, 11, calendar.THURSDAY, 4), "Thanksgiving Day"),
        (pd.Timestamp(year=year, month=12, day=25), "Christmas Day"),
    ]
    return [
        {
            "date": str(date.date()),
            "event_name": name,
            "event_type": "federal_holiday",
            "event_weight": 0.75,
            "is_federal_holiday": True,
            "is_major_event": False,
        }
        for date, name in holidays
    ]


def major_nyc_event_rows(year: int) -> list[dict[str, object]]:
    """Return selected major NYC public-event rows for one calendar year."""
    if year != 2024:
        return []
    return [
        {
            "date": "2024-06-30",
            "event_name": "NYC Pride March",
            "event_type": "major_parade",
            "event_weight": 1.0,
            "is_federal_holiday": False,
            "is_major_event": True,
        },
        {
            "date": "2024-11-03",
            "event_name": "TCS New York City Marathon",
            "event_type": "major_race",
            "event_weight": 1.0,
            "is_federal_holiday": False,
            "is_major_event": True,
        },
        {
            "date": "2024-11-28",
            "event_name": "Macy's Thanksgiving Day Parade",
            "event_type": "major_parade",
            "event_weight": 0.9,
            "is_federal_holiday": True,
            "is_major_event": True,
        },
        {
            "date": "2024-12-31",
            "event_name": "New Year's Eve",
            "event_type": "civic_event",
            "event_weight": 0.8,
            "is_federal_holiday": False,
            "is_major_event": True,
        },
    ]


def nth_weekday(year: int, month: int, weekday: int, n: int) -> pd.Timestamp:
    """Return the nth weekday in a month as a timestamp."""
    first = pd.Timestamp(year=year, month=month, day=1)
    offset = (weekday - first.weekday()) % 7
    return first + pd.Timedelta(days=offset + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> pd.Timestamp:
    """Return the last requested weekday in a month as a timestamp."""
    last_day = calendar.monthrange(year, month)[1]
    last = pd.Timestamp(year=year, month=month, day=last_day)
    offset = (last.weekday() - weekday) % 7
    return last - pd.Timedelta(days=offset)


def build_model_panel(
    cluster_hourly: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    weather: pd.DataFrame,
    event_calendar: pd.DataFrame,
) -> pd.DataFrame:
    """Join cluster demand with calendar, weather, event, and lag features."""
    panel = cluster_hourly.copy()
    panel = add_calendar_columns(panel)
    event_features = build_hourly_event_features(
        panel[["hour", "date", "hour_of_day"]].drop_duplicates(), event_calendar
    )
    panel = panel.merge(weather, on="hour", how="left")
    panel = panel.merge(event_features, on="hour", how="left")

    fill_zero_columns = [
        "event_intensity",
        "is_major_event_int",
        "is_event_peak_hour_int",
        "is_holiday_eve_int",
        "is_holiday_window_int",
    ]
    for column in fill_zero_columns:
        panel[column] = panel[column].fillna(0)
    panel["event_names"] = panel["event_names"].fillna("")

    cluster_lookup = cluster_summary.set_index("segment_id")[
        ["annual_starts", "share_of_system_starts", "rank"]
    ].to_dict("index")
    panel["annual_segment_starts"] = panel["segment_id"].map(
        lambda value: cluster_lookup.get(value, {}).get("annual_starts", np.nan)
    )
    panel["segment_rank"] = panel["segment_id"].map(
        lambda value: cluster_lookup.get(value, {}).get("rank", np.nan)
    )
    system_total = panel.loc[panel["segment_id"] == "system_total", "rides"].sum()
    panel.loc[panel["segment_id"] == "system_total", "annual_segment_starts"] = (
        system_total
    )
    panel.loc[panel["segment_id"] == "system_total", "segment_rank"] = 0
    panel["share_of_system_starts"] = panel["annual_segment_starts"] / system_total

    panel = add_forecast_features(panel)
    return panel


def add_calendar_columns(panel: pd.DataFrame) -> pd.DataFrame:
    """Add calendar dimensions and federal holiday flags to an hourly panel."""
    frame = panel.copy()
    frame["date"] = frame["hour"].dt.date.astype(str)
    frame["month"] = frame["hour"].dt.to_period("M").astype(str)
    frame["day_name"] = frame["hour"].dt.day_name()
    frame["day_of_week"] = frame["hour"].dt.dayofweek
    frame["hour_of_day"] = frame["hour"].dt.hour
    frame["day_of_year"] = frame["hour"].dt.dayofyear
    frame["is_weekend"] = frame["day_of_week"].isin([5, 6])
    holidays = {
        row["date"]
        for year in range(frame["hour"].dt.year.min(), frame["hour"].dt.year.max() + 1)
        for row in federal_holiday_rows(int(year))
    }
    frame["is_federal_holiday"] = frame["date"].isin(holidays)
    return frame


def build_hourly_event_features(
    hours: pd.DataFrame, event_calendar: pd.DataFrame
) -> pd.DataFrame:
    """Expand date-level event windows into hour-level model features."""
    events = event_calendar.copy()
    events["is_federal_holiday_int"] = events["is_federal_holiday"].astype(int)
    events["is_major_event_int"] = events["is_major_event"].astype(int)
    daily = (
        events.groupby("date", as_index=False)
        .agg(
            event_intensity=("event_intensity", "max"),
            is_major_event_int=("is_major_event_int", "max"),
            is_federal_holiday_event_int=("is_federal_holiday_int", "max"),
            event_names=(
                "event_name",
                lambda values: "; ".join(sorted(set(map(str, values)))),
            ),
            event_types=(
                "event_type",
                lambda values: "; ".join(sorted(set(map(str, values)))),
            ),
            event_windows=(
                "event_window",
                lambda values: "; ".join(sorted(set(map(str, values)))),
            ),
        )
        .sort_values("date")
    )
    frame = hours.merge(daily, on="date", how="left")
    frame["event_intensity"] = frame["event_intensity"].fillna(0)
    frame["is_major_event_int"] = frame["is_major_event_int"].fillna(0).astype(int)
    frame["event_names"] = frame["event_names"].fillna("")
    frame["event_types"] = frame["event_types"].fillna("")
    frame["event_windows"] = frame["event_windows"].fillna("")
    frame["is_holiday_eve_int"] = (
        frame["event_windows"].str.contains("lead_day", regex=False)
        & frame["event_types"].str.contains("federal_holiday", regex=False)
    ).astype(int)
    frame["is_holiday_window_int"] = (
        frame["event_types"].str.contains("federal_holiday", regex=False)
    ).astype(int)
    daytime_event = (
        (frame["is_major_event_int"] == 1)
        & frame["hour_of_day"].between(6, 18)
        & ~frame["event_names"].str.contains("New Year's Eve", regex=False)
    )
    night_event = frame["event_names"].str.contains(
        "New Year's Eve", regex=False
    ) & frame["hour_of_day"].between(18, 23)
    frame["is_event_peak_hour_int"] = (daytime_event | night_event).astype(int)
    return frame[
        [
            "hour",
            "event_intensity",
            "is_major_event_int",
            "is_event_peak_hour_int",
            "is_holiday_eve_int",
            "is_holiday_window_int",
            "event_names",
            "event_types",
            "event_windows",
        ]
    ]


def add_forecast_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Add leakage-aware calendar, lag, and rolling features by segment."""
    frame = panel.copy().sort_values(["segment_id", "hour"]).reset_index(drop=True)
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

    grouped = frame.groupby("segment_id", group_keys=False)
    frame["lag_24h"] = grouped["rides"].shift(24)
    frame["lag_168h"] = grouped["rides"].shift(168)
    frame["rolling_24h_prior_day"] = grouped["rides"].apply(
        lambda values: values.shift(24).rolling(24, min_periods=12).mean()
    )
    frame["rolling_168h_prior_day"] = grouped["rides"].apply(
        lambda values: values.shift(24).rolling(168, min_periods=72).mean()
    )
    return frame


def build_rolling_backtests(
    panel: pd.DataFrame,
    *,
    horizon_hours: int,
    min_train_days: int,
    origin_step_days: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Score segment forecasts across leakage-aware rolling origins."""
    first_origin = (panel["hour"].min() + pd.Timedelta(days=min_train_days)).normalize()
    last_origin = panel["hour"].max() - pd.Timedelta(hours=horizon_hours - 1)
    origins = pd.date_range(
        first_origin, last_origin.normalize(), freq=f"{origin_step_days}D"
    )

    scored_rows: list[dict[str, object]] = []
    origin_rows: list[dict[str, object]] = []
    segment_columns = ["segment_id", "segment_label", "segment_type"]

    for segment_id, segment in panel.groupby("segment_id", sort=False):
        segment = segment.sort_values("hour").reset_index(drop=True)
        hourly_by_hour = segment.set_index("hour")["rides"].astype(float)
        segment_context = segment.loc[0, segment_columns].to_dict()
        for origin in origins:
            train = segment[segment["hour"] < origin].copy()
            test = segment[
                (segment["hour"] >= origin)
                & (segment["hour"] < origin + pd.Timedelta(hours=horizon_hours))
            ].copy()
            if len(train) < min_train_days * 24 or len(test) != horizon_hours:
                continue

            forecasts = {
                "previous_day": forecast_from_previous(
                    hourly_by_hour, test["hour"], 24
                ),
                "previous_week": forecast_from_previous(
                    hourly_by_hour, test["hour"], 168
                ),
                "calendar_lag_ridge": forecast_from_ridge(
                    train, test, BASE_REGRESSION_FEATURES
                ),
                "weather_event_ridge": forecast_from_ridge(
                    train, test, WEATHER_EVENT_FEATURES
                ),
            }
            for model, forecast in forecasts.items():
                scored = pd.DataFrame(
                    {
                        **segment_context,
                        "origin": origin,
                        "hour": test["hour"].to_numpy(),
                        "model": model,
                        "model_label": label_model(model),
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
                    {
                        **segment_context,
                        "origin": origin,
                        "model": model,
                        "model_label": label_model(model),
                        **score_forecast(scored),
                    }
                )

    scored_df = pd.DataFrame(scored_rows)
    origin_metrics = pd.DataFrame(origin_rows)
    aggregate_metrics = aggregate_model_metrics(scored_df, origin_metrics)
    return aggregate_metrics, origin_metrics, scored_df


def forecast_from_previous(
    hourly_by_hour: pd.Series, hours: pd.Series, lag: int
) -> pd.Series:
    """Forecast each hour from the same segment's lagged historical value."""
    return pd.Series(
        [hourly_by_hour.get(hour - pd.Timedelta(hours=lag), np.nan) for hour in hours],
        index=hours.index,
        dtype=float,
    )


def forecast_from_ridge(
    train: pd.DataFrame, test: pd.DataFrame, features: list[str]
) -> pd.Series:
    """Fit a regularized linear model and forecast non-negative demand."""
    usable_train = train.dropna(subset=features + ["rides"]).copy()
    usable_test = test.dropna(subset=features).copy()
    predictions = pd.Series(np.nan, index=test.index, dtype=float)
    if len(usable_train) < max(240, len(features) * 20) or usable_test.empty:
        return predictions

    x_train = usable_train[features].to_numpy(dtype=float)
    y_train = usable_train["rides"].to_numpy(dtype=float)
    means = x_train.mean(axis=0)
    stds = x_train.std(axis=0)
    stds[stds == 0] = 1.0
    x_scaled = (x_train - means) / stds
    x_design = np.column_stack([np.ones(len(x_scaled)), x_scaled])

    alpha = 25.0 if len(features) <= len(BASE_REGRESSION_FEATURES) else 35.0
    penalty = np.eye(x_design.shape[1])
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(
        x_design.T @ x_design + alpha * penalty, x_design.T @ y_train
    )

    x_test = usable_test[features].to_numpy(dtype=float)
    x_test_scaled = (x_test - means) / stds
    test_design = np.column_stack([np.ones(len(x_test_scaled)), x_test_scaled])
    predictions.loc[usable_test.index] = np.maximum(0, test_design @ beta)
    return predictions


def score_forecast(scored: pd.DataFrame) -> dict[str, float]:
    """Compute standard forecast-error metrics for scored rows."""
    if scored.empty:
        return {"n": 0, "mae": np.nan, "rmse": np.nan, "mape": np.nan, "wape": np.nan}
    error = scored["actual"] - scored["forecast"]
    denom = scored["actual"].replace(0, np.nan)
    actual_sum = float(scored["actual"].sum())
    return {
        "n": int(len(scored)),
        "mae": float(error.abs().mean()),
        "rmse": float(math.sqrt((error**2).mean())),
        "mape": float((error.abs() / denom).dropna().mean()),
        "wape": float(error.abs().sum() / actual_sum) if actual_sum else np.nan,
    }


def aggregate_model_metrics(
    scored: pd.DataFrame, origin_metrics: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate scored forecast rows into segment/model metrics."""
    if scored.empty:
        return pd.DataFrame()

    winner_counts = pd.DataFrame()
    if not origin_metrics.empty:
        winner_idx = origin_metrics.groupby(["segment_id", "origin"])["mae"].idxmin()
        winner_counts = (
            origin_metrics.loc[winner_idx]
            .groupby(["segment_id", "model"])
            .size()
            .rename("origin_wins")
        )

    rows = []
    group_columns = [
        "segment_id",
        "segment_label",
        "segment_type",
        "model",
        "model_label",
    ]
    for keys, part in scored.groupby(group_columns, dropna=False):
        key_map = dict(zip(group_columns, keys))
        origin_part = origin_metrics[
            (origin_metrics["segment_id"] == key_map["segment_id"])
            & (origin_metrics["model"] == key_map["model"])
        ]
        origins = int(part["origin"].nunique())
        rows.append(
            {
                **key_map,
                "origins": origins,
                "holdout_hours": int(len(part)),
                "mean_actual": float(part["actual"].mean()),
                "total_actual": float(part["actual"].sum()),
                "median_origin_mae": float(origin_part["mae"].median())
                if not origin_part.empty
                else np.nan,
                "origin_wins": int(
                    winner_counts.get((key_map["segment_id"], key_map["model"]), 0)
                )
                if not winner_counts.empty
                else 0,
                **score_forecast(part),
            }
        )

    metrics = (
        pd.DataFrame(rows)
        .sort_values(["segment_id", "mae", "rmse"])
        .reset_index(drop=True)
    )
    max_origins = metrics.groupby("segment_id")["origins"].transform("max")
    metrics["origin_win_rate"] = metrics["origin_wins"] / max_origins.replace(0, np.nan)
    return metrics


def build_model_lift(metrics: pd.DataFrame) -> pd.DataFrame:
    """Compare weather/event ridge errors against the baseline models."""
    if metrics.empty:
        return pd.DataFrame()
    validate_model_lift_metrics(metrics)
    pivot = metrics.pivot_table(
        index=["segment_id", "segment_label", "segment_type"],
        columns="model",
        values=["mae", "rmse", "wape"],
        aggfunc="first",
    )
    pivot.columns = [f"{metric}_{model}" for metric, model in pivot.columns]
    lift = pivot.reset_index()
    for baseline in ["previous_week", "calendar_lag_ridge"]:
        lift[f"mae_lift_vs_{baseline}"] = (
            lift[f"mae_{baseline}"] - lift["mae_weather_event_ridge"]
        )
        baseline_mae = lift[f"mae_{baseline}"].replace(0, np.nan)
        lift[f"mae_lift_pct_vs_{baseline}"] = (
            lift[f"mae_lift_vs_{baseline}"] / baseline_mae
        ).fillna(0.0)
    model_order = [
        "weather_event_ridge",
        "calendar_lag_ridge",
        "previous_week",
        "previous_day",
    ]
    best_rows = []
    for row in lift.itertuples(index=False):
        available = {
            model: getattr(row, f"mae_{model}")
            for model in model_order
            if hasattr(row, f"mae_{model}")
            and not pd.isna(getattr(row, f"mae_{model}"))
        }
        best_model = min(available, key=available.get)
        best_rows.append(best_model)
    lift["best_model"] = best_rows
    lift["best_model_label"] = lift["best_model"].map(label_model)
    return lift


def validate_model_lift_metrics(metrics: pd.DataFrame) -> None:
    """Validate segment/model metrics before calculating model lift."""
    required_columns = {
        "segment_id",
        "segment_label",
        "segment_type",
        "model",
        "mae",
        "rmse",
        "wape",
    }
    missing = sorted(required_columns.difference(metrics.columns))
    if missing:
        raise KeyError(f"Model lift metrics are missing required columns: {missing}")

    numeric_columns = ["mae", "rmse", "wape"]
    for column in numeric_columns:
        values = pd.to_numeric(metrics[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(f"Model lift metrics have invalid values in {column}.")
        if (values < 0).any():
            raise ValueError(f"Model lift metrics have negative values in {column}.")
        metrics[column] = values.astype(float)

    duplicate_rows = metrics.loc[
        metrics.duplicated(["segment_id", "model"], keep=False),
        ["segment_id", "model"],
    ].drop_duplicates()
    if not duplicate_rows.empty:
        duplicate_keys = [
            f"{row.segment_id}/{row.model}"
            for row in duplicate_rows.itertuples(index=False)
        ]
        raise ValueError(
            "Model lift metrics have duplicate segment/model row(s): "
            + ", ".join(duplicate_keys)
        )

    required_models = set(MODEL_LIFT_REQUIRED_MODELS)
    missing_segments = []
    for segment_id, group in metrics.groupby("segment_id"):
        missing_models = sorted(required_models - set(group["model"]))
        if missing_models:
            missing_segments.append(f"{segment_id}: {', '.join(missing_models)}")
    if missing_segments:
        raise ValueError(
            "Model lift metrics are missing required model row(s): "
            + "; ".join(missing_segments)
        )


def build_capacity_priorities(
    cluster_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    lift: pd.DataFrame,
) -> pd.DataFrame:
    """Rank clusters for rebalancing and capacity-planning review."""
    cluster_metrics = metrics[
        (metrics["segment_type"] == "station_cluster")
        & (metrics["model"] == "weather_event_ridge")
    ][["segment_id", "mae", "rmse", "wape", "mean_actual"]]
    priorities = cluster_summary.merge(cluster_metrics, on="segment_id", how="left")
    priorities = priorities.merge(
        lift[
            [
                "segment_id",
                "mae_lift_pct_vs_previous_week",
                "mae_lift_pct_vs_calendar_lag_ridge",
                "best_model_label",
            ]
        ],
        on="segment_id",
        how="left",
    )
    priorities["priority_score"] = (
        priorities["share_of_system_starts"].fillna(0) * 100
        + priorities["wape"].fillna(0) * 10
        + priorities["mae"].fillna(0) / max(priorities["mae"].max(), 1)
    )
    priorities = priorities.sort_values("priority_score", ascending=False).reset_index(
        drop=True
    )
    priorities["capacity_planning_use"] = priorities.apply(
        capacity_planning_use, axis=1
    )
    return priorities


def capacity_planning_use(row: pd.Series) -> str:
    """Convert forecast lift and reliability into a planning recommendation."""
    if pd.isna(row.get("mae_lift_pct_vs_previous_week")):
        return "Needs more validation before operational use."
    if row["mae_lift_pct_vs_previous_week"] > 0.05:
        return "Use as a rebalancing watchlist signal when event or weather pressure is high."
    if row["mae_lift_pct_vs_calendar_lag_ridge"] > 0:
        return "Use as a secondary planning signal next to the calendar-lag ridge baseline."
    return "Keep as a demand segment, but monitor before replacing simpler baselines."


def label_model(model: object) -> str:
    """Return a reader-friendly model label."""
    return MODEL_LABELS.get(str(model), str(model).replace("_", " ").title())


def build_summary(
    *,
    args: argparse.Namespace,
    monthly_summaries: pd.DataFrame,
    system_hourly: pd.DataFrame,
    station_metadata: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    panel: pd.DataFrame,
    weather: pd.DataFrame,
    event_calendar: pd.DataFrame,
    metrics: pd.DataFrame,
    lift: pd.DataFrame,
    priorities: pd.DataFrame,
) -> dict[str, object]:
    """Build the headline JSON payload used by the HTML report."""
    system_lift = lift[lift["segment_id"] == "system_total"].iloc[0].to_dict()
    cluster_lift = lift[lift["segment_type"] == "station_cluster"].copy()
    rich_beats_week = int((cluster_lift["mae_lift_pct_vs_previous_week"] > 0).sum())
    rich_beats_ridge = int(
        (cluster_lift["mae_lift_pct_vs_calendar_lag_ridge"] > 0).sum()
    )
    best_rich_clusters = int(
        (cluster_lift["best_model"] == "weather_event_ridge").sum()
    )
    weather_event_metrics = metrics[metrics["model"] == "weather_event_ridge"]
    best_priority = priorities.iloc[0].to_dict() if not priorities.empty else {}
    missing_weather_hours = int(weather["weather_missing_int"].sum())
    station_id_denominator = (
        monthly_summaries["rows_valid_fixed_window"].sum()
        if "rows_valid_fixed_window" in monthly_summaries.columns
        else monthly_summaries["rows_valid"].sum()
    )
    summary = {
        "title": "Citi Bike Station-Cluster Forecasting",
        "decision": "Rebalancing and station-capacity planning",
        "start_month": args.start_month,
        "end_month": args.end_month,
        "months": int(len(monthly_summaries)),
        "top_stations_clustered": int(cluster_summary["station_count"].sum()),
        "station_clusters": int(len(cluster_summary)),
        "segments_modeled": int(panel["segment_id"].nunique()),
        "hourly_observations_per_segment": int(
            panel.groupby("segment_id")["hour"].nunique().max()
        ),
        "total_system_rides": int(system_hourly["rides"].sum()),
        "rows_total": int(monthly_summaries["rows_total"].sum()),
        "rows_valid": int(monthly_summaries["rows_valid"].sum()),
        "station_id_coverage": safe_divide(
            monthly_summaries["rows_with_station_id"].sum(),
            station_id_denominator,
        ),
        "weather_hours": int(len(weather)),
        "weather_missing_hours": missing_weather_hours,
        "event_feature_dates": int(event_calendar["date"].nunique()),
        "rolling_origins": int(metrics["origins"].max()) if not metrics.empty else 0,
        "horizon_hours": int(args.horizon_hours),
        "origin_step_days": int(args.origin_step_days),
        "min_train_days": int(args.min_train_days),
        "weather_event_beats_previous_week_clusters": rich_beats_week,
        "weather_event_beats_calendar_lag_ridge_clusters": rich_beats_ridge,
        "weather_event_best_clusters": best_rich_clusters,
        "cluster_count": int(len(cluster_lift)),
        "system_weather_event_lift_pct_vs_previous_week": float(
            system_lift["mae_lift_pct_vs_previous_week"]
        ),
        "system_weather_event_lift_pct_vs_calendar_lag_ridge": float(
            system_lift["mae_lift_pct_vs_calendar_lag_ridge"]
        ),
        "weather_event_mean_mae": float(weather_event_metrics["mae"].mean()),
        "top_capacity_priority": best_priority,
        "recommendation": recommendation_text(cluster_lift, system_lift),
    }
    return make_json_safe(summary)


def safe_divide(numerator: object, denominator: object) -> float:
    """Divide two values while returning zero for zero or missing denominators."""
    denominator_value = float(denominator)
    if denominator_value == 0 or not np.isfinite(denominator_value):
        return 0.0
    return float(numerator) / denominator_value


def recommendation_text(
    cluster_lift: pd.DataFrame, system_lift: dict[str, object]
) -> str:
    """Choose a concise recommendation from segment-level model lift."""
    rich_beats_week = int((cluster_lift["mae_lift_pct_vs_previous_week"] > 0).sum())
    rich_beats_ridge = int(
        (cluster_lift["mae_lift_pct_vs_calendar_lag_ridge"] > 0).sum()
    )
    cluster_count = max(int(len(cluster_lift)), 1)
    if rich_beats_week >= math.ceil(
        cluster_count / 2
    ) and rich_beats_ridge >= math.ceil(cluster_count / 3):
        return (
            "Use weather/event cluster forecasts as a rebalancing planning layer, "
            "with the calendar-lag ridge retained as the control benchmark."
        )
    if rich_beats_week >= math.ceil(cluster_count / 2):
        return (
            "Use the cluster targets for capacity planning, but keep the simpler ridge "
            "model as the default until weather/event lift is more consistent."
        )
    return (
        "Use the station clusters as the operational unit, but treat weather/event "
        "features as diagnostics until they consistently beat simpler baselines."
    )


def make_json_safe(value: object) -> object:
    """Recursively convert pandas and NumPy values into JSON-safe objects."""
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
    """Apply the shared report chart theme."""
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "figure.edgecolor": "none",
            "savefig.facecolor": TOKENS["surface"],
            "savefig.edgecolor": "none",
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.monospace": MONO_FONT_FAMILY,
            "patch.linewidth": 1.0,
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
    """Add a wrapped title and subtitle to a static Matplotlib chart."""
    title = textwrap.fill(str(title).strip(), width=title_width, break_long_words=False)
    subtitle = textwrap.fill(
        str(subtitle).strip(), width=subtitle_width, break_long_words=False
    )
    if not title or not subtitle:
        raise ValueError("Every shipped chart needs a non-empty title and subtitle.")
    title_lines = title.count("\n") + 1
    subtitle_lines = subtitle.count("\n") + 1
    fig.subplots_adjust(
        top=max(0.62, 0.86 - 0.045 * (title_lines - 1) - 0.032 * (subtitle_lines - 1))
    )
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
        0.93 - 0.045 * (title_lines - 1),
        subtitle,
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
        linespacing=1.18,
    )
    sns.despine(ax=ax)


def format_date_axis(ax: plt.Axes, *, max_ticks: int = 6) -> None:
    """Format datetime axes with concise, non-overlapping tick labels."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def save_chart(fig: plt.Figure, filename: str) -> Path:
    """Save one chart PNG to the report chart directory."""
    path = CHART_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def build_charts(
    assignments: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    lift: pd.DataFrame,
    scored: pd.DataFrame,
    priorities: pd.DataFrame,
) -> list[Path]:
    """Render all station-cluster report charts."""
    use_chart_theme()
    paths = [
        plot_station_cluster_map(assignments),
        plot_cluster_volume(cluster_summary),
        plot_model_lift(lift),
        plot_segment_model_mae(metrics),
    ]
    if not scored.empty:
        paths.append(plot_forecast_example(scored, priorities))
    return paths


def cluster_palette(cluster_ids: Iterable[str]) -> dict[str, str]:
    """Return explicit fill colors for station-cluster categories."""
    ids = list(cluster_ids)
    palette = {}
    for idx, cluster_id in enumerate(ids):
        family = COLOR_FAMILIES[CLUSTER_FAMILIES[idx % len(CLUSTER_FAMILIES)]]
        tone = "base" if idx < 5 else "light"
        palette[cluster_id] = family[tone]
    return palette


def cluster_edge_palette(cluster_ids: Iterable[str]) -> dict[str, str]:
    """Return explicit edge colors for station-cluster categories."""
    ids = list(cluster_ids)
    palette = {}
    for idx, cluster_id in enumerate(ids):
        family = COLOR_FAMILIES[CLUSTER_FAMILIES[idx % len(CLUSTER_FAMILIES)]]
        palette[cluster_id] = family["dark"]
    return palette


def plot_station_cluster_map(assignments: pd.DataFrame) -> Path:
    """Plot clustered station locations with volume-scaled markers."""
    plot_df = assignments.copy()
    cluster_ids = sorted(plot_df["cluster_id"].unique())
    palette = cluster_palette(cluster_ids)
    edge_palette = cluster_edge_palette(cluster_ids)
    fig, ax = plt.subplots(figsize=(9.8, 6.0))
    for cluster_id, part in plot_df.groupby("cluster_id"):
        size = 25 + (part["annual_starts"] / plot_df["annual_starts"].max()) * 240
        ax.scatter(
            part["longitude"],
            part["latitude"],
            s=size,
            facecolors=palette[cluster_id],
            edgecolors=edge_palette[cluster_id],
            linewidths=0.7,
            alpha=0.72,
            label=cluster_id.replace("_", " ").title(),
        )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=3)
    add_chart_header(
        fig,
        ax,
        "Station ID clusters from observed metadata",
        "Top station IDs by 2024 starts, clustered by observed latitude and longitude. Marker size reflects annual starts.",
    )
    return save_chart(fig, "station_cluster_map.png")


def plot_cluster_volume(cluster_summary: pd.DataFrame) -> Path:
    """Plot annual trip starts by station cluster."""
    plot_df = cluster_summary.sort_values("annual_starts", ascending=True)
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    palette = cluster_palette(plot_df["cluster_id"])
    edge_palette = cluster_edge_palette(plot_df["cluster_id"])
    bars = ax.barh(
        plot_df["cluster_label"],
        plot_df["annual_starts"],
        color=[palette[value] for value in plot_df["cluster_id"]],
        edgecolor=[edge_palette[value] for value in plot_df["cluster_id"]],
        linewidth=1.0,
    )
    for bar, value in zip(bars, plot_df["annual_starts"]):
        ax.text(
            bar.get_width() + plot_df["annual_starts"].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value / 1000:,.0f}k",
            va="center",
            fontsize=8,
            color=TOKENS["ink"],
        )
    ax.set_xlabel("2024 trip starts")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(
            lambda value, _: "0" if value == 0 else f"{value / 1_000_000:.1f}M"
        )
    )
    ax.set_xlim(0, plot_df["annual_starts"].max() * 1.16)
    add_chart_header(
        fig,
        ax,
        "Cluster volume creates an operational planning unit",
        "Annual starts from the clustered top station IDs. These are demand pools, not inventory or dock-capacity counts.",
    )
    return save_chart(fig, "station_cluster_volume.png")


def plot_model_lift(lift: pd.DataFrame) -> Path:
    """Plot weather/event ridge MAE lift versus the previous-week baseline."""
    plot_df = lift.copy()
    plot_df["segment_short"] = np.where(
        plot_df["segment_id"] == "system_total",
        "System total",
        plot_df["segment_label"].str.replace(r"^Cluster \d+ - ", "", regex=True),
    )
    plot_df = plot_df.sort_values("mae_lift_pct_vs_previous_week")
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    positive_family = COLOR_FAMILIES["olive"]
    negative_family = COLOR_FAMILIES["orange"]
    values = plot_df["mae_lift_pct_vs_previous_week"].fillna(0)
    colors = np.where(values >= 0, positive_family["base"], negative_family["base"])
    edge_colors = np.where(
        values >= 0, positive_family["dark"], negative_family["dark"]
    )
    bars = ax.barh(
        plot_df["segment_short"],
        values,
        color=colors,
        edgecolor=edge_colors,
        linewidth=1.0,
    )
    for bar, value in zip(bars, values):
        x_offset = 0.006 if value >= 0 else -0.006
        ax.text(
            value + x_offset,
            bar.get_y() + bar.get_height() / 2,
            f"{value * 100:+.1f}%",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8,
            color=TOKENS["ink"],
        )
    ax.axvline(0, color=TOKENS["ink"], linewidth=1.0)
    max_abs = max(abs(values.min()), abs(values.max()), 0.02)
    ax.set_xlim(-max_abs * 1.25, max_abs * 1.25)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("MAE improvement vs previous-week baseline")
    ax.set_ylabel("")
    ax.legend(
        handles=[
            Patch(
                facecolor=positive_family["base"],
                edgecolor=positive_family["dark"],
                label="Lower MAE",
            ),
            Patch(
                facecolor=negative_family["base"],
                edgecolor=negative_family["dark"],
                label="Higher MAE",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        frameon=False,
        ncol=2,
        borderaxespad=0,
    )
    add_chart_header(
        fig,
        ax,
        "Weather/event features are judged against a simple operating baseline",
        "Positive values mean the weather/event ridge beat previous-week MAE for that segment.",
    )
    return save_chart(fig, "station_cluster_model_lift.png")


def plot_segment_model_mae(metrics: pd.DataFrame) -> Path:
    """Plot model MAE by system and station-cluster target."""
    keep_models = ["previous_week", "calendar_lag_ridge", "weather_event_ridge"]
    plot_df = metrics[metrics["model"].isin(keep_models)].copy()
    plot_df["segment_short"] = np.where(
        plot_df["segment_id"] == "system_total",
        "System total",
        plot_df["segment_label"].str.replace(r"^Cluster \d+ - ", "", regex=True),
    )
    segment_order = (
        plot_df[plot_df["model"] == "weather_event_ridge"]
        .sort_values("mae", ascending=False)["segment_short"]
        .tolist()
    )
    model_order = [label_model(model) for model in keep_models]
    plot_df["model_label"] = pd.Categorical(
        plot_df["model_label"], categories=model_order, ordered=True
    )
    plot_df["segment_short"] = pd.Categorical(
        plot_df["segment_short"], categories=segment_order, ordered=True
    )
    palette = {
        "Previous week": COLOR_FAMILIES["orange"]["base"],
        "Calendar + lag ridge": COLOR_FAMILIES["blue"]["base"],
        "Weather/event ridge": COLOR_FAMILIES["olive"]["base"],
    }
    fig, ax = plt.subplots(figsize=(11.2, 6.0))
    sns.barplot(
        data=plot_df,
        x="mae",
        y="segment_short",
        hue="model_label",
        palette=palette,
        ax=ax,
        edgecolor=TOKENS["ink"],
        linewidth=0.8,
    )
    ax.set_xlabel("Mean absolute error, rides per hour")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        frameon=False,
        ncol=3,
        borderaxespad=0,
    )
    add_chart_header(
        fig,
        ax,
        "Segment MAE keeps the aggregate model honest",
        "System and station-cluster targets are scored on the same rolling 24-hour origins.",
    )
    return save_chart(fig, "station_cluster_segment_mae.png")


def plot_forecast_example(scored: pd.DataFrame, priorities: pd.DataFrame) -> Path:
    """Plot the final scored forecast trace for the top-priority cluster."""
    segment_id = (
        str(priorities.iloc[0]["segment_id"])
        if not priorities.empty
        else str(
            scored.loc[scored["segment_type"] == "station_cluster", "segment_id"].iloc[
                0
            ]
        )
    )
    segment_scored = scored[scored["segment_id"] == segment_id]
    origin = segment_scored["origin"].max()
    plot_df = segment_scored[
        (segment_scored["origin"] == origin)
        & (segment_scored["model"].isin(["previous_week", "weather_event_ridge"]))
    ].copy()
    actual = plot_df[["hour", "actual"]].drop_duplicates()
    segment_label = str(plot_df["segment_label"].iloc[0])
    fig, ax = plt.subplots(figsize=(10.8, 5.2))
    sns.lineplot(
        data=actual,
        x="hour",
        y="actual",
        ax=ax,
        color=COLOR_FAMILIES["blue"]["mid"],
        linewidth=1.3,
        label="Actual",
    )
    line_styles = {"previous_week": "--", "weather_event_ridge": "-."}
    line_colors = {
        "previous_week": COLOR_FAMILIES["orange"]["base"],
        "weather_event_ridge": COLOR_FAMILIES["olive"]["base"],
    }
    for model, part in plot_df.groupby("model"):
        sns.lineplot(
            data=part,
            x="hour",
            y="forecast",
            ax=ax,
            color=line_colors[model],
            linewidth=1.2,
            linestyle=line_styles[model],
            label=label_model(model),
        )
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel(str(pd.Timestamp(origin).date()))
    ax.set_ylabel("Trip starts")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=3)
    add_chart_header(
        fig,
        ax,
        "A cluster-level forecast trace supports rebalancing review",
        f"Final scored 24-hour origin for {segment_label}. The trace shows actuals against the operating baseline and richer model.",
    )
    return save_chart(fig, "station_cluster_forecast_example.png")


def write_outputs(
    *,
    monthly_summaries: pd.DataFrame,
    station_metadata: pd.DataFrame,
    assignments: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    panel: pd.DataFrame,
    weather: pd.DataFrame,
    event_calendar: pd.DataFrame,
    metrics: pd.DataFrame,
    origin_metrics: pd.DataFrame,
    scored: pd.DataFrame,
    lift: pd.DataFrame,
    priorities: pd.DataFrame,
    summary: dict[str, object],
    chart_paths: list[Path],
) -> None:
    """Write CSV, JSON, chart-backed HTML, and run-summary artifacts."""
    monthly_summaries.to_csv(
        OUT_DIR / "station_cluster_source_inventory.csv", index=False
    )
    station_metadata.to_csv(
        OUT_DIR / "station_cluster_station_metadata.csv", index=False
    )
    assignments.to_csv(OUT_DIR / "station_cluster_assignments.csv", index=False)
    cluster_summary.to_csv(OUT_DIR / "station_cluster_summary.csv", index=False)
    panel.to_csv(OUT_DIR / "station_cluster_hourly_profile.csv", index=False)
    weather.to_csv(OUT_DIR / "station_cluster_weather_hourly.csv", index=False)
    event_calendar.to_csv(OUT_DIR / "station_cluster_events.csv", index=False)
    metrics.to_csv(OUT_DIR / "station_cluster_model_metrics.csv", index=False)
    origin_metrics.to_csv(OUT_DIR / "station_cluster_origin_metrics.csv", index=False)
    scored.to_csv(OUT_DIR / "station_cluster_backtest_scored.csv", index=False)
    lift.to_csv(OUT_DIR / "station_cluster_model_lift.csv", index=False)
    priorities.to_csv(OUT_DIR / "station_cluster_capacity_priorities.csv", index=False)
    with (OUT_DIR / "station_cluster_forecast_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2)

    report = strip_trailing_whitespace(
        render_html_report(
            summary, cluster_summary, metrics, lift, priorities, chart_paths
        )
    )
    (OUT_DIR / "station_cluster_forecast.html").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Report written to {OUT_DIR / 'station_cluster_forecast.html'}")


def strip_trailing_whitespace(text: str) -> str:
    """Normalize trailing whitespace before writing generated text."""
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def render_html_report(
    summary: dict[str, object],
    cluster_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    lift: pd.DataFrame,
    priorities: pd.DataFrame,
    chart_paths: list[Path],
) -> str:
    """Render the station-cluster forecast report as portable static HTML."""
    chart_blocks = "\n".join(
        f"""
        <figure>
          <img src="charts/{html.escape(path.name)}" alt="{html.escape(path.stem.replace("_", " "))}">
          <figcaption>{html.escape(chart_caption(path.name))}</figcaption>
        </figure>
        """
        for path in chart_paths
    )
    cluster_table = table_html(
        cluster_summary,
        columns=[
            "cluster_label",
            "station_count",
            "annual_starts",
            "share_of_system_starts",
            "top_station",
        ],
        rename={
            "cluster_label": "Cluster",
            "station_count": "Stations",
            "annual_starts": "Annual Starts",
            "share_of_system_starts": "System Share",
            "top_station": "Highest-Volume Station",
        },
        formatters={
            "Annual Starts": fmt_number,
            "System Share": fmt_percent,
        },
    )
    lift_table = table_html(
        lift,
        columns=[
            "segment_label",
            "mae_previous_week",
            "mae_calendar_lag_ridge",
            "mae_weather_event_ridge",
            "mae_lift_pct_vs_previous_week",
            "mae_lift_pct_vs_calendar_lag_ridge",
            "best_model_label",
        ],
        rename={
            "segment_label": "Segment",
            "mae_previous_week": "Previous Week MAE",
            "mae_calendar_lag_ridge": "Calendar-Lag MAE",
            "mae_weather_event_ridge": "Weather/Event MAE",
            "mae_lift_pct_vs_previous_week": "Lift vs Previous Week",
            "mae_lift_pct_vs_calendar_lag_ridge": "Lift vs Calendar-Lag",
            "best_model_label": "Best Model",
        },
        formatters={
            "Previous Week MAE": fmt_number,
            "Calendar-Lag MAE": fmt_number,
            "Weather/Event MAE": fmt_number,
            "Lift vs Previous Week": fmt_signed_percent,
            "Lift vs Calendar-Lag": fmt_signed_percent,
        },
    )
    priority_table = table_html(
        priorities.head(4),
        columns=[
            "cluster_label",
            "annual_starts",
            "mae",
            "wape",
            "mae_lift_pct_vs_previous_week",
            "capacity_planning_use",
        ],
        rename={
            "cluster_label": "Cluster",
            "annual_starts": "Annual Starts",
            "mae": "Weather/Event MAE",
            "wape": "Weather/Event WAPE",
            "mae_lift_pct_vs_previous_week": "Lift vs Previous Week",
            "capacity_planning_use": "Planning Use",
        },
        formatters={
            "Annual Starts": fmt_number,
            "Weather/Event MAE": fmt_number,
            "Weather/Event WAPE": fmt_percent,
            "Lift vs Previous Week": fmt_signed_percent,
        },
    )
    weather_event_cluster_count = int(
        summary["weather_event_beats_previous_week_clusters"]
    )
    cluster_count = int(summary["cluster_count"])
    ridge_cluster_count = int(
        summary["weather_event_beats_calendar_lag_ridge_clusters"]
    )
    top_priority = summary.get("top_capacity_priority", {})
    if not isinstance(top_priority, dict):
        top_priority = {}

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
      --good: #71B436;
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
    h3 {{
      margin: 24px 0 8px;
      font-size: 18px;
      line-height: 1.3;
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
    .summary {{
      border-left: 4px solid var(--accent);
      background: #EAF1FE;
      border-radius: 6px;
      padding: 16px 18px;
    }}
    .summary li {{
      margin: 8px 0;
      color: var(--ink);
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
      .data-table {{ display: block; overflow-x: auto; white-space: nowrap; }}
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
  </header>

  <section>
    <h2>Executive Summary</h2>
    <ul class="summary">
      <li><strong>The upgrade changes the target from a citywide hourly total to operational demand pools.</strong> It models the system total plus {fmt_number(summary["station_clusters"])} station clusters built from stable station IDs, observed station names, and observed coordinates.</li>
      <li><strong>The richer model is evaluated, not assumed better.</strong> The weather/event ridge beat previous-week MAE in {weather_event_cluster_count} of {cluster_count} station clusters and beat the simpler calendar-lag ridge in {ridge_cluster_count} of {cluster_count} clusters.</li>
      <li><strong>The decision fit is rebalancing and capacity planning.</strong> The highest-priority planning cluster in this run is {html.escape(str(top_priority.get("cluster_label", "n/a")))} because it combines scale, forecast error, and operating relevance.</li>
      <li><strong>Recommended use:</strong> {html.escape(str(summary["recommendation"]))}</li>
    </ul>
  </section>

  <section class="kpis">
    <div class="kpi"><strong>{fmt_number(summary["total_system_rides"])}</strong><span>system trip starts modeled</span></div>
    <div class="kpi"><strong>{fmt_number(summary["station_clusters"])}</strong><span>station clusters</span></div>
    <div class="kpi"><strong>{fmt_number(summary["rolling_origins"])}</strong><span>rolling origins per segment</span></div>
    <div class="kpi"><strong>{fmt_percent(summary["station_id_coverage"])}</strong><span>valid rides with station ID</span></div>
  </section>

  <section>
    <h2>Station clusters make the forecast operational</h2>
    <p>
      The prior proof showed that aggregate hourly demand can be forecast from
      calendar and lag structure. This layer asks the more useful operating
      question: where should a rebalancing or capacity-planning review look
      first? Clusters are built from station IDs and observed coordinates, then
      scored as their own hourly targets.
    </p>
    {cluster_table}
  </section>

  <section>
    <h2>Weather and event features must earn their place</h2>
    <p>
      The richer model receives the same calendar and prior-demand features as
      the baseline ridge model, plus hourly weather, federal holiday windows,
      and selected major NYC event windows. The table below shows whether that
      extra context reduces out-of-sample MAE in rolling 24-hour validation.
    </p>
    {lift_table}
  </section>

  <section>
    <h2>Visual evidence</h2>
    {chart_blocks}
  </section>

  <section>
    <h2>Planning recommendation</h2>
    <p class="callout">
      Tie this model to <strong>{html.escape(str(summary["decision"]))}</strong>.
      Use cluster-level forecast misses and event/weather pressure as a watchlist
      for where to review bike availability, dock availability, and field-crew
      coverage. Do not treat trip-start demand as a direct inventory measure.
    </p>
    {priority_table}
  </section>

  <section>
    <h2>Further questions</h2>
    <ul>
      <li>Would the same cluster ranking hold with dock capacity, bike availability, and rebalancing truck logs?</li>
      <li>Should the cluster map be rebuilt quarterly as stations open, close, or shift coordinates?</li>
      <li>Would weather forecasts available at the origin perform differently from the observed weather used in this historical proof?</li>
    </ul>
  </section>

  <section>
    <h2>Caveats and assumptions</h2>
    <ul>
      <li>The target is trip starts, not unmet demand, empty docks, bike stockouts, or truck moves.</li>
      <li>Weather inputs use historical Open-Meteo reanalysis as a stand-in for weather forecasts that would be available before an operating day.</li>
      <li>The event calendar is a compact public-calendar feature set, not a complete New York City events database.</li>
      <li>Station metadata is derived from observed trip-history station IDs, names, and coordinates, not an official capacity or station-status feed.</li>
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
    """Render a selected DataFrame view as an HTML table."""
    display = df.loc[:, columns].rename(columns=rename)
    return display.to_html(
        index=False,
        escape=True,
        border=0,
        classes="data-table",
        formatters=formatters,
    )


def fmt_number(value: object, digits: int = 0) -> str:
    """Format a numeric value with thousands separators."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value):,.{digits}f}"


def fmt_percent(value: object, digits: int = 1) -> str:
    """Format a numeric proportion as a percentage."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def fmt_signed_percent(value: object, digits: int = 1) -> str:
    """Format a numeric proportion as a signed percentage."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:+.{digits}f}%"


def chart_caption(filename: str) -> str:
    """Return the report caption for a generated chart filename."""
    captions = {
        "station_cluster_map.png": "Station clusters are built from stable station IDs and observed coordinates.",
        "station_cluster_volume.png": "Annual starts by station cluster, giving the operating scale of each segment.",
        "station_cluster_model_lift.png": "Weather/event ridge MAE improvement versus the previous-week baseline by segment.",
        "station_cluster_segment_mae.png": "MAE comparison for previous-week, calendar-lag ridge, and weather/event ridge models.",
        "station_cluster_forecast_example.png": "Final 24-hour forecast trace for the top planning-priority station cluster.",
    }
    return captions.get(
        filename, filename.replace("_", " ").replace(".png", "").title()
    )


if __name__ == "__main__":
    main()
