"""Build the Citi Bike portfolio dashboard and decision simulator.

This module sits on top of the generated forecasting artifacts. It does not
retrain models or re-download raw trip archives. Instead, it turns reviewed
CSV and JSON outputs into a compact portfolio surface:

* a static dashboard for reviewers,
* a scenario-based rebalancing simulator, and
* feature-family lift tables that explain why richer inputs help.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "outputs"

SIMULATOR_COLUMNS = [
    "scenario",
    "scenario_label",
    "cluster_label",
    "annual_starts",
    "expected_hourly_starts",
    "weather_event_mae",
    "weather_event_wape",
    "lift_vs_previous_week",
    "risk_score",
    "priority_tier",
    "recommended_action",
]

MODEL_COMPARISON_MODELS = [
    "weather_event_ridge",
    "calendar_lag_ridge",
    "previous_week",
]
CLUSTER_SEGMENT_PATTERN = re.compile(r"^cluster_(\d+)$")


@dataclass(frozen=True)
class Scenario:
    """Decision-simulator settings for one operating review scenario."""

    name: str
    label: str
    demand_multiplier: float
    weather_pressure: float
    event_pressure: float
    alert_threshold: float


DEFAULT_SCENARIOS = [
    Scenario(
        name="normal_weekday",
        label="Normal weekday",
        demand_multiplier=1.00,
        weather_pressure=0.00,
        event_pressure=0.00,
        alert_threshold=0.56,
    ),
    Scenario(
        name="rain_event",
        label="Rain or snow pressure",
        demand_multiplier=0.86,
        weather_pressure=0.22,
        event_pressure=0.00,
        alert_threshold=0.48,
    ),
    Scenario(
        name="major_event",
        label="Major event window",
        demand_multiplier=1.12,
        weather_pressure=0.04,
        event_pressure=0.20,
        alert_threshold=0.50,
    ),
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the portfolio dashboard builder."""
    parser = argparse.ArgumentParser(
        description="Build portfolio dashboard and simulator artifacts."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUT_DIR,
        help="Directory containing generated Citi Bike output artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    """Build dashboard, simulator, and explainability outputs."""
    args = parse_args()
    artifacts = load_artifacts(args.output_dir)
    feature_lift = build_feature_family_lift(artifacts["lift"])
    panel_hours = panel_hours_from_summary(artifacts["station_summary"])
    simulator = build_decision_simulator(
        artifacts["priorities"],
        artifacts["lift"],
        scenarios=DEFAULT_SCENARIOS,
        panel_hours=panel_hours,
    )
    dashboard = render_html_report(
        station_summary=artifacts["station_summary"],
        multi_month_summary=artifacts["multi_month_summary"],
        metrics=artifacts["metrics"],
        lift=artifacts["lift"],
        priorities=artifacts["priorities"],
        feature_lift=feature_lift,
        simulator=simulator,
    )
    write_outputs(args.output_dir, feature_lift, simulator, dashboard)


def load_artifacts(output_dir: Path = OUT_DIR) -> dict[str, object]:
    """Load the reviewed outputs required by the portfolio dashboard."""
    paths = {
        "station_summary": output_dir / "station_cluster_forecast_summary.json",
        "multi_month_summary": output_dir / "multi_month_proof_summary.json",
        "metrics": output_dir / "station_cluster_model_metrics.csv",
        "lift": output_dir / "station_cluster_model_lift.csv",
        "priorities": output_dir / "station_cluster_capacity_priorities.csv",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing dashboard source artifact(s): " + ", ".join(missing)
        )

    return {
        "station_summary": read_json(paths["station_summary"]),
        "multi_month_summary": read_json(paths["multi_month_summary"]),
        "metrics": pd.read_csv(paths["metrics"]),
        "lift": pd.read_csv(paths["lift"]),
        "priorities": pd.read_csv(paths["priorities"]),
    }


def read_json(path: Path) -> dict[str, object]:
    """Read a JSON object from disk with a clear error for non-objects."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def build_feature_family_lift(lift: pd.DataFrame) -> pd.DataFrame:
    """Summarize out-of-sample lift by feature family.

    The source model artifacts compare three progressively richer model
    families. This table turns those comparisons into a reviewer-friendly
    explanation without pretending to have causal feature attributions.
    """
    required = {
        "segment_id",
        "segment_label",
        "mae_previous_week",
        "mae_calendar_lag_ridge",
        "mae_weather_event_ridge",
    }
    require_columns(lift, required, "station_cluster_model_lift.csv")
    if lift.empty:
        raise ValueError("station_cluster_model_lift.csv has no evaluated segments.")
    validate_unique_key(lift, "segment_id", "station_cluster_model_lift.csv")
    validate_text_columns(
        lift,
        ["segment_id", "segment_label"],
        source_name="station_cluster_model_lift.csv",
    )
    validate_numeric_columns(
        lift,
        ["mae_previous_week", "mae_calendar_lag_ridge", "mae_weather_event_ridge"],
        source_name="station_cluster_model_lift.csv",
    )
    validate_nonnegative_columns(
        lift,
        ["mae_previous_week", "mae_calendar_lag_ridge", "mae_weather_event_ridge"],
        source_name="station_cluster_model_lift.csv",
    )

    comparisons = [
        (
            "Calendar and lag features",
            "Previous-week operating baseline",
            "Calendar + lag ridge",
            "mae_previous_week",
            "mae_calendar_lag_ridge",
            "Calendar cycles, federal holiday flags, 24-hour lag, 168-hour lag, and rolling means.",
        ),
        (
            "Weather and event features",
            "Calendar + lag ridge",
            "Weather/event ridge",
            "mae_calendar_lag_ridge",
            "mae_weather_event_ridge",
            "Observed weather, precipitation/snow flags, temperature pressure, holiday windows, and selected event windows.",
        ),
    ]

    rows: list[dict[str, object]] = []
    for (
        family,
        baseline,
        challenger,
        baseline_col,
        challenger_col,
        definition,
    ) in comparisons:
        baseline_mae = lift[baseline_col].astype(float)
        challenger_mae = lift[challenger_col].astype(float)
        reduction = baseline_mae - challenger_mae
        lift_pct = reduction / baseline_mae.replace(0, np.nan)
        mean_lift = coerce_float(lift_pct.mean(), default=0.0)
        median_lift = coerce_float(lift_pct.median(), default=0.0)
        best_idx = reduction.idxmax()
        weakest_idx = reduction.idxmin()
        rows.append(
            {
                "feature_family": family,
                "baseline_model": baseline,
                "challenger_model": challenger,
                "segments_evaluated": int(len(lift)),
                "segments_improved": int((reduction > 0).sum()),
                "weighted_lift_pct": safe_ratio(reduction.sum(), baseline_mae.sum()),
                "mean_lift_pct": mean_lift,
                "median_lift_pct": median_lift,
                "best_segment": str(lift.loc[best_idx, "segment_label"]),
                "weakest_segment": str(lift.loc[weakest_idx, "segment_label"]),
                "definition": definition,
                "interpretation": feature_family_interpretation(
                    family, int((reduction > 0).sum()), int(len(lift))
                ),
            }
        )
    return pd.DataFrame(rows)


def feature_family_interpretation(
    family: str, segments_improved: int, segments_evaluated: int
) -> str:
    """Return a concise interpretation for a feature-family result."""
    if segments_evaluated == 0:
        return "No evaluated segments were available."
    if segments_improved == segments_evaluated:
        return f"{family} improved MAE for every evaluated segment."
    if segments_improved >= max(1, round(segments_evaluated * 0.7)):
        return f"{family} improved MAE for most evaluated segments."
    if segments_improved > 0:
        return f"{family} improved MAE for some segments and should stay diagnostic."
    return f"{family} did not improve MAE in this validation run."


def build_decision_simulator(
    priorities: pd.DataFrame,
    lift: pd.DataFrame,
    *,
    scenarios: Iterable[Scenario],
    panel_hours: int,
) -> pd.DataFrame:
    """Build a deterministic cluster-level rebalancing scenario table."""
    required_priorities = {
        "segment_id",
        "cluster_label",
        "annual_starts",
        "mae",
        "wape",
    }
    required_lift = {
        "segment_id",
        "mae_lift_pct_vs_previous_week",
    }
    require_columns(
        priorities, required_priorities, "station_cluster_capacity_priorities.csv"
    )
    require_columns(lift, required_lift, "station_cluster_model_lift.csv")
    panel_hours = validate_positive_integer(panel_hours, field="panel_hours")
    scenario_list = validate_scenarios(scenarios)
    scenario_order = {
        scenario.name: index for index, scenario in enumerate(scenario_list)
    }
    validate_unique_key(lift, "segment_id", "station_cluster_model_lift.csv")
    validate_unique_key(
        priorities, "segment_id", "station_cluster_capacity_priorities.csv"
    )
    validate_text_columns(
        lift, ["segment_id"], source_name="station_cluster_model_lift.csv"
    )
    validate_text_columns(
        priorities,
        ["segment_id", "cluster_label"],
        source_name="station_cluster_capacity_priorities.csv",
    )
    if priorities.empty:
        return pd.DataFrame(columns=SIMULATOR_COLUMNS)

    missing_lift_ids = sorted(set(priorities["segment_id"]) - set(lift["segment_id"]))
    if missing_lift_ids:
        preview = preview_values(missing_lift_ids)
        raise ValueError(
            "station_cluster_model_lift.csv is missing lift rows for priority "
            f"segment_id value(s): {preview}."
        )

    merged = priorities.drop(
        columns=["mae_lift_pct_vs_previous_week"], errors="ignore"
    ).merge(
        lift[["segment_id", "mae_lift_pct_vs_previous_week"]],
        on="segment_id",
        how="left",
        validate="one_to_one",
    )
    validate_numeric_columns(
        merged,
        ["annual_starts", "mae", "wape", "mae_lift_pct_vs_previous_week"],
        source_name="portfolio simulator source tables",
    )
    validate_nonnegative_columns(
        merged,
        ["annual_starts", "mae", "wape"],
        source_name="portfolio simulator source tables",
    )
    max_annual = max(float(merged["annual_starts"].max()), 1.0)
    max_wape = max(float(merged["wape"].max()), 0.001)
    max_mae = max(float(merged["mae"].max()), 1.0)

    rows: list[dict[str, object]] = []
    for scenario in scenario_list:
        for row in merged.itertuples(index=False):
            annual_starts = float(row.annual_starts)
            wape = float(row.wape)
            mae = float(row.mae)
            lift_pct = coerce_float(row.mae_lift_pct_vs_previous_week)
            score = scenario_risk_score(
                annual_starts=annual_starts,
                max_annual=max_annual,
                wape=wape,
                max_wape=max_wape,
                mae=mae,
                max_mae=max_mae,
                lift_pct=lift_pct,
                scenario=scenario,
            )
            tier = priority_tier(score, scenario.alert_threshold)
            rows.append(
                {
                    "scenario": scenario.name,
                    "scenario_label": scenario.label,
                    "cluster_label": str(row.cluster_label),
                    "annual_starts": annual_starts,
                    "expected_hourly_starts": annual_starts
                    / panel_hours
                    * scenario.demand_multiplier,
                    "weather_event_mae": mae,
                    "weather_event_wape": wape,
                    "lift_vs_previous_week": lift_pct,
                    "risk_score": score,
                    "priority_tier": tier,
                    "recommended_action": recommended_action(tier, scenario),
                }
            )

    simulator = pd.DataFrame(rows, columns=SIMULATOR_COLUMNS)
    simulator["_scenario_order"] = simulator["scenario"].map(scenario_order)
    return (
        simulator.sort_values(
            ["_scenario_order", "risk_score", "annual_starts"],
            ascending=[True, False, False],
        )
        .drop(columns="_scenario_order")
        .reset_index(drop=True)
    )


def panel_hours_from_summary(station_summary: dict[str, object]) -> int:
    """Return the station-cluster panel length from the summary artifact."""
    value = station_summary.get("hourly_observations_per_segment")
    if value is None:
        raise KeyError(
            "station_cluster_forecast_summary.json is missing "
            "'hourly_observations_per_segment'."
        )
    return validate_positive_integer(
        value,
        field=(
            "station_cluster_forecast_summary.json 'hourly_observations_per_segment'"
        ),
    )


def scenario_risk_score(
    *,
    annual_starts: float,
    max_annual: float,
    wape: float,
    max_wape: float,
    mae: float,
    max_mae: float,
    lift_pct: float,
    scenario: Scenario,
) -> float:
    """Score operating review priority for one cluster and scenario."""
    volume_index = safe_ratio(annual_starts, max_annual)
    error_index = safe_ratio(wape, max_wape)
    absolute_error_index = safe_ratio(mae, max_mae)
    residual_uncertainty = max(0.0, 1.0 - max(lift_pct, 0.0) / 0.25)
    scenario_pressure = scenario.demand_multiplier * (
        1.0 + scenario.weather_pressure + scenario.event_pressure
    )
    raw_score = scenario_pressure * (
        0.48 * volume_index
        + 0.24 * error_index
        + 0.18 * absolute_error_index
        + 0.10 * residual_uncertainty
    )
    return float(min(max(raw_score, 0.0), 1.0))


def priority_tier(score: float, alert_threshold: float) -> str:
    """Classify a scenario score into an operating-review tier."""
    if score >= alert_threshold:
        return "High"
    if score >= alert_threshold * 0.65:
        return "Medium"
    return "Monitor"


def recommended_action(tier: str, scenario: Scenario) -> str:
    """Map a priority tier and scenario into a concise planning action."""
    if tier == "High":
        return f"Pre-review capacity and bike positioning before the {scenario.label.lower()}."
    if tier == "Medium":
        return (
            "Monitor against the previous-week baseline and review during peak hours."
        )
    return "Keep on the watchlist; no immediate rebalancing review from demand alone."


def validate_scenarios(scenarios: Iterable[Scenario]) -> list[Scenario]:
    """Validate scenario definitions before building simulator rows."""
    try:
        scenario_list = list(scenarios)
    except TypeError as exc:
        raise ValueError(
            "Simulator scenarios must be an iterable of Scenario objects."
        ) from exc
    if not scenario_list:
        raise ValueError("At least one simulator scenario is required.")

    seen: set[str] = set()
    for scenario in scenario_list:
        if not isinstance(scenario, Scenario):
            raise ValueError("Simulator scenarios must be Scenario objects.")
        if (
            not isinstance(scenario.name, str)
            or not scenario.name.strip()
            or scenario.name.strip() != scenario.name
        ):
            raise ValueError("Simulator scenario names must be non-empty.")
        if scenario.name in seen:
            raise ValueError(f"Duplicate simulator scenario name: {scenario.name}")
        seen.add(scenario.name)
        if (
            not isinstance(scenario.label, str)
            or not scenario.label.strip()
            or scenario.label.strip() != scenario.label
        ):
            raise ValueError(
                f"Simulator scenario '{scenario.name}' must have a non-empty label."
            )
        validate_finite_number(
            scenario.demand_multiplier,
            field=f"{scenario.name}.demand_multiplier",
        )
        validate_finite_number(
            scenario.weather_pressure,
            field=f"{scenario.name}.weather_pressure",
        )
        validate_finite_number(
            scenario.event_pressure,
            field=f"{scenario.name}.event_pressure",
        )
        validate_finite_number(
            scenario.alert_threshold,
            field=f"{scenario.name}.alert_threshold",
        )
        if scenario.demand_multiplier <= 0:
            raise ValueError(
                f"Simulator scenario '{scenario.name}' needs a positive demand multiplier."
            )
        if scenario.weather_pressure < 0 or scenario.event_pressure < 0:
            raise ValueError(
                f"Simulator scenario '{scenario.name}' pressures cannot be negative."
            )
        if not 0 < scenario.alert_threshold <= 1:
            raise ValueError(
                f"Simulator scenario '{scenario.name}' alert threshold must be in (0, 1]."
            )
    return scenario_list


def select_dashboard_kpis(
    station_summary: dict[str, object],
    multi_month_summary: dict[str, object],
    metrics: pd.DataFrame,
    simulator: pd.DataFrame,
) -> dict[str, object]:
    """Select headline KPIs for the dashboard hero cards."""
    high_alerts = 0
    if not simulator.empty:
        high_alerts = int((simulator["priority_tier"] == "High").sum())
    system_weather_event = metrics[
        (metrics["segment_id"] == "system_total")
        & (metrics["model"] == "weather_event_ridge")
    ]
    system_mae: object = station_summary.get("weather_event_mean_mae", "n/a")
    if not system_weather_event.empty:
        system_mae = system_weather_event["mae"].iloc[0]
    best_model = multi_month_summary.get("best_model", {})
    if not isinstance(best_model, dict):
        best_model = {}
    return {
        "months": multi_month_summary.get("months", "n/a"),
        "hourly_observations": multi_month_summary.get("hourly_observations", "n/a"),
        "station_clusters": station_summary.get("station_clusters", "n/a"),
        "weather_event_mae": system_mae,
        "best_full_year_model": best_model.get("model_label", "n/a"),
        "high_alerts": high_alerts,
    }


def require_columns(df: pd.DataFrame, required: set[str], source_name: str) -> None:
    """Raise a clear error if a source table is missing required columns."""
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"{source_name} is missing required columns: {missing}")


