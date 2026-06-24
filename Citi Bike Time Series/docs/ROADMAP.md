# Roadmap

This roadmap separates publish-now improvements from deeper future work.

## Publish-Ready Now

The project is ready to publish as a first-pass analytics case study after a
final local review. It already includes:

- Reproducible Python pipeline
- Public data source
- Data quality filtering
- Hourly demand table
- Seasonality profile
- Autocorrelation profile
- Lag feature screening
- Decomposition-style trend, seasonal expected value, and residual table
- Baseline forecast backtest
- Rolling-origin baseline validation
- Full-2024 rolling-origin forecast proof
- Calendar + lag ridge benchmark against transparent baselines
- Anomaly candidate table
- Charts
- HTML reports
- Measure documentation
- Methodology documentation
- Model caveats

## Completed Upgrade: Full-2024 Proof

The project now includes the first high-value upgrade:

- 12 public monthly archives for Jan.-Dec. 2024
- 44.25M valid rows
- 8,784 hourly observations
- zero missing hourly periods
- 44 weekly 24-hour rolling forecast origins
- previous-day, previous-week, calendar-profile, blend, and ridge comparisons
- full-year proof report and charts

This does not make the project production-ready, but it makes the portfolio
claim much stronger than the original one-month profile.

## High-Value Next Work

### 1. Add Station Metadata

Why it matters:

- Station names can change.
- Station IDs are needed for longitudinal analysis.
- Capacity and location make forecasts more operational.

Measures to add:

- Station ID
- Latitude and longitude
- Station capacity
- Active station days
- Starts per station-day
- Station-cluster demand
- Station-cluster forecast error
- Cross-station spatial lag features

### 2. Build Station-Cluster Forecasts

Why it matters:

- Aggregate demand is useful for a portfolio story.
- Station-cluster demand is closer to rebalancing and operations.

Measures to add:

- Cluster hourly rides
- Cluster share of total rides
- Cluster forecast error
- Peak-hour cluster load
- Error by cluster and hour

### 3. Add Weather, Event, Or Stronger Model Features

Candidate models:

- SARIMAX with calendar and weather features
- Gradient-boosted lag-feature model
- Regularized regression with lag, calendar, weather, and event features
- Prophet-style additive baseline if the goal is explainable trend and
  seasonality comparison

Measures to add:

- Rolling holdout MAE
- Rolling holdout RMSE
- Error by hour of day
- Error by weekday
- Error by weather condition
- Baseline improvement percentage
- Prediction interval coverage
- Error stability across seasons

### 4. Make Anomalies Explainable

Why it matters:

- An anomaly detector is more useful when it helps explain what happened.

Context to add:

- Severe weather warnings
- Local events
- Station outages
- System-wide availability
- Public status feeds

Measures to add:

- Expected rides
- Actual rides
- Absolute gap
- Percent gap
- Robust z-score
- Context category
- Follow-up status

## Time-Series Concepts To Keep Visible

As the project grows, keep these concepts visible in the repository rather than
burying them inside code:

- Time index regularity
- Resampling and aggregation
- Missing-period handling
- Calendar features
- Trend and smoothing
- Daily, weekly, and yearly seasonality
- Autocorrelation and partial autocorrelation
- Lag feature selection
- Exogenous regressors
- Rolling-origin validation
- Baseline comparison
- Residual analysis
- Prediction intervals
- Hierarchical or grouped time series
- Model cards and caveats

## Long-Term Version

A strong final version would answer:

> Which station clusters are likely to exceed expected demand in the next 24
> hours, and what operational action should be taken?

That version would shift the project from descriptive portfolio profile to an
applied forecasting and operations case study.
