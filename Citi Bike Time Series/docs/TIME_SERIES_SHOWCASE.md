# Time-Series Showcase Guide

This guide explains how the Citi Bike project demonstrates time-series
practice. It is designed for a portfolio reviewer who wants to see more than a
single forecast chart.

## Showcase Positioning

The project should be framed as:

```text
Time-series demand profiling, baseline forecasting, and validation for public
urban mobility data.
```

The strongest message is not that a complex model was forced onto one month of
data. The stronger message is that the project builds the full analytical
foundation a responsible forecast needs before model complexity.

## Reviewer Promise

This project should be judged on analytical discipline:

- the target is defined before modeling
- the time index is checked before lag features are used
- simple baselines are established before stronger models are recommended
- rolling validation is separated from a single holdout
- limitations are visible instead of hidden

That is the proof this version is meant to provide.

## What The Project Demonstrates

| Area | Current Artifact | Status | What It Shows |
| --- | --- | --- | --- |
| Regular time index | `outputs/hourly_profile.csv` | Implemented | A fixed hourly panel with missing-hour and duplicate-hour checks |
| Resampling | `src/citibike_time_series_profile.py` | Implemented | Raw trip starts aggregated to hourly and daily demand |
| Calendar features | `outputs/hourly_profile.csv` | Implemented | Hour, weekday, weekend, and holiday features |
| Seasonality | `outputs/seasonality_profile.csv` | Implemented | Weekday/hour commute structure and weekend differences |
| Smoothing | `outputs/decomposition_components.csv` | Implemented | Rolling 24-hour and 168-hour trend columns |
| Decomposition | `outputs/decomposition_components.csv` | Implemented | Trend proxy, weekday/hour expected value, and seasonal residual |
| Autocorrelation | `outputs/autocorrelation_profile.csv` | Implemented | Short-memory, daily, and weekly lag structure |
| Lag features | `outputs/lag_feature_correlations.csv` | Implemented | Candidate lag and rolling features ranked before modeling |
| Exogenous features | `outputs/hourly_profile.csv` | Implemented | Weather joined at hourly grain |
| Baseline forecasts | `outputs/forecast_backtest_metrics.csv` | Implemented | Previous-day, previous-week, and calendar-profile benchmarks |
| Rolling validation | `outputs/rolling_backtest_metrics.csv` | Implemented | Daily rolling 24-hour forecast origins |
| Error metrics | Forecast metric CSVs | Implemented | MAE, RMSE, MAPE, mean actual, and benchmark comparison |
| Residual analysis | `outputs/anomaly_hours.csv` | Implemented | Seasonal residuals and anomaly candidates |
| Hierarchical modeling | `outputs/top_stations.csv` | Extension documented | Path from aggregate demand to station-cluster forecasts |
| Governance | `docs/MODEL_CARD.md` | Implemented | Scope, caveats, and responsible interpretation |

## New Showcase Script

Run:

```bash
python src/citibike_time_series_showcase.py
```

The script reads the existing generated hourly profile and creates:

- `outputs/time_series_showcase.html`
- `outputs/time_series_showcase_metrics.csv`
- `outputs/time_series_showcase_coverage.csv`
- `outputs/autocorrelation_profile.csv`
- `outputs/lag_feature_correlations.csv`
- `outputs/rolling_backtest_metrics.csv`
- `outputs/rolling_backtest_origin_metrics.csv`
- `outputs/rolling_backtest_scored.csv`
- `outputs/decomposition_components.csv`
- additional PNG charts under `outputs/charts/`

It does not redownload the raw Citi Bike archive. It depends on the existing
profile outputs, so run `citibike_time_series_profile.py` first if the output
folder is empty.

## Concepts To Talk Through In An Interview

### 1. Grain And Index

The raw event data is not a time series until it is transformed into a regular
hourly panel. The project makes the target explicit:

```text
rides = count(valid trip starts by hour)
```

The fixed January panel has 744 hourly observations. This allows forecast
features, backtests, and missing-period checks to be defined consistently.

### 2. Seasonality Before Modeling

The project uses weekday and hour-of-day structure before heavier models. This
is important because urban mobility demand is highly calendar-driven. The
weekday/hour profile is interpretable and becomes both:

- a forecast baseline
- an expected-value benchmark for anomaly candidates

### 3. Autocorrelation And Lag Features

The autocorrelation profile answers a basic modeling question:

```text
Which historical values are likely to carry signal for future demand?
```

The lag feature table then turns that into a practical feature screen:

- short-memory lags
- daily lags
- weekly lags
- rolling means
- weather fields

This is a clean way to explain why a future model would include lagged demand
features rather than blindly adding everything.

### 4. Rolling-Origin Validation

The original report includes a single Jan. 25-31 holdout. The showcase layer
adds daily rolling 24-hour forecast origins. This demonstrates a stronger
validation habit:

```text
train on history before each origin -> forecast next 24 hours -> score errors
```

The current project still has only one winter month, but rolling origins make
the evaluation logic more portfolio-worthy.

Why the rolling result can differ from the Jan. 25-31 holdout:

- the rolling test uses multiple 24-hour windows
- the original holdout uses one 168-hour block
- each split contains a different mix of weekdays, weather, and demand levels
- the right interpretation is benchmark sensitivity, not model contradiction

### 5. Decomposition And Residual Thinking

The decomposition output is intentionally labeled as a proxy. It separates:

- actual hourly rides
- rolling trend
- weekday/hour expected demand
- seasonal residual

This is enough to show the reasoning pattern behind trend, seasonality, and
anomaly detection without overstating a formal STL or production-grade
decomposition.

## What Not To Overclaim

Do not claim this is a production forecast. The current version is a showcase
of method and judgment. Important limits:

- one winter month
- no annual seasonality
- no station IDs in the generated station output
- weather correlations are descriptive
- anomaly candidates lack event, outage, and operations context
- residual bands are not calibrated prediction intervals

## Short Interview Defense

If asked why this project is useful before adding a machine-learning model:

```text
I wanted to show the forecast foundation first. The project proves the hourly
target is well defined, the panel is regular, the series has daily and weekly
structure, and transparent baselines can be evaluated without leakage. A
stronger model is only meaningful after it beats those baselines across more
history.
```

If asked what you would do next:

```text
I would extend the archive pull to 12-24 months, add station IDs, run monthly
rolling-origin validation, and compare a lag-feature model against the current
baselines. I would judge the model by error stability across seasons and by
whether it improves a concrete decision such as rebalancing or peak-hour
planning.
```

## Best Next Portfolio Upgrade

The next major version should extend the public archive pull to 12-24 months,
then rerun the same showcase pattern at a larger scale:

1. Rolling monthly and weekly validation windows
2. Yearly seasonality and holiday effects
3. Station IDs and station metadata
4. Station-cluster panel forecasts
5. One stronger model compared against the transparent baselines
