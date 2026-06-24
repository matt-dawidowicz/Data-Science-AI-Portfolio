"""Build the January 2024 Citi Bike hourly time-series profile."""

from __future__ import annotations

import html
import json
import math
import shutil
import textwrap
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt


def find_project_root() -> Path:
    """Return the packaged project root that contains src/, outputs/, and docs/."""
    return Path(__file__).resolve().parents[1]


ROOT = find_project_root()
WORK_DIR = ROOT / "work"
DATA_DIR = WORK_DIR / "data"
CHART_DIR = ROOT / "outputs" / "charts"
OUT_DIR = ROOT / "outputs"

DATASET_MONTH = "2024-01"
DATA_URL = "https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip"
DATA_ZIP = DATA_DIR / "202401-citibike-tripdata.zip"
WEATHER_CSV = DATA_DIR / "nyc_open_meteo_hourly_2024_01.csv"

FONT_FAMILY = ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]
MONO_FONT_FAMILY = ["Consolas", "DejaVu Sans Mono", "monospace"]

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


def main() -> None:
    """Run the full January profile pipeline and write portfolio artifacts."""
    prepare_dirs()
    download_trip_data()
    summary, hourly, top_stations, member_mix, bike_mix = build_hourly_profile()
    weather = fetch_weather()
    hourly = (
        hourly.merge(weather, on="hour", how="left") if weather is not None else hourly
    )
    seasonality = build_seasonality(hourly)
    anomalies = detect_anomalies(hourly)
    forecast_results, forecast_scored, best_model, interval = run_forecast_backtest(
        hourly
    )
    chart_paths = build_charts(
        hourly, seasonality, top_stations, forecast_scored, best_model, interval
    )
    write_outputs(
        summary=summary,
        hourly=hourly,
        top_stations=top_stations,
        member_mix=member_mix,
        bike_mix=bike_mix,
        seasonality=seasonality,
        anomalies=anomalies,
        forecast_results=forecast_results,
        forecast_scored=forecast_scored,
        best_model=best_model,
        chart_paths=chart_paths,
        weather_loaded=weather is not None,
    )


