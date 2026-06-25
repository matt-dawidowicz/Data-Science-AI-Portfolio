# Portfolio Case Study

## One-Sentence Summary

This project turns public Citi Bike trip-history data into a full-year hourly
demand forecasting system, then extends the forecast to station clusters so the
results support a concrete rebalancing and capacity-planning decision.

## Business Question

Which parts of the Citi Bike network are likely to see demand pressure in the
next operating window, and can a richer weather/event model beat simple
previous-week and calendar-lag baselines?

The project is framed around rebalancing and station-capacity planning because
that is where a demand forecast becomes useful. A citywide forecast is helpful,
but a cluster-level forecast tells an operator where to look first.

## Data

The project uses public Citi Bike monthly trip-history archives for January
through December 2024. The target is hourly valid trip starts. A trip is kept
when start and end timestamps are parseable and the duration is between 1 and
240 minutes.

The full-year layer profiles:

- 12 monthly public archives
- 44.25M valid trip rows
- 8,784 hourly observations
- zero missing hourly periods
- 120 top station IDs grouped into 6 station clusters
- 8,784 hourly weather observations
- holiday and selected event-window features

## Method

The project is built in layers:

1. The January profile proves the basic time-series mechanics: hourly
   resampling, regular indexing, commute seasonality, weather context,
   anomalies, and baseline forecasts.
2. The full-year proof checks whether those ideas survive a much larger panel
   with rolling validation across 2024.
3. The station-cluster layer turns aggregate demand into operational demand
   pools using station IDs and observed station metadata.
4. The portfolio dashboard summarizes the result for reviewers and includes a
   scenario simulator for cluster-level planning review.

## Models

The project intentionally starts with transparent baselines:

- previous day
- previous week
- hour-of-day profile
- weekday/hour profile
- seasonal lag blend
- calendar + lag ridge
- weather/event ridge

The richer model is not accepted because it is more complex. It is accepted
only if it improves out-of-sample rolling validation error.

## Validation

The full-year and station-cluster layers use weekly 24-hour rolling origins
after a 60-day training warmup. This makes the validation harder to game than a
single holdout because each origin trains only on prior observations and scores
a future 24-hour window.

Primary metric: MAE in rides per hour.

Secondary metrics: RMSE, WAPE, MAPE, origin-level win rate, and segment-level
model lift.

## Results

The full-year aggregate proof found that the calendar + lag ridge model had the
best aggregate MAE, beating previous-week and previous-day baselines across the
2024 rolling origins.

The station-cluster upgrade found that the weather/event ridge model improved
system MAE to about 711 rides per hour, beating previous week by 22.7% and the
calendar + lag ridge by 5.2%. It also beat both baselines across all 6 station
clusters in this run.

## Decision Output

The project ties the model to rebalancing and station-capacity planning. The
decision artifacts are:

- `outputs/station_cluster_capacity_priorities.csv`
- `outputs/portfolio_decision_simulator.csv`
- `outputs/portfolio_dashboard.html`

These outputs rank station clusters for operating review. They do not dispatch
trucks or estimate live inventory.

## What This Proves

This project demonstrates that I can:

- acquire and process large public datasets,
- define a clean time-series target,
- preserve a regular hourly panel,
- build leakage-aware lag and calendar features,
- compare transparent baselines before using richer models,
- evaluate with rolling-origin validation,
- extend aggregate forecasts to grouped time series,
- add weather and event features without treating them as causal proof,
- write portfolio documentation that explains both value and limits.

## Production Next Step

The next production step would join station capacity, live bike availability,
available docks, and rebalancing activity. That would let the project shift
from forecasting trip starts to predicting stockout or full-dock risk.