def validate_text_columns(
    df: pd.DataFrame, columns: list[str], *, source_name: str
) -> None:
    """Validate that identifier and label columns contain non-empty strings."""
    for column in columns:
        values = df[column]
        non_string = values.map(lambda value: not isinstance(value, str)).astype(bool)
        blank_string = values.map(
            lambda value: isinstance(value, str) and not value.strip()
        ).astype(bool)
        padded_string = values.map(
            lambda value: isinstance(value, str) and value.strip() != value
        ).astype(bool)
        invalid = values.isna() | non_string | blank_string | padded_string
        if invalid.any():
            raise ValueError(
                f"{source_name} has blank, padded, or non-string values in {column}."
            )


def validate_unique_key(df: pd.DataFrame, key: str, source_name: str) -> None:
    """Validate that a source table key uniquely identifies rows."""
    duplicates = df.loc[df.duplicated(key, keep=False), key]
    if not duplicates.empty:
        preview = preview_values(duplicates.drop_duplicates().astype(str))
        raise ValueError(f"{source_name} has duplicate {key} value(s): {preview}.")


def validate_model_comparison_coverage(comparison: pd.DataFrame) -> None:
    """Validate dashboard model-comparison rows are unique and complete."""
    duplicate_rows = comparison.loc[
        comparison.duplicated(["segment_id", "model"], keep=False),
        ["segment_id", "model"],
    ].drop_duplicates()
    if not duplicate_rows.empty:
        duplicate_keys = [
            f"{row.segment_id}/{row.model}"
            for row in duplicate_rows.itertuples(index=False)
        ]
        raise ValueError(
            "station_cluster_model_metrics.csv has duplicate segment/model "
            f"row(s): {preview_values(duplicate_keys)}."
        )

    expected_models = set(MODEL_COMPARISON_MODELS)
    missing_by_segment = []
    for segment_id, group in comparison.groupby("segment_id"):
        missing_models = sorted(expected_models - set(group["model"]))
        if missing_models:
            missing_by_segment.append(f"{segment_id}: {', '.join(missing_models)}")
    if missing_by_segment:
        raise ValueError(
            "station_cluster_model_metrics.csv is missing dashboard model "
            f"row(s): {preview_values(missing_by_segment)}."
        )