def prepare_dirs() -> None:
    """Create local work, output, and chart directories."""
    for path in [WORK_DIR, DATA_DIR, OUT_DIR, CHART_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path) -> None:
    """Download a remote file to the requested local destination."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "codex-time-series-profile/1.0"}
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        with destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)


def download_trip_data() -> None:
    """Ensure the January 2024 Citi Bike trip archive is cached locally."""
    if DATA_ZIP.exists() and DATA_ZIP.stat().st_size > 1_000_000:
        return
    print(f"Downloading Citi Bike trip history from {DATA_URL}")
    download_file(DATA_URL, DATA_ZIP)
    if not zipfile.is_zipfile(DATA_ZIP):
        raise RuntimeError(f"Downloaded file is not a valid zip: {DATA_ZIP}")


def get_csv_header(zip_path: Path) -> list[str]:
    """Return the first CSV header found inside a Citi Bike archive."""
    with zipfile.ZipFile(zip_path) as zf:
        csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError(f"No CSV found inside {zip_path}")
        with zf.open(csv_names[0]) as raw:
            first_line = raw.readline().decode("utf-8-sig").strip()
    return first_line.split(",")


def build_hourly_profile() -> tuple[
    dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """Aggregate trip starts, mix tables, and summary statistics by hour."""
    expected = {
        "ride_id",
        "rideable_type",
        "started_at",
        "ended_at",
        "start_station_name",
        "member_casual",
    }
    header = set(get_csv_header(DATA_ZIP))
    missing = expected - header
    if missing:
        raise RuntimeError(f"Trip data is missing expected columns: {sorted(missing)}")

    usecols = sorted(expected)
    hourly_counter: Counter[pd.Timestamp] = Counter()
    station_counter: Counter[str] = Counter()
    member_counter: Counter[str] = Counter()
    bike_counter: Counter[str] = Counter()
    duration_minutes: list[np.ndarray] = []
    rows_total = 0
    rows_valid = 0
    first_started: pd.Timestamp | None = None
    last_started: pd.Timestamp | None = None

    with zipfile.ZipFile(DATA_ZIP) as zf:
        csv_names = sorted(
            name for name in zf.namelist() if name.lower().endswith(".csv")
        )
        for csv_name in csv_names:
            with zf.open(csv_name) as raw:
                reader = pd.read_csv(raw, usecols=usecols, chunksize=300_000)
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
                    duration = duration.loc[valid]
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

                    hour_counts = chunk["started_at"].dt.floor("h").value_counts()
                    hourly_counter.update(hour_counts.to_dict())
                    station_counter.update(
                        chunk["start_station_name"].dropna().astype(str)
                    )
                    member_counter.update(
                        chunk["member_casual"].fillna("unknown").astype(str)
                    )
                    bike_counter.update(
                        chunk["rideable_type"].fillna("unknown").astype(str)
                    )
                    duration_minutes.append(duration.to_numpy(dtype=float))

    if not hourly_counter:
        raise RuntimeError("No valid trips found after filtering.")

    full_hours = pd.date_range("2024-01-01 00:00:00", "2024-01-31 23:00:00", freq="h")
    hourly = pd.DataFrame({"hour": full_hours})
    hourly["rides"] = hourly["hour"].map(
        lambda value: int(hourly_counter.get(value, 0))
    )
    hourly["date"] = hourly["hour"].dt.date.astype(str)
    hourly["day_name"] = hourly["hour"].dt.day_name()
    hourly["day_of_week"] = hourly["hour"].dt.dayofweek
    hourly["hour_of_day"] = hourly["hour"].dt.hour
    hourly["is_weekend"] = hourly["day_of_week"].isin([5, 6])
    hourly["is_federal_holiday"] = hourly["date"].isin(["2024-01-01", "2024-01-15"])

    durations = np.concatenate(duration_minutes)
    summary = {
        "dataset_month": DATASET_MONTH,
        "source_url": DATA_URL,
        "rows_total": int(rows_total),
        "rows_valid": int(rows_valid),
        "valid_rate": float(rows_valid / rows_total if rows_total else 0),
        "first_started_at": str(first_started),
        "last_started_at": str(last_started),
        "hourly_points": int(len(hourly)),
        "total_rides": int(hourly["rides"].sum()),
        "average_hourly_rides": float(hourly["rides"].mean()),
        "median_hourly_rides": float(hourly["rides"].median()),
        "peak_hour": str(hourly.loc[hourly["rides"].idxmax(), "hour"]),
        "peak_hour_rides": int(hourly["rides"].max()),
        "average_daily_rides": float(hourly.groupby("date")["rides"].sum().mean()),
        "duration_median_minutes": float(np.median(durations)),
        "duration_p90_minutes": float(np.percentile(durations, 90)),
        "duration_p99_minutes": float(np.percentile(durations, 99)),
    }

    top_stations = pd.DataFrame(
        station_counter.most_common(15), columns=["station", "rides"]
    )
    top_stations["share_of_valid_trips"] = top_stations["rides"] / rows_valid
    member_mix = counter_to_share_frame(member_counter, "rider_type", rows_valid)
    bike_mix = counter_to_share_frame(bike_counter, "bike_type", rows_valid)
    return summary, hourly, top_stations, member_mix, bike_mix


def counter_to_share_frame(
    counter: Counter[str], label: str, denominator: int
) -> pd.DataFrame:
    """Convert counted categories into a ride-share table."""
    frame = pd.DataFrame(counter.most_common(), columns=[label, "rides"])
    frame["share"] = frame["rides"] / denominator if denominator else 0
    return frame


def fetch_weather() -> pd.DataFrame | None:
    """Fetch cached or remote Open-Meteo hourly weather context for NYC."""
    if WEATHER_CSV.exists():
        return pd.read_csv(WEATHER_CSV, parse_dates=["hour"])

    params = {
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "hourly": "temperature_2m,precipitation,snowfall,wind_speed_10m",
        "timezone": "America/New_York",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(
        params
    )
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "codex-time-series-profile/1.0"}
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.load(response)
    except Exception as exc:
        print(f"Weather download skipped: {exc}")
        return None

    hourly_payload = payload.get("hourly", {})
    if not hourly_payload or "time" not in hourly_payload:
        return None

    weather = pd.DataFrame(
        {
            "hour": pd.to_datetime(hourly_payload["time"]),
            "temperature_c": hourly_payload.get("temperature_2m"),
            "precipitation_mm": hourly_payload.get("precipitation"),
            "snowfall_cm": hourly_payload.get("snowfall"),
            "wind_speed_kmh": hourly_payload.get("wind_speed_10m"),
        }
    )
    weather.to_csv(WEATHER_CSV, index=False)
    return weather


def build_seasonality(hourly: pd.DataFrame) -> pd.DataFrame:
    """Calculate average ride demand by weekday and hour."""
    seasonality = (
        hourly.groupby(["day_of_week", "day_name", "hour_of_day"], as_index=False)[
            "rides"
        ]
        .mean()
        .sort_values(["day_of_week", "hour_of_day"])
    )
    return seasonality


def detect_anomalies(hourly: pd.DataFrame) -> pd.DataFrame:
    """Rank hourly demand anomalies using a robust seasonal profile."""
    frame = hourly.copy()
    grouped = frame.groupby(["day_of_week", "hour_of_day"])["rides"]
    profile = grouped.transform("median")
    mad = grouped.transform(
        lambda values: np.median(np.abs(values - np.median(values)))
    )
    frame["expected_profile_rides"] = profile
    frame["robust_z"] = 0.6745 * (frame["rides"] - profile) / mad.replace(0, np.nan)
    frame["robust_z"] = frame["robust_z"].replace([np.inf, -np.inf], np.nan).fillna(0)
    frame["absolute_gap"] = frame["rides"] - frame["expected_profile_rides"]
    anomalies = frame.reindex(
        frame["robust_z"].abs().sort_values(ascending=False).index
    )
    columns = [
        "hour",
        "rides",
        "expected_profile_rides",
        "absolute_gap",
        "robust_z",
        "day_name",
        "hour_of_day",
    ]
    return anomalies[columns].head(20).reset_index(drop=True)


def run_forecast_backtest(
    hourly: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, str, tuple[float, float]]:
    """Evaluate simple January holdout forecasts and prediction bands."""
    frame = hourly[["hour", "rides", "day_of_week", "hour_of_day"]].copy()
    test_start = pd.Timestamp("2024-01-25 00:00:00")
    train_mask = frame["hour"] < test_start
    test_mask = frame["hour"] >= test_start

    train = frame.loc[train_mask].copy()
    profile = train.groupby(["day_of_week", "hour_of_day"])["rides"].mean()
    global_mean = train["rides"].mean()

    scored = frame.copy()
    scored["previous_day"] = scored["rides"].shift(24)
    scored["previous_week"] = scored["rides"].shift(24 * 7)
    scored["calendar_profile"] = [
        float(profile.get((row.day_of_week, row.hour_of_day), global_mean))
        for row in scored.itertuples(index=False)
    ]
    scored.loc[train_mask, ["previous_day", "previous_week", "calendar_profile"]] = (
        np.nan
    )

    metric_rows = []
    for model in ["previous_day", "previous_week", "calendar_profile"]:
        part = scored.loc[test_mask, ["rides", model]].dropna()
        metric_rows.append(score_model(model, part["rides"], part[model]))
    results = pd.DataFrame(metric_rows).sort_values("mae").reset_index(drop=True)
    best_model = str(results.loc[0, "model"])

    train_residuals = frame["rides"] - frame["rides"].shift(24 * 7)
    train_residuals = train_residuals.loc[train_mask].dropna()
    lower, upper = (
        np.quantile(train_residuals, [0.1, 0.9])
        if len(train_residuals)
        else (-0.0, 0.0)
    )
    scored["forecast"] = scored[best_model]
    scored["forecast_lower"] = np.maximum(0, scored["forecast"] + lower)
    scored["forecast_upper"] = np.maximum(0, scored["forecast"] + upper)
    return (
        results,
        scored.loc[test_mask].reset_index(drop=True),
        best_model,
        (float(lower), float(upper)),
    )


def score_model(model: str, actual: pd.Series, forecast: pd.Series) -> dict:
    """Score one forecast with portfolio-friendly error metrics."""
    error = forecast - actual
    abs_error = error.abs()
    denom = actual.replace(0, np.nan)
    return {
        "model": model,
        "n": int(len(actual)),
        "mae": float(abs_error.mean()),
        "rmse": float(math.sqrt((error**2).mean())),
        "mape": float((abs_error / denom).dropna().mean()),
        "mean_actual": float(actual.mean()),
    }


def use_chart_theme() -> None:
    """Apply the shared visual theme for Matplotlib charts."""
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
    fig,
    ax,
    title: str,
    subtitle: str,
    *,
    title_width: int = 78,
    subtitle_width: int = 112,
) -> None:
    """Add a consistent title and subtitle treatment to a chart."""
    title = textwrap.fill(str(title).strip(), width=title_width, break_long_words=False)
    subtitle = textwrap.fill(
        str(subtitle).strip(), width=subtitle_width, break_long_words=False
    )
    if not title or not subtitle:
        raise ValueError("Every chart needs a title and subtitle.")
    title_lines = title.count("\n") + 1
    subtitle_lines = subtitle.count("\n") + 1
    ax.set_title("")
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
        linespacing=1.08,
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


def format_date_axis(ax, *, max_ticks: int = 7) -> None:
    """Format an x-axis for compact hourly or daily dates."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.offsetText.set_visible(False)
    ax.tick_params(axis="x", labelrotation=0)


