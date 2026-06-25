"""Render the Citi Bike decision-facing HTML report from prepared outputs."""

from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "outputs"
CHART_DIR = PROFILE_DIR / "charts"
REPORT_PATH = PROFILE_DIR / "decision_report.html"
SOURCE_NOTES_PATH = PROFILE_DIR / "decision_report_source_notes.md"

PROFILE_REQUIRED_KEYS = {
    "rush_vs_off_hour_ratio",
    "weekend_vs_weekday_ratio",
    "summary",
}
SUMMARY_REQUIRED_KEYS = {
    "total_rides",
    "hourly_points",
    "average_daily_rides",
    "average_hourly_rides",
    "peak_hour_rides",
    "peak_hour",
}
FORECAST_REQUIRED_COLUMNS = {"model", "mae", "rmse", "mape", "mean_actual"}
TOP_STATIONS_REQUIRED_COLUMNS = {"station", "rides", "share_of_valid_trips"}
ANOMALY_REQUIRED_COLUMNS = {"hour", "absolute_gap"}


def fmt_int(value: float | int) -> str:
    """Format a number as a rounded integer string."""
    if pd.isna(value):
        return "n/a"
    return f"{int(round(float(value))):,}"


def fmt_k(value: float | int) -> str:
    """Format a number using compact thousand or million suffixes."""
    if pd.isna(value):
        return "n/a"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return fmt_int(value)


def fmt_pct(value: float, digits: int = 1) -> str:
    """Format a decimal ratio as a percentage string."""
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def fmt_num(value: float, digits: int = 1) -> str:
    """Format a number with grouped thousands and fixed decimals."""
    if pd.isna(value):
        return "n/a"
    return f"{value:,.{digits}f}"


def load_inputs() -> dict:
    """Load profile, forecast, station, anomaly, and mix inputs."""
    profile = read_json_object(PROFILE_DIR / "profile_summary.json")
    require_mapping_keys(profile, PROFILE_REQUIRED_KEYS, "profile_summary.json")
    summary = profile["summary"]
    if not isinstance(summary, dict):
        raise ValueError("profile_summary.json field 'summary' must be an object.")
    require_mapping_keys(summary, SUMMARY_REQUIRED_KEYS, "profile_summary.json summary")

    forecast = read_csv_table(
        PROFILE_DIR / "forecast_backtest_metrics.csv",
        required_columns=FORECAST_REQUIRED_COLUMNS,
    )
    top_stations = read_csv_table(
        PROFILE_DIR / "top_stations.csv",
        required_columns=TOP_STATIONS_REQUIRED_COLUMNS,
    )
    anomalies = read_csv_table(
        PROFILE_DIR / "anomaly_hours.csv",
        required_columns=ANOMALY_REQUIRED_COLUMNS,
    )
    return {
        "profile": profile,
        "summary": summary,
        "forecast": forecast,
        "top_stations": top_stations,
        "anomalies": anomalies,
        "member_mix": read_csv_table(PROFILE_DIR / "member_mix.csv"),
        "bike_mix": read_csv_table(PROFILE_DIR / "bike_mix.csv"),
    }