def preview_values(values: Iterable[object], *, limit: int = 5) -> str:
    """Return a compact, deterministic preview for validation errors."""
    items = [str(value) for value in values]
    preview = ", ".join(items[:limit])
    if len(items) > limit:
        preview += f", ... (+{len(items) - limit} more)"
    return preview


def validate_numeric_columns(
    df: pd.DataFrame, columns: list[str], *, source_name: str
) -> None:
    """Validate that required source columns are finite and numeric."""
    for column in columns:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(
                f"{source_name} has nonnumeric or missing values in {column}."
            )
        df[column] = values.astype(float)


def validate_nonnegative_columns(
    df: pd.DataFrame, columns: list[str], *, source_name: str
) -> None:
    """Validate that required source columns are not negative."""
    for column in columns:
        if (df[column] < 0).any():
            raise ValueError(f"{source_name} has negative values in {column}.")


def validate_finite_number(value: float, *, field: str) -> None:
    """Validate a scalar scenario setting is finite."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number.") from exc
    if isinstance(value, bool) or not np.isfinite(numeric_value):
        raise ValueError(f"{field} must be a finite number.")


def validate_positive_integer(value: object, *, field: str) -> int:
    """Validate a scalar setting is a positive integer and return it."""
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer.")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a positive integer.") from exc
    if not np.isfinite(numeric_value) or not numeric_value.is_integer():
        raise ValueError(f"{field} must be a positive integer.")
    integer_value = int(numeric_value)
    if integer_value <= 0:
        raise ValueError(f"{field} must be a positive integer.")
    return integer_value


def safe_ratio(numerator: float, denominator: float) -> float:
    """Divide two numeric values while avoiding zero-denominator failures."""
    if denominator == 0 or pd.isna(denominator):
        return 0.0
    return float(numerator / denominator)


def coerce_float(value: object, default: float = 0.0) -> float:
    """Convert a scalar value to float, returning a default for missing values."""
    if pd.isna(value):
        return default
    return float(value)


def render_html_report(
    *,
    station_summary: dict[str, object],
    multi_month_summary: dict[str, object],
    metrics: pd.DataFrame,
    lift: pd.DataFrame,
    priorities: pd.DataFrame,
    feature_lift: pd.DataFrame,
    simulator: pd.DataFrame,
) -> str:
    """Render the portfolio dashboard as a portable static HTML page."""
    kpis = select_dashboard_kpis(
        station_summary, multi_month_summary, metrics, simulator
    )
    top_priority = priorities.iloc[0].to_dict() if not priorities.empty else {}
    system_lift = lift[lift["segment_id"] == "system_total"]
    system_lift_value = (
        system_lift["mae_lift_pct_vs_previous_week"].iloc[0]
        if not system_lift.empty
        else np.nan
    )
    metrics_table = table_html(
        prepare_model_comparison(metrics),
        columns=["segment_label", "model_label", "mae", "rmse", "wape"],
        rename={
            "segment_label": "Segment",
            "model_label": "Model",
            "mae": "MAE",
            "rmse": "RMSE",
            "wape": "WAPE",
        },
        formatters={
            "MAE": fmt_number,
            "RMSE": fmt_number,
            "WAPE": fmt_percent,
        },
    )
    feature_table = table_html(
        feature_lift,
        columns=[
            "feature_family",
            "segments_improved",
            "segments_evaluated",
            "weighted_lift_pct",
            "best_segment",
            "interpretation",
        ],
        rename={
            "feature_family": "Feature Family",
            "segments_improved": "Segments Improved",
            "segments_evaluated": "Segments Evaluated",
            "weighted_lift_pct": "Weighted Lift",
            "best_segment": "Largest Gain",
            "interpretation": "Interpretation",
        },
        formatters={"Weighted Lift": fmt_signed_percent},
    )
    simulator_table = simulator_table_html(simulator)

    return strip_trailing_whitespace(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Citi Bike Time Series Portfolio Dashboard</title>
  <style>
    :root {{
      --surface: #fbfcfd;
      --panel: #ffffff;
      --ink: #1f2430;
      --muted: #667085;
      --grid: #e6e8f0;
      --blue: #5477c4;
      --green: #71b436;
      --orange: #f0986e;
      --gold: #b8a037;
    }}
    body {{
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font-family: Aptos, Inter, "Segoe UI", Arial, sans-serif;
    }}
    main {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 36px 20px 72px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: clamp(32px, 5vw, 50px);
      line-height: 1.04;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 34px 0 12px;
      font-size: 24px;
      line-height: 1.2;
    }}
    p, li {{
      color: var(--muted);
      font-size: 16px;
      line-height: 1.58;
    }}
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
      padding: 15px;
    }}
    .kpi strong {{
      display: block;
      margin-bottom: 6px;
      font-size: 24px;
      line-height: 1.1;
    }}
    .kpi span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .summary {{
      border-left: 4px solid var(--blue);
      background: #eaf1fe;
      border-radius: 6px;
      padding: 14px 16px;
    }}
    .summary strong {{
      color: var(--ink);
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 10px 0 14px;
    }}
    .controls button {{
      border: 1px solid var(--grid);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
      padding: 8px 11px;
      font: inherit;
      font-size: 14px;
    }}
    .controls button.active {{
      border-color: var(--blue);
      background: #eaf1fe;
      color: var(--blue);
      font-weight: 600;
    }}
    figure {{
      margin: 20px 0;
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
      margin: 12px 0 24px;
    }}
    .data-table th, .data-table td {{
      border-bottom: 1px solid var(--grid);
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    .data-table th {{
      background: #f4f5f7;
      color: var(--ink);
    }}
    .data-table tr:last-child td {{
      border-bottom: 0;
    }}
    .tier-high {{
      color: #8a3a1f;
      font-weight: 700;
    }}
    .tier-medium {{
      color: #736422;
      font-weight: 700;
    }}
    .tier-monitor {{
      color: #386411;
      font-weight: 700;
    }}
    @media (max-width: 780px) {{
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
    <h1>Citi Bike Time Series Portfolio Dashboard</h1>
    <p>
      A reviewer-first surface for the full-year forecasting proof, station
      clusters, feature-family lift, and rebalancing decision simulator.
    </p>
  </header>

  <section class="kpis">
    <div class="kpi"><strong>{fmt_number(kpis["months"])}</strong><span>months profiled</span></div>
    <div class="kpi"><strong>{fmt_number(kpis["hourly_observations"])}</strong><span>hourly observations</span></div>
    <div class="kpi"><strong>{fmt_number(kpis["station_clusters"])}</strong><span>station clusters</span></div>
    <div class="kpi"><strong>{fmt_number(kpis["weather_event_mae"])}</strong><span>system weather/event MAE</span></div>
  </section>

  <section>
    <h2>Decision Context</h2>
    <p class="summary">
      <strong>Recommended decision:</strong> use the weather/event ridge as a
      rebalancing and station-capacity planning watchlist, with previous-week
      and calendar-lag ridge retained as controls. The system-level weather/event
      model improved MAE by {fmt_signed_percent(system_lift_value)} versus the
      previous-week baseline. The top current planning cluster is
      <strong>{html.escape(str(top_priority.get("cluster_label", "n/a")))}</strong>.
    </p>
  </section>

  <section>
    <h2>Scenario Simulator</h2>
    <p>
      The simulator does not claim to dispatch trucks. It ranks station clusters
      for operating review under a few plausible demand-pressure scenarios using
      observed annual scale, model error, WAPE, and baseline lift.
    </p>
    {scenario_buttons(simulator)}
    {simulator_table}
  </section>

  <section>
    <h2>Feature Explainability</h2>
    <p>
      Instead of using in-sample coefficients as proof, this table explains
      feature families by out-of-sample lift. Each family must reduce rolling
      validation error against the simpler model before it earns space in the
      portfolio narrative.
    </p>
    {feature_table}
  </section>

  <section>
    <h2>Model Comparison</h2>
    {metrics_table}
  </section>

  <section>
    <h2>Core Visuals</h2>
    <figure>
      <img src="charts/station_cluster_model_lift.png" alt="Model lift by station cluster">
      <figcaption>Weather/event ridge lift versus the previous-week baseline across the system and station clusters.</figcaption>
    </figure>
    <figure>
      <img src="charts/station_cluster_forecast_example.png" alt="Forecast example for top station cluster">
      <figcaption>Final scored 24-hour forecast trace for the top planning-priority station cluster.</figcaption>
    </figure>
    <figure>
      <img src="charts/multi_month_daily_demand.png" alt="Full-year daily demand">
      <figcaption>Full-year demand pattern that proves the model beyond the original January snapshot.</figcaption>
    </figure>
  </section>

  <section>
    <h2>Source And Limits</h2>
    <ul>
      <li>Source artifacts are generated from public Citi Bike 2024 monthly archives and Open-Meteo historical weather.</li>
      <li>The dashboard target is hourly trip starts, not live bike inventory, dock availability, or actual truck moves.</li>
      <li>Scenario scores are planning indices. They should be calibrated against station capacity and availability snapshots before operational use.</li>
    </ul>
  </section>
</main>
<script>
  const buttons = document.querySelectorAll("[data-scenario-button]");
  const rows = document.querySelectorAll("[data-scenario-row]");
  function setScenario(name) {{
    buttons.forEach((button) => button.classList.toggle("active", button.dataset.scenarioButton === name));
    rows.forEach((row) => {{
      row.style.display = row.dataset.scenarioRow === name ? "" : "none";
    }});
  }}
  if (buttons.length > 0) {{
    setScenario(buttons[0].dataset.scenarioButton);
    buttons.forEach((button) => button.addEventListener("click", () => setScenario(button.dataset.scenarioButton)));
  }}
</script>
</body>
</html>"""
    )