def save_chart(fig, name: str) -> Path:
    """Save a chart image to the project chart directory."""
    path = CHART_DIR / name
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def build_charts(
    hourly: pd.DataFrame,
    seasonality: pd.DataFrame,
    top_stations: pd.DataFrame,
    forecast_scored: pd.DataFrame,
    best_model: str,
    interval: tuple[float, float],
) -> dict[str, Path]:
    """Render the profile, seasonality, station, and forecast charts."""
    use_chart_theme()
    chart_paths: dict[str, Path] = {}

    daily = hourly.groupby("date", as_index=False)["rides"].sum()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["rolling_7d"] = daily["rides"].rolling(7, min_periods=3).mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    family = COLOR_FAMILIES["blue"]
    sns.lineplot(
        data=daily,
        x="date",
        y="rides",
        ax=ax,
        color=family["base"],
        linewidth=1.2,
        label="Daily rides",
    )
    sns.lineplot(
        data=daily,
        x="date",
        y="rolling_7d",
        ax=ax,
        color=family["dark"],
        linewidth=1.2,
        label="7-day average",
    )
    ax.set_xlabel("")
    ax.set_ylabel("Rides")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1000:.0f}k"))
    format_date_axis(ax)
    add_chart_header(
        fig,
        ax,
        "Daily demand moved with weekday rhythm",
        "Citi Bike trip starts, January 2024. The 7-day average smooths daily volatility.",
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        frameon=False,
        ncol=2,
        borderaxespad=0,
    )
    chart_paths["daily_demand"] = save_chart(fig, "daily_demand.png")

    heatmap = seasonality.pivot(index="day_name", columns="hour_of_day", values="rides")
    ordered_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    heatmap = heatmap.reindex(ordered_days)
    fig, ax = plt.subplots(figsize=(11, 5.8))
    cmap = sns.blend_palette(
        [
            TOKENS["panel"],
            COLOR_FAMILIES["blue"]["xlight"],
            COLOR_FAMILIES["blue"]["light"],
            COLOR_FAMILIES["blue"]["base"],
        ],
        as_cmap=True,
    )
    sns.heatmap(
        heatmap,
        ax=ax,
        cmap=cmap,
        linewidths=0.5,
        linecolor=TOKENS["panel"],
        cbar_kws={"label": "Avg. rides"},
    )
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("")
    add_chart_header(
        fig,
        ax,
        "The commute signature is visible by hour and weekday",
        "Average hourly starts by day of week and hour. Darker cells mark stronger demand.",
    )
    chart_paths["seasonality_heatmap"] = save_chart(fig, "seasonality_heatmap.png")

    forecast_plot = forecast_scored.copy()
    fig, ax = plt.subplots(figsize=(11, 5.4))
    forecast_family = COLOR_FAMILIES["orange"]
    ax.fill_between(
        forecast_plot["hour"],
        forecast_plot["forecast_lower"],
        forecast_plot["forecast_upper"],
        color=forecast_family["xlight"],
        alpha=0.95,
        label="80% residual band",
    )
    sns.lineplot(
        data=forecast_plot,
        x="hour",
        y="rides",
        ax=ax,
        color=COLOR_FAMILIES["blue"]["base"],
        linewidth=1.0,
        label="Actual",
    )
    sns.lineplot(
        data=forecast_plot,
        x="hour",
        y="forecast",
        ax=ax,
        color=forecast_family["base"],
        linewidth=1.0,
        linestyle="--",
        label=best_model.replace("_", " ").title(),
    )
    ax.set_xlabel("")
    ax.set_ylabel("Hourly rides")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1000:.1f}k"))
    format_date_axis(ax)
    add_chart_header(
        fig,
        ax,
        "A simple seasonal baseline creates a useful forecast reference",
        f"Holdout: Jan. 25-31, 2024. Band uses 10th-90th percentile training residuals: {interval[0]:+.0f} to {interval[1]:+.0f} rides.",
    )
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        frameon=False,
        ncol=3,
        borderaxespad=0,
    )
    chart_paths["forecast_backtest"] = save_chart(fig, "forecast_backtest.png")

    station_plot = top_stations.head(10).sort_values("rides", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5.6))
    station_family = COLOR_FAMILIES["olive"]
    palette = {
        station: station_family[["base", "light", "xlight", "open", "base"][i % 5]]
        for i, station in enumerate(station_plot["station"])
    }
    sns.barplot(
        data=station_plot,
        x="rides",
        y="station",
        hue="station",
        palette=palette,
        legend=False,
        dodge=False,
        ax=ax,
        edgecolor=station_family["dark"],
        linewidth=1.0,
    )
    ax.set_xlabel("Trip starts")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x / 1000:.0f}k"))
    add_chart_header(
        fig,
        ax,
        "A small station set carries a visible share of trip starts",
        "Top 10 start stations in January 2024. Ranked bars are better than a table for concentration.",
    )
    chart_paths["top_stations"] = save_chart(fig, "top_stations.png")

    return chart_paths


