"""Build the reviewer-facing time-series showcase from generated hourly outputs.

This companion script intentionally works from `outputs/hourly_profile.csv`
instead of the raw Citi Bike archive. The raw-data pipeline owns extraction and
aggregation; this script owns the portfolio proof layer: lag structure,
rolling-origin validation, residual diagnostics, and a polished HTML handoff.
"""

from __future__ import annotations

import html
import math
import textwrap
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
OUT_DIR = ROOT / "outputs"
CHART_DIR = OUT_DIR / "charts"

HOURLY_CSV = OUT_DIR / "hourly_profile.csv"

MODEL_LABELS = {
    "previous_day": "Previous day",
    "previous_week": "Previous week",
    "hour_of_day_profile": "Hour-of-day profile",
    "weekday_hour_profile": "Weekday/hour profile",
}

CHART_CAPTIONS = {
    "autocorrelation_profile.png": (
        "Daily and weekly peaks make the lag structure visible before any model is trained."
    ),
    "lag_feature_correlations.png": (
        "Lagged demand and rolling means screen as stronger candidates than raw weather fields."
    ),
    "rolling_backtest_mae.png": (
        "Repeated forecast origins make the benchmark harder to hand-wave than a single split."
    ),
    "decomposition_proxy.png": (
        "The trend and weekday/hour expected line separate level, seasonality, and residual movement."
    ),
    "seasonal_residual_distribution.png": (
        "Residual spread frames anomaly candidates without pretending to explain root cause."
    ),
}

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
    "xlight": "#F4F5F7",
    "light": "#E2E5EA",
    "base": "#C5CAD3",
    "mid": "#7A828F",
    "dark": "#464C55",
}