def prepare_model_comparison(metrics: pd.DataFrame) -> pd.DataFrame:
    """Return the model-comparison table without dropping evaluated segments."""
    required = {
        "segment_id",
        "segment_label",
        "model",
        "model_label",
        "mae",
        "rmse",
        "wape",
    }
    require_columns(metrics, required, "station_cluster_model_metrics.csv")
    validate_text_columns(
        metrics,
        ["segment_id", "segment_label", "model", "model_label"],
        source_name="station_cluster_model_metrics.csv",
    )
    validate_numeric_columns(
        metrics,
        ["mae", "rmse", "wape"],
        source_name="station_cluster_model_metrics.csv",
    )
    validate_nonnegative_columns(
        metrics,
        ["mae", "rmse", "wape"],
        source_name="station_cluster_model_metrics.csv",
    )
    model_order = {model: index for index, model in enumerate(MODEL_COMPARISON_MODELS)}
    comparison = metrics[metrics["model"].isin(MODEL_COMPARISON_MODELS)].copy()
    if comparison.empty:
        raise ValueError(
            "station_cluster_model_metrics.csv has no rows for the dashboard "
            "model comparison models."
        )
    if "system_total" not in set(comparison["segment_id"]):
        raise ValueError(
            "station_cluster_model_metrics.csv is missing the system_total "
            "dashboard segment."
        )
    validate_model_comparison_coverage(comparison)
    comparison["segment_order"] = comparison["segment_id"].map(segment_sort_key)
    comparison["model_order"] = comparison["model"].map(model_order)
    return (
        comparison.sort_values(["segment_order", "model_order"])
        .drop(columns=["segment_order", "model_order"])
        .reset_index(drop=True)
    )