def write_outputs(
    *,
    summary: dict,
    hourly: pd.DataFrame,
    top_stations: pd.DataFrame,
    member_mix: pd.DataFrame,
    bike_mix: pd.DataFrame,
    seasonality: pd.DataFrame,
    anomalies: pd.DataFrame,
    forecast_results: pd.DataFrame,
    forecast_scored: pd.DataFrame,
    best_model: str,
    chart_paths: dict[str, Path],
    weather_loaded: bool,
) -> None:
    """Write CSV, JSON, and HTML outputs for the profile project."""
    hourly.to_csv(OUT_DIR / "hourly_profile.csv", index=False)
    top_stations.to_csv(OUT_DIR / "top_stations.csv", index=False)
    member_mix.to_csv(OUT_DIR / "member_mix.csv", index=False)
    bike_mix.to_csv(OUT_DIR / "bike_mix.csv", index=False)
    seasonality.to_csv(OUT_DIR / "seasonality_profile.csv", index=False)
    anomalies.to_csv(OUT_DIR / "anomaly_hours.csv", index=False)
    forecast_results.to_csv(OUT_DIR / "forecast_backtest_metrics.csv", index=False)
    forecast_scored.to_csv(OUT_DIR / "forecast_backtest_scored.csv", index=False)

    profile = build_report_payload(
        summary=summary,
        hourly=hourly,
        top_stations=top_stations,
        member_mix=member_mix,
        bike_mix=bike_mix,
        anomalies=anomalies,
        forecast_results=forecast_results,
        best_model=best_model,
        weather_loaded=weather_loaded,
    )
    with (OUT_DIR / "profile_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2)

    html_report = render_report(profile, chart_paths)
    (OUT_DIR / "report.html").write_text(html_report, encoding="utf-8")

    print(json.dumps(profile, indent=2))
    print(f"Report written to {OUT_DIR / 'report.html'}")


def build_report_payload(
    *,
    summary: dict,
    hourly: pd.DataFrame,
    top_stations: pd.DataFrame,
    member_mix: pd.DataFrame,
    bike_mix: pd.DataFrame,
    anomalies: pd.DataFrame,
    forecast_results: pd.DataFrame,
    best_model: str,
    weather_loaded: bool,
) -> dict:
    """Assemble a JSON-safe report payload for the HTML summary."""
    daily = hourly.groupby("date", as_index=False)["rides"].sum()
    day_peaks = daily.sort_values("rides", ascending=False).head(3)
    weekend_avg = hourly.loc[hourly["is_weekend"], "rides"].mean()
    weekday_avg = hourly.loc[~hourly["is_weekend"], "rides"].mean()
    rush_hours = hourly.loc[
        hourly["hour_of_day"].isin([7, 8, 9, 16, 17, 18]), "rides"
    ].mean()
    off_hours = hourly.loc[
        ~hourly["hour_of_day"].isin([7, 8, 9, 16, 17, 18]), "rides"
    ].mean()

    weather_note = None
    if weather_loaded:
        weather_cols = [
            "temperature_c",
            "precipitation_mm",
            "snowfall_cm",
            "wind_speed_kmh",
        ]
        correlations = {
            col: float(hourly[["rides", col]].dropna().corr().iloc[0, 1])
            for col in weather_cols
            if col in hourly.columns and hourly[col].notna().any()
        }
        weather_note = correlations

    payload = {
        "title": "Citi Bike Time Series Profile",
        "summary": summary,
        "top_days": day_peaks.to_dict(orient="records"),
        "weekday_avg_hourly": float(weekday_avg),
        "weekend_avg_hourly": float(weekend_avg),
        "weekend_vs_weekday_ratio": float(
            weekend_avg / weekday_avg if weekday_avg else 0
        ),
        "rush_hour_avg": float(rush_hours),
        "off_hour_avg": float(off_hours),
        "rush_vs_off_hour_ratio": float(rush_hours / off_hours if off_hours else 0),
        "best_model": best_model,
        "forecast_results": forecast_results.to_dict(orient="records"),
        "top_stations": top_stations.head(10).to_dict(orient="records"),
        "member_mix": member_mix.to_dict(orient="records"),
        "bike_mix": bike_mix.to_dict(orient="records"),
        "anomalies": anomalies.head(10).to_dict(orient="records"),
        "weather_loaded": weather_loaded,
        "weather_correlations": weather_note,
    }
    return make_json_safe(payload)


def make_json_safe(value):
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


def render_report(profile: dict, chart_paths: dict[str, Path]) -> str:
    """Render the January profile as a standalone HTML report."""
    summary = profile["summary"]
    forecast_rows = profile["forecast_results"]
    best = forecast_rows[0]
    source_date = "January 2024"
    weather_phrase = (
        "Open-Meteo hourly weather joined successfully for optional context."
        if profile["weather_loaded"]
        else "Weather enrichment was skipped, so this profile relies on trip history only."
    )

    chart_img = {
        key: html.escape(str(path.relative_to(OUT_DIR)).replace("\\", "/"))
        for key, path in chart_paths.items()
    }
    top_anomaly = profile["anomalies"][0]
    top_station = profile["top_stations"][0]
    member_rows = table_rows(profile["member_mix"], ["rider_type", "rides", "share"])
    bike_rows = table_rows(profile["bike_mix"], ["bike_type", "rides", "share"])
    forecast_table = forecast_rows_html(forecast_rows)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(profile["title"])}</title>
  <style>
    :root {{
      --surface: #fcfcfd;
      --paper: #ffffff;
      --ink: #1f2430;
      --muted: #626b7c;
      --line: #dce1ec;
      --blue: #5477c4;
      --blue-soft: #eaf1fe;
      --orange: #cc6f47;
      --orange-soft: #ffedde;
      --olive: #71b436;
      --olive-soft: #eef8e5;
    }}
    body {{
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font-family: Aptos, Inter, "Segoe UI", Arial, sans-serif;
    }}
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 40px 22px 72px;
    }}
    header, section {{ margin-bottom: 36px; }}
    h1 {{
      margin: 0;
      font-size: clamp(34px, 5vw, 56px);
      line-height: 1.03;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 24px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 20px 0 8px;
      font-size: 17px;
      line-height: 1.25;
    }}
    p, li {{
      line-height: 1.58;
      font-size: 16px;
    }}
    .meta {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 14px;
    }}
    .executive-summary-box {{
      padding: 22px 24px;
      background: linear-gradient(180deg, #ffffff 0%, #f7f9fd 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 14px 32px rgba(31, 36, 48, 0.06);
    }}
    .executive-summary-box ul {{ margin: 0; padding-left: 22px; }}
    .executive-summary-box li + li {{ margin-top: 10px; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .kpi {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 14px 16px;
    }}
    .kpi strong {{
      display: block;
      font-size: 24px;
      line-height: 1.05;
      margin-bottom: 4px;
    }}
    .kpi span {{
      color: var(--muted);
      font-size: 13px;
    }}
    figure {{
      margin: 18px 0 6px;
      padding: 0;
    }}
    figure img {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
    }}
    figcaption {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
      line-height: 1.45;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      margin: 14px 0;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 14px;
    }}
    th {{
      color: var(--muted);
      font-weight: 650;
      background: #f8f9fc;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .callout {{
      border-left: 4px solid var(--orange);
      background: var(--orange-soft);
      padding: 14px 16px;
      border-radius: 8px;
    }}
    .source-note {{
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 760px) {{
      main {{ padding: 28px 16px 56px; }}
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpis {{ grid-template-columns: 1fr; }}
      th, td {{ font-size: 13px; }}
    }}
  </style>
</head>
<body>
  <main data-report-audience="product stakeholders">
    <header data-contract-section="title">
      <h1>{html.escape(profile["title"])}</h1>
      <p class="meta">Trip-start demand profile for Citi Bike, {source_date}. Source: Citi Bike public trip-history archive.</p>
    </header>

    <section class="executive-summary-box" data-contract-section="executive-summary">
      <h2>Executive Summary</h2>
      <ul>
        <li><strong>The dataset is portfolio-scale but still practical.</strong> The profile uses {format_int(summary["rows_valid"])} valid rides across {format_int(summary["hourly_points"])} hourly observations after filtering implausible trip durations.</li>
        <li><strong>The series has a strong human rhythm.</strong> Rush-hour demand averaged {format_int(profile["rush_hour_avg"])} starts per hour, {profile["rush_vs_off_hour_ratio"]:.1f}x off-hour demand, and the weekday/hour heatmap exposes commute-heavy peaks.</li>
        <li><strong>A basic seasonal forecast is already useful.</strong> The best baseline on the Jan. 25-31 holdout was <code>{html.escape(best["model"])}</code>, with MAE of {format_int(best["mae"])} rides per hour and RMSE of {format_int(best["rmse"])}.</li>
      </ul>
    </section>

    <section data-contract-section="key-findings">
      <h2>Demand shape is the main story, not the model name</h2>
      <p><strong>A strong showcase should first prove the temporal structure.</strong> This month has enough daily and hourly observations to show trend, weekday rhythm, commute peaks, holiday effects, station concentration, and forecast error. That gives the project a real analytical spine before introducing heavier forecasting methods.</p>
      <div class="kpis">
        <div class="kpi"><strong>{format_int(summary["total_rides"])}</strong><span>Total rides</span></div>
        <div class="kpi"><strong>{format_int(summary["average_daily_rides"])}</strong><span>Avg. daily rides</span></div>
        <div class="kpi"><strong>{format_int(summary["peak_hour_rides"])}</strong><span>Peak hourly rides</span></div>
        <div class="kpi"><strong>{summary["duration_median_minutes"]:.1f} min</strong><span>Median duration</span></div>
      </div>
      <figure>
        <img src="{chart_img["daily_demand"]}" alt="Daily Citi Bike demand line chart">
        <figcaption>Daily trip starts and 7-day average for January 2024.</figcaption>
      </figure>
    </section>

    <section data-contract-section="key-findings">
      <h2>Seasonality is visible at commuter granularity</h2>
      <p><strong>The weekday/hour profile is the most useful first feature view.</strong> It shows whether the model should expect a commute pattern, leisure pattern, or irregular event-driven pattern. Here, the rush-hour average is materially higher than off-hours, and weekends average {profile["weekend_vs_weekday_ratio"]:.2f}x weekday hourly volume.</p>
      <figure>
        <img src="{chart_img["seasonality_heatmap"]}" alt="Heatmap of Citi Bike average rides by day of week and hour">
        <figcaption>Average hourly trip starts by day of week and hour of day. This becomes the first seasonal baseline and the feature map for richer models.</figcaption>
      </figure>
    </section>

    <section data-contract-section="key-findings">
      <h2>The simple backtest creates a credible benchmark</h2>
      <p><strong>The right baseline prevents model theater.</strong> A time-series showcase should compare a proposed method against naive alternatives. The holdout below uses the final seven days of January and compares previous-day, previous-week, and calendar-profile baselines.</p>
      {forecast_table}
      <figure>
        <img src="{chart_img["forecast_backtest"]}" alt="Forecast backtest line chart">
        <figcaption>Actual hourly trip starts versus the best baseline forecast on the Jan. 25-31 holdout.</figcaption>
      </figure>
    </section>

    <section data-contract-section="key-findings">
      <h2>Stations and anomalies create the portfolio hooks</h2>
      <p><strong>Operational texture makes the showcase feel real.</strong> The top start station was {html.escape(top_station["station"])}, with {format_int(top_station["rides"])} starts. The largest anomaly flagged in this pass occurred at {html.escape(str(top_anomaly["hour"]))}, when actual starts differed from the weekday/hour profile by {format_int(top_anomaly["absolute_gap"])} rides.</p>
      <figure>
        <img src="{chart_img["top_stations"]}" alt="Ranked bar chart of top Citi Bike start stations">
        <figcaption>Top start stations by trip starts. Station-level extensions can turn this from one aggregate series into a multi-series forecasting problem.</figcaption>
      </figure>
      <h3>Rider and bike mix</h3>
      <table>
        <thead><tr><th>Rider type</th><th>Rides</th><th>Share</th></tr></thead>
        <tbody>{member_rows}</tbody>
      </table>
      <table>
        <thead><tr><th>Bike type</th><th>Rides</th><th>Share</th></tr></thead>
        <tbody>{bike_rows}</tbody>
      </table>
    </section>

    <section data-contract-section="recommended-next-steps">
      <h2>Recommended Next Steps</h2>
      <ol>
        <li>Use the full-2024 proof layer as the aggregate benchmark for yearly seasonality and rolling validation.</li>
        <li>Add station-cluster forecasts for the top stations or neighborhoods. That turns the project into a practical allocation problem.</li>
        <li>Add weather, event, or stronger model features only after they beat previous-week and calendar-lag benchmarks in rolling validation.</li>
      </ol>
    </section>

    <section data-contract-section="further-questions">
      <h2>Further Questions</h2>
      <p>Which business decision should the forecast serve: staffing, rebalancing, rider communications, station planning, or anomaly alerting? The answer determines the forecast horizon, error metric, and acceptable tradeoff between aggregate accuracy and station-level specificity.</p>
    </section>

    <section data-contract-section="caveats-and-assumptions">
      <h2>Caveats and Assumptions</h2>
      <div class="callout">
        <p>This is a first-pass profile on one winter month, not a production forecast. It intentionally emphasizes clean temporal profiling and transparent baselines. {html.escape(weather_phrase)} The companion full-2024 proof layer extends aggregate validation across multiple rolling holdout windows.</p>
      </div>
      <p class="source-note">Public sources used: Citi Bike trip history archive and, when available, Open-Meteo historical weather. Generated outputs include hourly profiles, backtest metrics, anomaly tables, and chart PNGs in this folder.</p>
    </section>
  </main>
</body>
</html>
"""


def table_rows(rows: list[dict], keys: list[str]) -> str:
    """Render dictionaries as HTML table rows for selected keys."""
    html_rows = []
    for row in rows:
        cells = []
        for key in keys:
            value = row.get(key, "")
            if isinstance(value, float) and key == "share":
                text = f"{value:.1%}"
            elif isinstance(value, float):
                text = f"{value:,.1f}"
            elif isinstance(value, int):
                text = format_int(value)
            else:
                text = str(value)
            cells.append(f"<td>{html.escape(text)}</td>")
        html_rows.append("<tr>" + "".join(cells) + "</tr>")
    return "\n".join(html_rows)


def forecast_rows_html(rows: list[dict]) -> str:
    """Render forecast metric rows as HTML table markup."""
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td><code>{html.escape(str(row['model']))}</code></td>"
            f"<td>{format_int(row['mae'])}</td>"
            f"<td>{format_int(row['rmse'])}</td>"
            f"<td>{row['mape']:.1%}</td>"
            "</tr>"
        )
    return (
        "<table>"
        "<thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody>"
        "</table>"
    )


def format_int(value: float | int) -> str:
    """Format a numeric value as a rounded integer string."""
    return f"{float(value):,.0f}"


if __name__ == "__main__":
    main()