def read_json_object(path: Path) -> dict:
    """Read a JSON object from disk with a clear schema error."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object.")
    return payload


def read_csv_table(
    path: Path, *, required_columns: set[str] | None = None
) -> pd.DataFrame:
    """Read a CSV source table and validate required columns when provided."""
    frame = pd.read_csv(path)
    if required_columns is not None:
        require_columns(frame, required_columns, path.name)
    return frame


def require_mapping_keys(mapping: dict, required: set[str], source_name: str) -> None:
    """Validate that a JSON mapping contains required keys."""
    missing = sorted(required.difference(mapping))
    if missing:
        raise KeyError(f"{source_name} is missing required keys: {missing}")


def require_columns(frame: pd.DataFrame, required: set[str], source_name: str) -> None:
    """Validate that a DataFrame contains required columns."""
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise KeyError(f"{source_name} is missing required columns: {missing}")


def require_nonempty(frame: pd.DataFrame, source_name: str) -> None:
    """Validate that a source table has at least one row."""
    if frame.empty:
        raise ValueError(f"{source_name} has no rows.")


def validate_numeric_columns(
    frame: pd.DataFrame, columns: list[str], source_name: str
) -> None:
    """Validate that source columns are numeric and finite enough for reporting."""
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(
                f"{source_name} has nonnumeric or missing values in {column}."
            )
        frame[column] = values.astype(float)


def validate_mapping_numeric(mapping: dict, keys: list[str], source_name: str) -> None:
    """Validate that JSON scalar fields are numeric and finite."""
    for key in keys:
        try:
            value = float(mapping[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"{source_name} has nonnumeric or missing value for {key}."
            ) from exc
        if not np.isfinite(value):
            raise ValueError(
                f"{source_name} has nonnumeric or missing value for {key}."
            )


def required_model_row(forecast: pd.DataFrame, model: str) -> pd.Series:
    """Return exactly one forecast metric row for a required model."""
    matches = forecast.loc[forecast["model"] == model]
    if matches.empty:
        raise ValueError(f"forecast_backtest_metrics.csv is missing model '{model}'.")
    if len(matches) > 1:
        raise ValueError(
            f"forecast_backtest_metrics.csv has duplicate rows for model '{model}'."
        )
    return matches.iloc[0]


def safe_improvement(baseline: object, challenger: object) -> float:
    """Calculate relative improvement without dividing by zero or missing values."""
    baseline_value = float(baseline)
    challenger_value = float(challenger)
    if baseline_value == 0:
        return 0.0
    return (baseline_value - challenger_value) / baseline_value


def table_html(frame: pd.DataFrame, columns: list[str], headers: list[str]) -> str:
    """Render selected DataFrame columns as an HTML table."""
    if len(columns) != len(headers):
        raise ValueError("Table columns and headers must have the same length.")
    require_columns(frame, set(columns), "HTML table source")
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(
            f"<td>{html.escape(str(row[column]))}</td>" for column in columns
        )
        rows.append(f"<tr>{cells}</tr>")
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_report() -> None:
    """Build the decision report and companion source notes."""
    inputs = load_inputs()
    profile = inputs["profile"]
    summary = inputs["summary"]
    forecast = inputs["forecast"].copy()
    top_stations = inputs["top_stations"].copy()
    anomalies = inputs["anomalies"].copy()

    validate_mapping_numeric(
        profile,
        ["rush_vs_off_hour_ratio", "weekend_vs_weekday_ratio"],
        "profile_summary.json",
    )
    validate_mapping_numeric(
        summary,
        [
            "total_rides",
            "hourly_points",
            "average_daily_rides",
            "average_hourly_rides",
            "peak_hour_rides",
        ],
        "profile_summary.json summary",
    )
    validate_numeric_columns(
        forecast,
        ["mae", "rmse", "mape", "mean_actual"],
        "forecast_backtest_metrics.csv",
    )
    validate_numeric_columns(
        top_stations, ["rides", "share_of_valid_trips"], "top_stations.csv"
    )
    validate_numeric_columns(anomalies, ["absolute_gap"], "anomaly_hours.csv")
    require_nonempty(forecast, "forecast_backtest_metrics.csv")
    require_nonempty(top_stations, "top_stations.csv")
    require_nonempty(anomalies, "anomaly_hours.csv")

    best = forecast.sort_values("mae").iloc[0]
    prev_day = required_model_row(forecast, "previous_day")
    prev_week = required_model_row(forecast, "previous_week")
    mae_improvement_day = safe_improvement(prev_day["mae"], best["mae"])
    mae_improvement_week = safe_improvement(prev_week["mae"], best["mae"])
    top10_share = float(top_stations.head(10)["share_of_valid_trips"].sum())
    top_station = top_stations.iloc[0]
    top_anomaly = anomalies.iloc[0]

    forecast_table = forecast.assign(
        mae=lambda frame: frame["mae"].map(lambda value: fmt_int(value)),
        rmse=lambda frame: frame["rmse"].map(lambda value: fmt_int(value)),
        mape=lambda frame: frame["mape"].map(lambda value: fmt_pct(value, 1)),
        mean_actual=lambda frame: frame["mean_actual"].map(
            lambda value: fmt_int(value)
        ),
    )[["model", "mae", "rmse", "mape", "mean_actual"]]

    source_stamp = "Generated from Citi Bike January 2024 public trip history and Open-Meteo weather context."
    title = "Citi Bike Forecast Showcase: Build Around Commuter Seasonality"

    css = """
    :root {
      --surface: #fcfcfd;
      --panel: #ffffff;
      --ink: #1f2430;
      --muted: #626a7c;
      --line: #dfe3ee;
      --soft: #eef4ff;
      --blue: #5477c4;
      --gold: #b8a037;
      --orange: #cc6f47;
      --olive: #71b436;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font-family: Aptos, Inter, "Segoe UI", Arial, sans-serif;
    }
    main {
      max-width: 980px;
      margin: 0 auto;
      padding: 44px 22px 72px;
    }
    header, section { margin-bottom: 34px; }
    h1 {
      margin: 0;
      max-width: 820px;
      font-size: 34px;
      line-height: 1.08;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 21px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    h3 {
      margin: 0 0 8px;
      font-size: 15px;
      letter-spacing: 0;
    }
    p, li {
      font-size: 15px;
      line-height: 1.58;
    }
    p { margin: 0 0 14px; }
    ul, ol { margin: 0; padding-left: 22px; }
    li + li { margin-top: 8px; }
    strong { font-weight: 700; }
    .scope {
      margin-top: 12px;
      color: var(--muted);
      font-size: 14px;
      max-width: 740px;
    }
    .executive-summary-box {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px 22px;
      box-shadow: 0 12px 28px rgba(31, 36, 48, 0.06);
    }
    .kpis {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-top: 18px;
    }
    .kpi {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }
    .kpi strong {
      display: block;
      font-size: 22px;
      line-height: 1.1;
      margin-bottom: 6px;
    }
    .kpi span {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }
    figure {
      margin: 20px 0 6px;
      padding: 0;
    }
    figure img {
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }
    figcaption {
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .two-up {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }
    .callout {
      border-left: 4px solid var(--orange);
      background: #fff8f3;
      padding: 14px 16px;
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0 18px;
      font-size: 14px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    th, td {
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }
    th {
      background: var(--soft);
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
    }
    tr:last-child td { border-bottom: 0; }
    .source-note {
      color: var(--muted);
      font-size: 13px;
      border-top: 1px solid var(--line);
      padding-top: 14px;
    }
    @media (max-width: 760px) {
      main { padding: 32px 16px 56px; }
      h1 { font-size: 29px; }
      .kpis, .two-up { grid-template-columns: 1fr; }
    }
    """

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
  <main data-report-audience="product stakeholders">
    <header data-contract-section="title">
      <h1>{html.escape(title)}</h1>
      <p class="scope">{html.escape(source_stamp)} The report is decision-ready for the portfolio roadmap, not a production operating forecast.</p>
    </header>

    <section class="executive-summary-box" data-contract-section="executive-summary">
      <h2>Executive Summary</h2>
      <ul>
        <li><strong>Make the next iteration a station-aware forecasting story.</strong> The January profile proves a strong hourly demand rhythm: {fmt_k(summary["total_rides"])} starts across {fmt_int(summary["hourly_points"])} hours, with rush-hour volume {fmt_num(profile["rush_vs_off_hour_ratio"], 2)}x off-hour volume and weekend hourly demand at {fmt_num(profile["weekend_vs_weekday_ratio"], 2)}x weekdays. The companion full-2024 proof now extends aggregate validation beyond this month.</li>
        <li><strong>Use the calendar profile as the benchmark, not the finish line.</strong> The simple weekday/hour baseline beat the previous-day baseline by {fmt_pct(mae_improvement_day, 1)} on MAE and the previous-week baseline by {fmt_pct(mae_improvement_week, 1)} on MAE over the Jan. 25-31 holdout. The full-year proof then adds rolling origins and a stronger calendar-lag ridge benchmark.</li>
        <li><strong>Turn the portfolio hook from aggregate demand into an operations question.</strong> The top station, {html.escape(str(top_station["station"]))}, had {fmt_int(top_station["rides"])} starts, and the top 10 stations represented {fmt_pct(top10_share, 1)} of valid trips. That is enough texture to motivate station clusters, rebalancing, and anomaly alerting as the next showcase layer.</li>
      </ul>
    </section>

    <section data-contract-section="key-findings">
      <h2>The demand pattern is strong enough to justify forecasting</h2>
      <p><strong>The core signal is calendar structure.</strong> January 2024 demand averaged {fmt_int(summary["average_daily_rides"])} starts per day and {fmt_int(summary["average_hourly_rides"])} starts per hour, with the peak hour reaching {fmt_int(summary["peak_hour_rides"])} starts on {html.escape(str(summary["peak_hour"]))}. The weekday/hour profile gives the project a clean analytical spine: it explains why a naive average is not enough, while keeping the first model interpretable.</p>
      <figure>
        <img src="charts/daily_demand.png" alt="Daily Citi Bike trip starts in January 2024">
        <figcaption>Daily starts show the month has enough movement for trend context, while the fixed 744-hour panel preserves the grain needed for forecasting.</figcaption>
      </figure>
      <figure>
        <img src="charts/seasonality_heatmap.png" alt="Average hourly starts by weekday and hour">
        <figcaption>The weekday/hour heatmap is the most important feature view: it separates commute structure from overnight and weekend behavior.</figcaption>
      </figure>
    </section>

    <section data-contract-section="key-findings">
      <h2>The baseline gives the next model a useful target</h2>
      <p><strong>The best first benchmark is the calendar profile.</strong> It forecasts each holdout hour from the training-period average for the same weekday and hour. That is simple enough to explain in a portfolio review, and it gives richer models a clear bar to beat before adding weather, holidays, lag features, station clusters, or gradient boosting.</p>
      {table_html(forecast_table, ["model", "mae", "rmse", "mape", "mean_actual"], ["Model", "MAE", "RMSE", "MAPE", "Mean actual"])}
      <figure>
        <img src="charts/forecast_backtest.png" alt="Actual hourly starts versus the best baseline forecast on the holdout period">
        <figcaption>Holdout period: Jan. 25-31, 2024. The residual band is a reference band from previous-week residuals, not calibrated production uncertainty.</figcaption>
      </figure>
      <p><strong>So what:</strong> the project now has the aggregate full-year proof that this January report originally pointed toward. The next credible lift is station metadata, station clusters, and weather or event features tested inside the same rolling-validation loop.</p>
    </section>

    <section data-contract-section="key-findings">
      <h2>Operational texture is the strongest extension path</h2>
      <p><strong>Station and anomaly views turn this from a generic forecast into an applied decision story.</strong> The current output already identifies top start stations and abnormal hours. The largest flagged gap was {fmt_int(top_anomaly["absolute_gap"])} rides at {html.escape(str(top_anomaly["hour"]))}, but it should be treated as a descriptive anomaly until weather, event, station-status, or operations context is checked.</p>
      <figure>
        <img src="charts/top_stations.png" alt="Top Citi Bike start stations by January 2024 starts">
        <figcaption>Station starts are currently keyed by station name, which is good for a first showcase but should be replaced or supplemented with stable station IDs before longitudinal station modeling.</figcaption>
      </figure>
      <div class="callout">
        <p><strong>Recommendation:</strong> frame the next project decision around rebalancing or anomaly alerting. Those decisions naturally use the evidence already present: hour-level demand, commute peaks, station-level starts, simple forecasts, and explicit anomaly rows.</p>
      </div>
    </section>

    <section data-contract-section="recommended-next-steps">
      <h2>Recommended Next Steps</h2>
      <ol>
        <li><strong>Use the full-2024 proof as the aggregate benchmark.</strong> The project now has 12 months, a complete hourly panel, and rolling validation for aggregate demand.</li>
        <li><strong>Add station IDs and station metadata before station-level forecasts.</strong> Station names are not stable enough for longitudinal modeling by themselves.</li>
        <li><strong>Build a station-cluster or neighborhood forecast after the aggregate benchmark.</strong> Keep previous-week and calendar-lag ridge as benchmarks across rolling holdouts.</li>
        <li><strong>Make anomalies explainable, not just detectable.</strong> Join severe weather, holidays, service status, and local event context before describing anomalies as operational causes.</li>
      </ol>
    </section>

    <section data-contract-section="further-questions">
      <h2>Further Questions</h2>
      <ul>
        <li>Which business decision should the forecast serve: staffing, rebalancing, rider communications, station planning, or anomaly alerting?</li>
        <li>What time convention should be treated as canonical for Citi Bike timestamps when joining weather and events?</li>
        <li>Which station metadata source should supply stable station identifiers and active-station periods?</li>
      </ul>
    </section>

    <section data-contract-section="caveats-and-assumptions">
      <h2>Caveats and Assumptions</h2>
      <div class="callout">
        <p>This report uses the local January 2024 Citi Bike profile artifacts as the authoritative computation source. It is source-backed for the portfolio showcase and directional for modeling strategy, but it should not be used as a production forecast without more months, rolling backtests, stable station IDs, and event or operations context.</p>
      </div>
      <p class="source-note">Primary sources: Citi Bike public trip-history archive, Open-Meteo historical weather, the local analysis script, generated CSV outputs, generated chart PNGs, and the Citi Bike time-series semantic layer.</p>
    </section>
  </main>
</body>
</html>
"""

    REPORT_PATH.write_text(html_text, encoding="utf-8")
    SOURCE_NOTES_PATH.write_text(
        build_source_notes(best, prev_day, prev_week, top10_share), encoding="utf-8"
    )


def build_source_notes(
    best: pd.Series, prev_day: pd.Series, prev_week: pd.Series, top10_share: float
) -> str:
    """Render Markdown source notes for the decision report."""
    return f"""# Citi Bike Decision Report Source Notes

## Report Contract

- Audience: product stakeholders.
- Delivery mode: portable static HTML.
- Required structure mapping:
  - Title: `decision_report.html` header.
  - Executive summary: visible `Executive Summary` section.
  - Key findings with visual evidence: demand pattern, baseline, and operational texture sections.
  - Recommended next steps: visible ordered list.
  - Further questions: visible questions section.
  - Caveats and assumptions: visible caveat callout.

## Context Note

The decision is how to evolve the Citi Bike time-series showcase. The best-supported recommendation is now to move from aggregate full-year demand into a station-aware forecasting and anomaly workflow. The current evidence is strong for a portfolio profile because it has public raw data, reproducible transformation code, hourly outputs, forecast backtest outputs, full-year rolling validation, and chart assets. It is still limited for live operational decisions because it lacks official station metadata, internal operations context, weather/event feature validation, and calibrated uncertainty.

## Chart Map

| Report Segment | Visual | Chart Family | Supports | Source |
| --- | --- | --- | --- | --- |
| Demand pattern | `charts/daily_demand.png` | Trend | January demand has enough temporal movement for time-series profiling | `hourly_profile.csv` |
| Demand pattern | `charts/seasonality_heatmap.png` | Heatmap | Weekday/hour structure is the core modeling signal | `seasonality_profile.csv` |
| Baseline | `charts/forecast_backtest.png` | Trend with benchmark | Calendar profile creates the first forecast benchmark | `forecast_backtest_scored.csv` |
| Operational texture | `charts/top_stations.png` | Ranked horizontal bars | Station starts create a practical extension path | `top_stations.csv` |

## Key Validation Checks

- Valid-trip filter came from `citibike_time_series_profile.py`: parseable start/end timestamps and duration from 1 to 240 minutes.
- Best baseline by MAE: `{best["model"]}` with MAE {best["mae"]:.1f}.
- Previous-day MAE: {prev_day["mae"]:.1f}; previous-week MAE: {prev_week["mae"]:.1f}.
- Top 10 station share of valid trips: {top10_share:.4f}.
- Weather correlations were treated as descriptive only.

## Omitted Or Deferred Evidence

- No live warehouse, dashboard, or team-communication source was used because the current project is based on public data and local artifacts.
- No new model was fit in this report; the recommendation is to extend the evidence base before adding a stronger model.
- No station-level longitudinal conclusion is made because current station outputs use names rather than stable station IDs.
"""


if __name__ == "__main__":
    build_report()
