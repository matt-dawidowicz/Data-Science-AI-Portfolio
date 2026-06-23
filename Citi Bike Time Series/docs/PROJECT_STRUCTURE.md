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

## `outputs/`

This folder contains generated reports, generated tables, summary data, and
chart assets.

Important files:

- `report.html`
- `decision_report.html`
- `profile_summary.json`
- `hourly_profile.csv`
- `forecast_backtest_metrics.csv`
- `forecast_backtest_scored.csv`
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

## `data/sample_outputs/`

Lightweight sample outputs for quick review. This is where small generated
tables can live without including the raw downloaded ZIP file.

## `docs/`

Documentation for reviewers:

| File | Purpose |
| --- | --- |
| `MEASURES.md` | Metric definitions and current values |
| `METHODOLOGY.md` | Data processing, modeling, validation, and limitations |
| `DATA_DICTIONARY.md` | Output column definitions |
| `MODEL_CARD.md` | Forecast baseline purpose, scope, results, and risks |
| `PORTFOLIO_WRITEUP.md` | Project narrative, resume bullets, and portfolio card copy |
| `PUBLISHING_CHECKLIST.md` | Pre-push review checklist |
| `ROADMAP.md` | Future project improvements |

## `work/`

Created by the pipeline at runtime. It stores cached downloaded files and is
ignored by Git.
