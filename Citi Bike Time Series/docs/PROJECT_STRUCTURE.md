# Project Structure

This document explains how the packaged project is organized.

## Root Files

| File | Purpose |
| --- | --- |
| `README.md` | Main project overview, headline measures, run commands, and caveats |
| `requirements.txt` | Python dependencies needed to run the scripts |
| `.gitignore` | Keeps raw downloaded data and local cache files out of Git |

## `src/`

| File | Purpose |
| --- | --- |
| `citibike_time_series_profile.py` | Main data pipeline, chart generation, and first-pass report |
| `citibike_decision_report.py` | Builds the decision-ready portfolio report from generated outputs |
| `citibike_time_series_showcase.py` | Builds expanded time-series diagnostics, charts, and showcase report from the hourly profile |
| `citibike_multi_month_proof.py` | Streams multiple monthly archives, builds a full-year hourly panel, and evaluates rolling forecast origins |

## `outputs/`

This folder contains generated reports, generated tables, summary data, and
chart assets.

Important files:

- `report.html`
- `decision_report.html`
- `time_series_showcase.html`
- `multi_month_proof.html`
- `profile_summary.json`
- `hourly_profile.csv`
- `forecast_backtest_metrics.csv`
- `forecast_backtest_scored.csv`
- `rolling_backtest_metrics.csv`
- `rolling_backtest_origin_metrics.csv`
- `rolling_backtest_scored.csv`
- `autocorrelation_profile.csv`
- `lag_feature_correlations.csv`
- `decomposition_components.csv`
- `time_series_showcase_metrics.csv`
- `time_series_showcase_coverage.csv`
- `multi_month_proof_summary.json`
- `multi_month_hourly_profile.csv`
- `multi_month_daily_profile.csv`
- `multi_month_source_inventory.csv`
- `multi_month_model_metrics.csv`
- `multi_month_origin_metrics.csv`
- `multi_month_backtest_scored.csv`
- `multi_month_top_stations.csv`
- `anomaly_hours.csv`
- `seasonality_profile.csv`
- `top_stations.csv`
- `member_mix.csv`
- `bike_mix.csv`

## `outputs/charts/`

Static PNG charts used by the HTML reports:

- `daily_demand.png`
- `seasonality_heatmap.png`
- `forecast_backtest.png`
- `top_stations.png`
- `autocorrelation_profile.png`
- `lag_feature_correlations.png`
- `rolling_backtest_mae.png`
- `decomposition_proxy.png`
- `seasonal_residual_distribution.png`
- `multi_month_daily_demand.png`
- `multi_month_monthly_volume.png`
- `multi_month_model_mae.png`
- `multi_month_origin_mae.png`
- `multi_month_forecast_example.png`

## `data/sample_outputs/`

Lightweight sample outputs for quick review. This is where small generated
tables can live without including the raw downloaded ZIP file.

## `docs/`

Documentation for reviewers:

| File | Purpose |
| --- | --- |
| `MEASURES.md` | Metric definitions and current values |
| `MULTI_MONTH_PROOF.md` | Full-year validation design, model comparison, outputs, and interview defense |
| `TIME_SERIES_SHOWCASE.md` | Time-series concept map, interview framing, and extension path |
| `CHART_MAP.md` | Visual purpose, chart family, and quality checks for each chart |
| `METHODOLOGY.md` | Data processing, modeling, validation, and limitations |
| `DATA_DICTIONARY.md` | Output column definitions |
| `MODEL_CARD.md` | Forecast baseline purpose, scope, results, and risks |
| `PORTFOLIO_WRITEUP.md` | Project narrative, resume bullets, and portfolio card copy |
| `PUBLISHING_CHECKLIST.md` | Pre-push review checklist |
| `ROADMAP.md` | Future project improvements |

## `work/`

Created by the pipeline at runtime. It stores cached downloaded files and is
ignored by Git.