def segment_sort_key(segment_id: object) -> tuple[int, str]:
    """Sort system total first, then station clusters by numeric suffix."""
    value = str(segment_id)
    if value == "system_total":
        return (0, value)
    cluster_match = CLUSTER_SEGMENT_PATTERN.match(value)
    if cluster_match:
        return (1, f"{int(cluster_match.group(1)):06d}")
    return (2, value)


def scenario_buttons(simulator: pd.DataFrame) -> str:
    """Render simulator scenario filter buttons."""
    if simulator.empty:
        return ""
    scenarios = simulator[["scenario", "scenario_label"]].drop_duplicates()
    buttons = [
        (
            f'<button type="button" data-scenario-button="{html.escape(str(row.scenario))}">'
            f"{html.escape(str(row.scenario_label))}</button>"
        )
        for row in scenarios.itertuples(index=False)
    ]
    return '<div class="controls">' + "".join(buttons) + "</div>"


def simulator_table_html(simulator: pd.DataFrame) -> str:
    """Render simulator rows with scenario attributes for client-side filters."""
    if simulator.empty:
        return '<p class="summary">No simulator rows were available.</p>'
    headers = [
        "Cluster",
        "Tier",
        "Risk Score",
        "Expected Hourly Starts",
        "WAPE",
        "Lift vs Previous Week",
        "Action",
    ]
    body_rows = []
    for row in simulator.itertuples(index=False):
        tier_class = priority_tier_class(row.priority_tier)
        body_rows.append(
            f'<tr data-scenario-row="{html.escape(str(row.scenario))}">'
            f"<td>{html.escape(str(row.cluster_label))}</td>"
            f'<td class="{tier_class}">{html.escape(str(row.priority_tier))}</td>'
            f"<td>{fmt_number(row.risk_score, digits=2)}</td>"
            f"<td>{fmt_number(row.expected_hourly_starts, digits=1)}</td>"
            f"<td>{fmt_percent(row.weather_event_wape)}</td>"
            f"<td>{fmt_signed_percent(row.lift_vs_previous_week)}</td>"
            f"<td>{html.escape(str(row.recommended_action))}</td>"
            "</tr>"
        )
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    return (
        '<table class="data-table"><thead><tr>'
        + header_html
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def priority_tier_class(tier: object) -> str:
    """Return a controlled CSS class for a simulator priority tier."""
    tier_classes = {
        "High": "tier-high",
        "Medium": "tier-medium",
        "Monitor": "tier-monitor",
    }
    return tier_classes.get(str(tier), "tier-monitor")


def table_html(
    df: pd.DataFrame,
    *,
    columns: list[str],
    rename: dict[str, str],
    formatters: dict[str, object] | None = None,
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


def write_outputs(
    output_dir: Path,
    feature_lift: pd.DataFrame,
    simulator: pd.DataFrame,
    dashboard: str,
) -> None:
    """Write generated portfolio dashboard artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    feature_lift.to_csv(output_dir / "portfolio_feature_family_lift.csv", index=False)
    simulator.to_csv(output_dir / "portfolio_decision_simulator.csv", index=False)
    (output_dir / "portfolio_dashboard.html").write_text(dashboard, encoding="utf-8")


def strip_trailing_whitespace(text: str) -> str:
    """Normalize generated text by removing trailing whitespace."""
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def fmt_number(value: object, digits: int = 0) -> str:
    """Format a numeric value with thousands separators."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value):,.{digits}f}"


def fmt_percent(value: object, digits: int = 1) -> str:
    """Format a decimal ratio as a percentage."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def fmt_signed_percent(value: object, digits: int = 1) -> str:
    """Format a decimal ratio as a signed percentage."""
    if pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:+.{digits}f}%"


if __name__ == "__main__":
    main()
