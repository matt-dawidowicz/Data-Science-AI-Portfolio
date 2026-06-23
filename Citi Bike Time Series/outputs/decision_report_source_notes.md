# Citi Bike Decision Report Source Notes

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

The decision is how to evolve the Citi Bike time-series showcase. The best-supported recommendation is to extend the project into a multi-month, station-aware forecasting and anomaly workflow. The current evidence is strong for a portfolio profile because it has public raw data, reproducible transformation code, hourly outputs, forecast backtest outputs, and chart assets. It is limited for live operational decisions because it covers one winter month and lacks official station metadata, internal operations context, and rolling validation.

## Chart Map

| Report Segment | Visual | Chart Family | Supports | Source |
| --- | --- | --- | --- | --- |
| Demand pattern | `charts/daily_demand.png` | Trend | January demand has enough temporal movement for time-series profiling | `hourly_profile.csv` |
| Demand pattern | `charts/seasonality_heatmap.png` | Heatmap | Weekday/hour structure is the core modeling signal | `seasonality_profile.csv` |
| Baseline | `charts/forecast_backtest.png` | Trend with benchmark | Calendar profile creates the first forecast benchmark | `forecast_backtest_scored.csv` |
| Operational texture | `charts/top_stations.png` | Ranked horizontal bars | Station starts create a practical extension path | `top_stations.csv` |

## Key Validation Checks

- Valid-trip filter came from `citibike_time_series_profile.py`: parseable start/end timestamps and duration from 1 to 240 minutes.
- Best baseline by MAE: `calendar_profile` with MAE 796.1.
- Previous-day MAE: 1001.0; previous-week MAE: 871.6.
- Top 10 station share of valid trips: 0.0325.
- Weather correlations were treated as descriptive only.

## Omitted Or Deferred Evidence

- No live warehouse, dashboard, or team-communication source was used because the current project is based on public data and local artifacts.
- No new model was fit in this report; the recommendation is to extend the evidence base before adding a stronger model.
- No station-level longitudinal conclusion is made because current station outputs use names rather than stable station IDs.