COLOR_FAMILIES = {
    "blue": {
        "xlight": "#EAF1FE",
        "light": "#CEDFFE",
        "base": "#A3BEFA",
        "mid": "#5477C4",
        "dark": "#2E4780",
    },
    "gold": {
        "xlight": "#FFF4C2",
        "light": "#FFEA8F",
        "base": "#FFE15B",
        "mid": "#B8A037",
        "dark": "#736422",
    },
    "orange": {
        "xlight": "#FFEDDE",
        "light": "#FFBDA1",
        "base": "#F0986E",
        "mid": "#CC6F47",
        "dark": "#804126",
    },
    "olive": {
        "xlight": "#D8ECBD",
        "light": "#BEEB96",
        "base": "#A3D576",
        "mid": "#71B436",
        "dark": "#386411",
    },
    "pink": {
        "xlight": "#FCDAD6",
        "light": "#F5BACC",
        "base": "#F390CA",
        "mid": "#BD569B",
        "dark": "#8A3A6F",
    },
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
    fig: plt.Figure,
    ax: plt.Axes,
    title: str,
    subtitle: str,
    *,
    title_width: int = 80,
    subtitle_width: int = 112,
) -> None:
    """Add a consistent title and subtitle treatment to a chart."""
    title = textwrap.fill(str(title).strip(), width=title_width, break_long_words=False)
    subtitle = textwrap.fill(
        str(subtitle).strip(), width=subtitle_width, break_long_words=False
    )
    if not title or not subtitle:
        raise ValueError("Every shipped chart needs a title and subtitle.")

    title_lines = title.count("\n") + 1
    subtitle_lines = subtitle.count("\n") + 1
    ax.set_title("")
    fig.subplots_adjust(
        top=max(0.60, 0.86 - 0.045 * (title_lines - 1) - 0.032 * (subtitle_lines - 1))
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


def format_date_axis(ax: plt.Axes, *, max_ticks: int = 7) -> None:
    """Format a chart x-axis for compact dates."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def save_chart(fig: plt.Figure, filename: str) -> Path:
    """Save a chart image to the project chart directory."""
    path = CHART_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def label_model(model: object) -> str:
    """Return a reader-friendly model label while preserving unknown names."""
    return MODEL_LABELS.get(str(model), str(model).replace("_", " ").title())


def fmt_number(value: object, *, digits: int = 0) -> str:
    """Format report numbers without leaking raw floating-point noise."""
    if pd.isna(value):
        return "n/a"
    number = float(value)
    if digits == 0:
        return f"{number:,.0f}"
    return f"{number:,.{digits}f}"


def fmt_percent(value: object, *, digits: int = 1) -> str:
    """Format a decimal ratio as a percentage string."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def load_hourly_profile() -> pd.DataFrame:
    """Load and validate the generated hourly Citi Bike profile."""
    if not HOURLY_CSV.exists():
        raise FileNotFoundError(
            f"Missing {HOURLY_CSV}. Run citibike_time_series_profile.py first."
        )

    hourly = pd.read_csv(HOURLY_CSV, parse_dates=["hour", "date"])
    required = {
        "hour",
        "rides",
        "day_of_week",
        "hour_of_day",
        "temperature_c",
        "precipitation_mm",
        "snowfall_cm",
        "wind_speed_kmh",
    }
    missing = required.difference(hourly.columns)
    if missing:
        raise ValueError(
            f"hourly_profile.csv is missing required columns: {sorted(missing)}"
        )

    hourly = hourly.sort_values("hour").reset_index(drop=True)
    hourly["rides"] = hourly["rides"].astype(float)
    return hourly


def validate_hourly_index(hourly: pd.DataFrame) -> dict[str, int | str]:
    """Check hourly continuity and duplicate timestamps in the profile."""
    expected = pd.date_range(hourly["hour"].min(), hourly["hour"].max(), freq="h")
    observed = pd.DatetimeIndex(hourly["hour"])
    missing_hours = expected.difference(observed)
    duplicate_hours = int(hourly["hour"].duplicated().sum())
    return {
        "first_hour": str(hourly["hour"].min()),
        "last_hour": str(hourly["hour"].max()),
        "hourly_observations": int(len(hourly)),
        "expected_hourly_observations": int(len(expected)),
        "missing_hours": int(len(missing_hours)),
        "duplicate_hours": duplicate_hours,
    }


def safe_mape(actual: pd.Series, forecast: pd.Series) -> float:
    """Calculate MAPE while ignoring zero-actual rows."""
    mask = actual != 0
    if not mask.any():
        return float("nan")
    return float((actual[mask] - forecast[mask]).abs().div(actual[mask].abs()).mean())


def score_forecast(actual: pd.Series, forecast: pd.Series) -> dict[str, float]:
    """Calculate forecast accuracy metrics after dropping missing pairs."""
    scored = pd.DataFrame({"actual": actual, "forecast": forecast}).dropna()
    if scored.empty:
        return {"n": 0, "mae": float("nan"), "rmse": float("nan"), "mape": float("nan")}

    error = scored["actual"] - scored["forecast"]
    return {
        "n": int(len(scored)),
        "mae": float(error.abs().mean()),
        "rmse": float(math.sqrt((error**2).mean())),
        "mape": safe_mape(scored["actual"], scored["forecast"]),
    }


def build_autocorrelation_profile(
    hourly: pd.DataFrame, max_lag: int = 168
) -> pd.DataFrame:
    """Build autocorrelation values across candidate hourly lags."""
    rides = hourly["rides"]
    rows = []
    for lag in range(1, max_lag + 1):
        rows.append(
            {
                "lag_hours": lag,
                "autocorrelation": float(rides.autocorr(lag=lag)),
                "lag_family": classify_lag(lag),
            }
        )
    return pd.DataFrame(rows)


def classify_lag(lag: int) -> str:
    """Classify a lag into short, daily, weekly, or other families."""
    if lag in {1, 2, 3, 6, 12}:
        return "short lag"
    if lag % 168 == 0:
        return "weekly seasonal lag"
    if lag % 24 == 0:
        return "daily seasonal lag"
    return "other lag"


def build_lag_feature_correlations(hourly: pd.DataFrame) -> pd.DataFrame:
    """Rank lag, rolling, and weather features by demand correlation."""
    rides = hourly["rides"]
    feature_series: dict[str, tuple[str, pd.Series]] = {
        "lag_1h": ("short-memory lag", rides.shift(1)),
        "lag_2h": ("short-memory lag", rides.shift(2)),
        "lag_3h": ("short-memory lag", rides.shift(3)),
        "lag_6h": ("same-day lag", rides.shift(6)),
        "lag_12h": ("same-day lag", rides.shift(12)),
        "lag_24h": ("daily seasonal lag", rides.shift(24)),
        "lag_48h": ("daily seasonal lag", rides.shift(48)),
        "lag_72h": ("daily seasonal lag", rides.shift(72)),
        "lag_168h": ("weekly seasonal lag", rides.shift(168)),
        # Shift before rolling so the feature uses only values known before the
        # current hour. That keeps the screening table aligned with forecast use.
        "rolling_3h_mean": ("rolling feature", rides.shift(1).rolling(3).mean()),
        "rolling_6h_mean": ("rolling feature", rides.shift(1).rolling(6).mean()),
        "rolling_12h_mean": ("rolling feature", rides.shift(1).rolling(12).mean()),
        "rolling_24h_mean": ("rolling feature", rides.shift(1).rolling(24).mean()),
        "rolling_168h_mean": ("rolling feature", rides.shift(1).rolling(168).mean()),
        "temperature_c": ("exogenous weather", hourly["temperature_c"]),
        "precipitation_mm": ("exogenous weather", hourly["precipitation_mm"]),
        "snowfall_cm": ("exogenous weather", hourly["snowfall_cm"]),
        "wind_speed_kmh": ("exogenous weather", hourly["wind_speed_kmh"]),
    }

    rows = []
    for feature, (concept, values) in feature_series.items():
        corr = rides.corr(values)
        rows.append(
            {
                "feature": feature,
                "concept": concept,
                "correlation_with_rides": float(corr) if pd.notna(corr) else np.nan,
                "abs_correlation": float(abs(corr)) if pd.notna(corr) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("abs_correlation", ascending=False)


def forecast_from_previous(
    hourly_by_hour: pd.Series, hours: pd.Series, lag: int
) -> pd.Series:
    """Forecast each test hour from a previous observed hour."""
    return pd.Series(
        [hourly_by_hour.get(hour - pd.Timedelta(hours=lag), np.nan) for hour in hours],
        index=hours.index,
        dtype=float,
    )


def forecast_from_hour_profile(train: pd.DataFrame, test: pd.DataFrame) -> pd.Series:
    """Use the expanding training average for the same hour of day."""
    hour_profile = train.groupby("hour_of_day")["rides"].mean()
    global_mean = float(train["rides"].mean())
    return test["hour_of_day"].map(hour_profile).fillna(global_mean).astype(float)


def forecast_from_calendar_profile(
    train: pd.DataFrame, test: pd.DataFrame
) -> pd.Series:
    """Use the expanding training average for the same weekday and hour."""
    calendar_profile = train.groupby(["day_of_week", "hour_of_day"])["rides"].mean()
    hour_profile = train.groupby("hour_of_day")["rides"].mean()
    global_mean = float(train["rides"].mean())
    forecasts = []
    for row in test.itertuples(index=False):
        key = (row.day_of_week, row.hour_of_day)
        forecasts.append(
            float(
                calendar_profile.get(
                    key, hour_profile.get(row.hour_of_day, global_mean)
                )
            )
        )
    return pd.Series(forecasts, index=test.index, dtype=float)


def build_rolling_backtests(
    hourly: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run leakage-safe daily 24-hour rolling-origin baseline backtests."""
    hourly_by_hour = hourly.set_index("hour")["rides"]
    first_origin = hourly["hour"].min() + pd.Timedelta(days=14)
    last_origin = hourly["hour"].max() - pd.Timedelta(hours=23)
    origins = pd.date_range(first_origin.normalize(), last_origin.normalize(), freq="D")
    scored_rows = []
    origin_rows = []

    for origin in origins:
        # This line is the leakage boundary: no forecast may use rows at or
        # after the origin, even when calculating calendar averages.
        train = hourly[hourly["hour"] < origin]
        test = hourly[
            (hourly["hour"] >= origin)
            & (hourly["hour"] < origin + pd.Timedelta(hours=24))
        ]
        if len(train) < 24 * 7 or len(test) != 24:
            continue

        model_forecasts = {
            "previous_day": forecast_from_previous(hourly_by_hour, test["hour"], 24),
            "previous_week": forecast_from_previous(hourly_by_hour, test["hour"], 168),
            "hour_of_day_profile": forecast_from_hour_profile(train, test),
            "weekday_hour_profile": forecast_from_calendar_profile(train, test),
        }

        for model, forecast in model_forecasts.items():
            scored = pd.DataFrame(
                {
                    "origin": origin,
                    "hour": test["hour"].to_numpy(),
                    "model": model,
                    "actual": test["rides"].to_numpy(),
                    "forecast": forecast.to_numpy(),
                }
            ).dropna()
            scored["error"] = scored["actual"] - scored["forecast"]
            scored["abs_error"] = scored["error"].abs()
            scored_rows.extend(scored.to_dict("records"))
            metrics = score_forecast(scored["actual"], scored["forecast"])
            origin_rows.append({"origin": origin, "model": model, **metrics})

    scored_df = pd.DataFrame(scored_rows)
    origin_metrics = pd.DataFrame(origin_rows)
    if scored_df.empty:
        aggregate_metrics = pd.DataFrame()
    else:
        aggregate_rows = []
        for model, part in scored_df.groupby("model"):
            metrics = score_forecast(part["actual"], part["forecast"])
            aggregate_rows.append(
                {
                    "model": model,
                    "origins": int(part["origin"].nunique()),
                    "holdout_hours": int(len(part)),
                    "mean_actual": float(part["actual"].mean()),
                    **metrics,
                }
            )
        aggregate_metrics = pd.DataFrame(aggregate_rows).sort_values("mae")

    return aggregate_metrics, origin_metrics, scored_df


def build_decomposition_components(hourly: pd.DataFrame) -> pd.DataFrame:
    """Create descriptive trend, seasonality, and residual columns.

    One month is too short for a serious annual STL decomposition, so this table
    is deliberately labeled as a proxy. It still helps reviewers see the
    time-series reasoning pattern behind trend and anomaly work.
    """
    components = hourly[
        ["hour", "rides", "day_of_week", "hour_of_day", "day_name", "is_weekend"]
    ].copy()
    components["trend_24h"] = (
        components["rides"].rolling(window=24, center=True, min_periods=12).mean()
    )
    components["trend_168h"] = (
        components["rides"].rolling(window=168, center=True, min_periods=72).mean()
    )

    seasonal_profile = components.groupby(["day_of_week", "hour_of_day"])[
        "rides"
    ].mean()
    components["seasonal_expected"] = [
        float(seasonal_profile.loc[(row.day_of_week, row.hour_of_day)])
        for row in components.itertuples(index=False)
    ]
    components["seasonal_component"] = (
        components["seasonal_expected"] - components["rides"].mean()
    )
    components["seasonal_residual"] = (
        components["rides"] - components["seasonal_expected"]
    )
    residual_median = components["seasonal_residual"].median()
    residual_mad = (components["seasonal_residual"] - residual_median).abs().median()
    scale = (
        1.4826 * residual_mad if residual_mad else components["seasonal_residual"].std()
    )
    components["residual_robust_z"] = (
        (components["seasonal_residual"] - residual_median) / scale if scale else np.nan
    )
    return components


def build_showcase_coverage() -> pd.DataFrame:
    """Build the reviewer-facing matrix of time-series concepts covered."""
    rows = [
        (
            "Regular time index",
            "hourly_profile.csv",
            "Implemented",
            "Shows hourly grain, complete panel, duplicate/missing-hour checks.",
            "Timestamps are parsed as timezone-naive in this version.",
        ),
        (
            "Resampling and aggregation",
            "citibike_time_series_profile.py",
            "Implemented",
            "Raw trips are transformed into hourly and daily demand measures.",
            "Only trip starts are modeled, not inventory or completions.",
        ),
        (
            "Calendar features",
            "hourly_profile.csv",
            "Implemented",
            "Weekday, weekend, hour-of-day, and holiday flags support interpretable seasonality.",
            "Holiday list is hand-scoped to January 2024.",
        ),
        (
            "Seasonality",
            "seasonality_profile.csv",
            "Implemented",
            "Weekday/hour profile demonstrates commute and weekend patterns.",
            "One winter month cannot prove stable annual seasonality.",
        ),
        (
            "Smoothing and trend",
            "decomposition_components.csv",
            "Implemented",
            "Rolling trend columns separate level from hourly volatility.",
            "This is a descriptive proxy, not formal STL decomposition.",
        ),
        (
            "Autocorrelation",
            "autocorrelation_profile.csv",
            "Implemented",
            "Lag correlations expose short-memory, daily, and weekly repetition.",
            "ACF is descriptive and should be retested on more months.",
        ),
        (
            "Lag features",
            "lag_feature_correlations.csv",
            "Implemented",
            "Candidate lags and rolling means are ranked before heavier modeling.",
            "Correlation does not imply out-of-sample lift.",
        ),
        (
            "Exogenous variables",
            "hourly_profile.csv",
            "Implemented",
            "Weather fields are joined at hourly grain and evaluated descriptively.",
            "Weather is one NYC coordinate, not station-level microclimate.",
        ),
        (
            "Baseline forecasting",
            "forecast_backtest_metrics.csv",
            "Implemented",
            "Previous-day, previous-week, and calendar-profile baselines establish benchmarks.",
            "Current main report uses a single Jan. 25-31 holdout.",
        ),
        (
            "Rolling-origin validation",
            "rolling_backtest_metrics.csv",
            "Implemented",
            "Daily rolling 24-hour origins demonstrate stronger forecast evaluation practice.",
            "January-only method layer; see multi_month_proof.html for full-year validation.",
        ),
        (
            "Forecast error metrics",
            "forecast_backtest_metrics.csv",
            "Implemented",
            "MAE, RMSE, MAPE, and mean actuals are reported for transparent model comparison.",
            "MAPE can overemphasize low-volume overnight hours.",
        ),
        (
            "Residual and anomaly analysis",
            "anomaly_hours.csv",
            "Implemented",
            "Seasonal residuals identify hours worth investigating.",
            "External events, outages, and operations context are needed for root cause.",
        ),
        (
            "Hierarchy and panels",
            "top_stations.csv",
            "Documented extension",
            "Station rankings show how to evolve from aggregate demand to station-cluster panels.",
            "Station IDs and metadata are required before longitudinal station forecasts.",
        ),
        (
            "Model governance",
            "MODEL_CARD.md",
            "Implemented",
            "Model card, caveats, and publishing checklist make limitations visible.",
            "Production claims require more history and stronger validation.",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=["time_series_area", "artifact", "status", "reviewer_value", "caveat"],
    )


def build_showcase_metrics(
    hourly: pd.DataFrame,
    index_validation: dict[str, int | str],
    autocorr: pd.DataFrame,
    lag_corr: pd.DataFrame,
    rolling_metrics: pd.DataFrame,
    components: pd.DataFrame,
) -> pd.DataFrame:
    """Build compact evidence metrics for the showcase report."""
    lag_lookup = autocorr.set_index("lag_hours")["autocorrelation"]
    best_rolling = rolling_metrics.iloc[0] if not rolling_metrics.empty else None
    max_positive = components.loc[components["seasonal_residual"].idxmax()]
    max_negative = components.loc[components["seasonal_residual"].idxmin()]
    top_lag_feature = lag_corr.iloc[0]

    rows = [
        (
            "time_index",
            "hourly_observations",
            index_validation["hourly_observations"],
            "Complete hourly panel size used by the time-series artifacts.",
        ),
        (
            "time_index",
            "missing_hours",
            index_validation["missing_hours"],
            "Zero is ideal because the model sees a regular hourly series.",
        ),
        (
            "time_index",
            "duplicate_hours",
            index_validation["duplicate_hours"],
            "Zero is ideal because each hour should have exactly one demand value.",
        ),
        (
            "seasonality",
            "lag_24h_autocorrelation",
            round(float(lag_lookup.get(24, np.nan)), 4),
            "Daily repetition signal in hourly ride starts.",
        ),
        (
            "seasonality",
            "lag_168h_autocorrelation",
            round(float(lag_lookup.get(168, np.nan)), 4),
            "Weekly repetition signal in hourly ride starts.",
        ),
        (
            "lag_features",
            "top_abs_correlation_feature",
            top_lag_feature["feature"],
            "Highest absolute correlation among lag, rolling, and weather candidates.",
        ),
        (
            "lag_features",
            "top_abs_correlation_value",
            round(float(top_lag_feature["correlation_with_rides"]), 4),
            "Correlation of the strongest candidate feature with hourly rides.",
        ),
        (
            "rolling_validation",
            "best_rolling_backtest_model",
            best_rolling["model"] if best_rolling is not None else "not_available",
            "Best average MAE across daily rolling 24-hour origins.",
        ),
        (
            "rolling_validation",
            "best_rolling_backtest_mae",
            round(float(best_rolling["mae"]), 2)
            if best_rolling is not None
            else np.nan,
            "Mean absolute error in rides per hour across rolling origins.",
        ),
        (
            "decomposition",
            "seasonal_residual_std",
            round(float(components["seasonal_residual"].std()), 2),
            "Residual spread after subtracting the weekday/hour seasonal profile.",
        ),
        (
            "decomposition",
            "largest_positive_residual_hour",
            str(max_positive["hour"]),
            "Hour where actual rides most exceeded the weekday/hour expected value.",
        ),
        (
            "decomposition",
            "largest_negative_residual_hour",
            str(max_negative["hour"]),
            "Hour where actual rides most missed the weekday/hour expected value.",
        ),
        (
            "volume",
            "mean_hourly_rides",
            round(float(hourly["rides"].mean()), 2),
            "Average hourly demand level for scale.",
        ),
    ]
    return pd.DataFrame(
        rows, columns=["category", "measure", "value", "interpretation"]
    )


def plot_autocorrelation(autocorr: pd.DataFrame) -> Path:
    """Plot hourly autocorrelation values and key seasonal lags."""
    family = COLOR_FAMILIES["blue"]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    sns.lineplot(
        data=autocorr,
        x="lag_hours",
        y="autocorrelation",
        ax=ax,
        color=family["base"],
        linewidth=1.0,
    )
    for lag, label in [(24, "24h"), (168, "168h")]:
        value = autocorr.loc[autocorr["lag_hours"] == lag, "autocorrelation"].iloc[0]
        ax.axvline(lag, color=TOKENS["ink"], linestyle=":", linewidth=1.0)
        ax.text(lag + 2, value, label, fontsize=8, color=TOKENS["ink"], va="center")
    ax.axhline(0, color=NEUTRAL_MARKS["mid"], linewidth=1.0)
    ax.set_xlabel("Lag Hours")
    ax.set_ylabel("Autocorrelation")
    add_chart_header(
        fig,
        ax,
        "Autocorrelation highlights daily and weekly repetition",
        "Hourly Citi Bike ride starts, lags 1-168 hours, January 2024 fixed panel.",
    )
    return save_chart(fig, "autocorrelation_profile.png")


def plot_lag_feature_correlations(lag_corr: pd.DataFrame) -> Path:
    """Plot the strongest lag, rolling, and weather feature correlations."""
    plot_df = lag_corr.dropna().head(12).sort_values("correlation_with_rides")
    pos = COLOR_FAMILIES["olive"]
    neg = COLOR_FAMILIES["orange"]
    colors = np.where(plot_df["correlation_with_rides"] >= 0, pos["base"], neg["base"])
    edges = np.where(plot_df["correlation_with_rides"] >= 0, pos["dark"], neg["dark"])

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    bars = ax.barh(plot_df["feature"], plot_df["correlation_with_rides"], color=colors)
    for bar, edge in zip(bars, edges):
        bar.set_edgecolor(edge)
        bar.set_linewidth(1.0)
    ax.axvline(0, color=TOKENS["ink"], linewidth=1.0)
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.2f}"))
    ax.set_xlabel("Correlation With Hourly Rides")
    ax.set_ylabel("")
    add_chart_header(
        fig,
        ax,
        "Lag and rolling features dominate simple correlation screening",
        "Top candidate features by absolute Pearson correlation with hourly rides.",
    )
    return save_chart(fig, "lag_feature_correlations.png")


def plot_rolling_backtest(rolling_metrics: pd.DataFrame) -> Path:
    """Plot rolling-origin MAE by forecast model."""
    plot_df = rolling_metrics.sort_values("mae", ascending=True).copy()
    plot_df["model_label"] = plot_df["model"].map(label_model)
    family = COLOR_FAMILIES["gold"]
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    sns.barplot(
        data=plot_df,
        x="mae",
        y="model_label",
        ax=ax,
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
    )
    for patch, value in zip(ax.patches, plot_df["mae"]):
        ax.text(
            patch.get_width() + 12,
            patch.get_y() + patch.get_height() / 2,
            f"{value:,.0f}",
            va="center",
            fontsize=8,
            color=TOKENS["ink"],
        )
    ax.set_xlabel("Mean Absolute Error, Rides Per Hour")
    ax.set_ylabel("")
    ax.set_xlim(0, plot_df["mae"].max() * 1.18)
    add_chart_header(
        fig,
        ax,
        "Rolling-origin validation keeps the benchmark honest",
        "Daily 24-hour forecast origins from Jan. 15-31, 2024; lower MAE is better.",
    )
    return save_chart(fig, "rolling_backtest_mae.png")


def plot_decomposition(components: pd.DataFrame) -> Path:
    """Plot observed demand against trend and seasonal expected demand."""
    family = COLOR_FAMILIES["blue"]
    seasonal_family = COLOR_FAMILIES["gold"]
    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    sns.lineplot(
        data=components,
        x="hour",
        y="rides",
        ax=ax,
        color=NEUTRAL_MARKS["base"],
        linewidth=0.8,
        label="Actual hourly rides",
    )
    sns.lineplot(
        data=components,
        x="hour",
        y="trend_24h",
        ax=ax,
        color=family["base"],
        linewidth=1.0,
        label="24h rolling trend",
    )
    sns.lineplot(
        data=components,
        x="hour",
        y="seasonal_expected",
        ax=ax,
        color=seasonal_family["base"],
        linewidth=0.9,
        label="Weekday/hour expected",
    )
    format_date_axis(ax)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        frameon=False,
        ncol=3,
        borderaxespad=0,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Ride Starts")
    add_chart_header(
        fig,
        ax,
        "Decomposition proxy separates level, seasonality, and residual movement",
        "Actual rides, rolling trend, and weekday/hour expected demand for the January hourly panel.",
    )
    return save_chart(fig, "decomposition_proxy.png")


def plot_residual_distribution(components: pd.DataFrame) -> Path:
    """Plot the distribution of seasonal residuals."""
    family = COLOR_FAMILIES["pink"]
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    sns.histplot(
        data=components,
        x="seasonal_residual",
        bins=34,
        ax=ax,
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
    )
    ax.axvline(0, color=TOKENS["ink"], linestyle=":", linewidth=1.0)
    ax.set_xlabel("Actual Minus Weekday/Hour Expected Rides")
    ax.set_ylabel("Hours")
    add_chart_header(
        fig,
        ax,
        "Seasonal residuals expose anomaly candidates",
        "Residual distribution after subtracting the weekday/hour expected profile.",
    )
    return save_chart(fig, "seasonal_residual_distribution.png")


def table_html(
    df: pd.DataFrame,
    *,
    max_rows: int | None = None,
    columns: list[str] | None = None,
    rename: dict[str, str] | None = None,
    formatters: dict[str, object] | None = None,
) -> str:
    """Render selected DataFrame content as an HTML table."""
    display = df if max_rows is None else df.head(max_rows)
    if columns is not None:
        display = display.loc[:, columns]
    if rename:
        display = display.rename(columns=rename)
        if formatters:
            formatters = {
                rename.get(key, key): value for key, value in formatters.items()
            }

    return display.to_html(
        index=False,
        escape=True,
        classes="data-table",
        border=0,
        formatters=formatters,
    )


def rolling_metrics_for_report(rolling_metrics: pd.DataFrame) -> pd.DataFrame:
    """Prepare rolling metrics with reader-friendly model labels."""
    display = rolling_metrics.copy()
    display["model"] = display["model"].map(label_model)
    return display


def generate_showcase_report(
    metrics: pd.DataFrame,
    coverage: pd.DataFrame,
    rolling_metrics: pd.DataFrame,
    chart_paths: list[Path],
) -> Path:
    """Render the time-series showcase as standalone HTML."""
    metric_lookup = metrics.set_index("measure")["value"].to_dict()
    chart_blocks = "\n".join(
        f"""
        <figure>
          <img src="charts/{html.escape(path.name)}" alt="{html.escape(path.stem.replace("_", " "))}">
          <figcaption>{html.escape(CHART_CAPTIONS.get(path.name, path.stem.replace("_", " ").title()))}</figcaption>
        </figure>
        """
        for path in chart_paths
    )
    best_model = label_model(
        metric_lookup.get("best_rolling_backtest_model", "not available")
    )
    best_mae = fmt_number(metric_lookup.get("best_rolling_backtest_mae", np.nan))
    rolling_report = rolling_metrics_for_report(rolling_metrics)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Citi Bike Time-Series Showcase</title>
  <style>
    :root {{
      --surface: #FCFCFD;
      --panel: #FFFFFF;
      --ink: #1F2430;
      --muted: #6F768A;
      --grid: #E6E8F0;
      --blue: #A3BEFA;
      --gold: #FFE15B;
      --orange: #F0986E;
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
      font-size: clamp(30px, 5vw, 48px);
      line-height: 1.02;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 36px 0 12px;
      font-size: 24px;
    }}
    p, li {{
      font-size: 16px;
      line-height: 1.62;
      color: var(--muted);
    }}
    a {{ color: #2E4780; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0 30px;
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
    figure {{
      margin: 24px 0;
    }}
    figure img {{
      display: block;
      width: 100%;
      height: auto;
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
    .callout {{
      border-left: 4px solid var(--orange);
      background: #FFEDDE;
      padding: 14px 16px;
      border-radius: 6px;
      color: var(--ink);
    }}
    .split {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin: 18px 0;
    }}
    .note {{
      background: var(--panel);
      border: 1px solid var(--grid);
      border-radius: 8px;
      padding: 16px;
    }}
    .note h3 {{
      margin: 0 0 8px;
      font-size: 17px;
    }}
    .note ul {{
      margin: 0;
      padding-left: 20px;
    }}
    @media (max-width: 760px) {{
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .split {{ grid-template-columns: 1fr; }}
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
    <h1>Citi Bike Time-Series Showcase</h1>
    <p>
      This companion report turns the January 2024 Citi Bike demand profile
      into a reviewer-ready time-series case study. It shows how the hourly
      target is built, which temporal signals appear, how transparent baselines
      are tested, and where the current one-month scope still limits the claim.
    </p>
  </header>

  <section class="kpis">
    <div class="kpi">
      <strong>{html.escape(str(metric_lookup.get("hourly_observations", "")))}</strong>
      <span>hourly observations</span>
    </div>
    <div class="kpi">
      <strong>{html.escape(str(metric_lookup.get("missing_hours", "")))}</strong>
      <span>missing hours in fixed panel</span>
    </div>
    <div class="kpi">
      <strong>{html.escape(str(best_model))}</strong>
      <span>best rolling-origin baseline</span>
    </div>
    <div class="kpi">
      <strong>{html.escape(best_mae)}</strong>
      <span>best rolling MAE, rides/hour</span>
    </div>
  </section>

  <section>
    <h2>Review Path</h2>
    <p class="callout">
      Read this report as the methods layer. It proves the project is not just
      a chart export: it builds a regular hourly index, checks seasonality and
      autocorrelation, screens lag features, scores leakage-safe rolling
      baselines, inspects residuals, and documents what remains unproven.
    </p>
    <div class="split">
      <div class="note">
        <h3>What this proves</h3>
        <ul>
          <li>The target grain is explicit: valid trip starts per hour.</li>
          <li>The hourly panel is regular, with no missing or duplicate hours.</li>
          <li>Daily and weekly lag structure is visible before modeling.</li>
          <li>Baselines are scored from history available before each origin.</li>
        </ul>
      </div>
      <div class="note">
        <h3>What it does not prove yet</h3>
        <ul>
          <li>Annual seasonality or production forecast stability.</li>
          <li>Causal weather effects or event root causes.</li>
          <li>Station-level performance with stable station identifiers.</li>
          <li>Calibrated prediction intervals.</li>
        </ul>
      </div>
    </div>
  </section>

  <section>
    <h2>Showcase Charts</h2>
    {chart_blocks}
  </section>

  <section>
    <h2>Rolling Backtest Summary</h2>
    {
        table_html(
            rolling_report,
            columns=[
                "model",
                "origins",
                "holdout_hours",
                "mean_actual",
                "mae",
                "rmse",
                "mape",
            ],
            rename={
                "model": "Model",
                "origins": "Origins",
                "holdout_hours": "Holdout Hours",
                "mean_actual": "Mean Actual",
                "mae": "MAE",
                "rmse": "RMSE",
                "mape": "MAPE",
            },
            formatters={
                "mean_actual": lambda value: fmt_number(value),
                "mae": lambda value: fmt_number(value),
                "rmse": lambda value: fmt_number(value),
                "mape": lambda value: fmt_percent(value),
            },
        )
    }
  </section>

  <section>
    <h2>Time-Series Coverage Map</h2>
    {
        table_html(
            coverage,
            rename={
                "time_series_area": "Area",
                "artifact": "Artifact",
                "status": "Status",
                "reviewer_value": "Reviewer Value",
                "caveat": "Caveat",
            },
        )
    }
  </section>

  <section>
    <h2>Important Limit And Upgrade Path</h2>
    <p>
      This report is still the January methods layer. The project now also
      includes <code>multi_month_proof.html</code>, which extends aggregate
      validation across full-year 2024 data. The strongest next version should
      add station IDs, station metadata, and station-cluster forecasts tied to a
      concrete operating decision.
    </p>
  </section>
</main>
</body>
</html>
"""
    report_path = OUT_DIR / "time_series_showcase.html"
    report_path.write_text(html_doc, encoding="utf-8")
    return report_path


def main() -> None:
    """Run the time-series showcase generation workflow."""
    use_chart_theme()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    hourly = load_hourly_profile()
    index_validation = validate_hourly_index(hourly)
    autocorr = build_autocorrelation_profile(hourly)
    lag_corr = build_lag_feature_correlations(hourly)
    rolling_metrics, rolling_origin_metrics, rolling_scored = build_rolling_backtests(
        hourly
    )
    components = build_decomposition_components(hourly)
    coverage = build_showcase_coverage()
    metrics = build_showcase_metrics(
        hourly, index_validation, autocorr, lag_corr, rolling_metrics, components
    )

    autocorr.to_csv(OUT_DIR / "autocorrelation_profile.csv", index=False)
    lag_corr.to_csv(OUT_DIR / "lag_feature_correlations.csv", index=False)
    rolling_metrics.to_csv(OUT_DIR / "rolling_backtest_metrics.csv", index=False)
    rolling_origin_metrics.to_csv(
        OUT_DIR / "rolling_backtest_origin_metrics.csv", index=False
    )
    rolling_scored.to_csv(OUT_DIR / "rolling_backtest_scored.csv", index=False)
    components.to_csv(OUT_DIR / "decomposition_components.csv", index=False)
    coverage.to_csv(OUT_DIR / "time_series_showcase_coverage.csv", index=False)
    metrics.to_csv(OUT_DIR / "time_series_showcase_metrics.csv", index=False)

    chart_paths = [
        plot_autocorrelation(autocorr),
        plot_lag_feature_correlations(lag_corr),
        plot_rolling_backtest(rolling_metrics),
        plot_decomposition(components),
        plot_residual_distribution(components),
    ]
    generate_showcase_report(metrics, coverage, rolling_metrics, chart_paths)


if __name__ == "__main__":
    main()
