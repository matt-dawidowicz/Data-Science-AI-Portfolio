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
- Station ID metadata and deterministic station-cluster grouping
- Station-cluster forecasts for system total plus top demand clusters
- Weather, holiday, and event features tested in rolling validation
- Rebalancing/capacity-planning priority table
- Portfolio dashboard for reviewer navigation
- Scenario simulator for cluster-level planning review
- Feature-family lift explanation based on out-of-sample validation
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

## Completed Upgrade: Station-Cluster Forecasting

The project now includes the next high-value upgrade:

- 120 top station IDs clustered from observed station metadata
- 6 station clusters plus the system total as modeled targets
- 99.93% station ID coverage across fixed-window modeled starts
- 8,784 hourly weather observations joined to the model panel
- holiday windows and selected public event windows
- previous-week, calendar-lag ridge, and weather/event ridge comparison
- weather/event ridge wins for the system total and all 6 station clusters
- rebalancing/capacity-planning recommendation and priority table

This still does not make the project an inventory-control model. It forecasts
trip-start demand by cluster, which is a useful planning signal but not the same
as live bike availability, dock availability, or truck routing.

## Completed Upgrade: Portfolio Dashboard And Simulator

The project now includes a reviewer-first portfolio layer:

- `outputs/portfolio_dashboard.html`
- `outputs/portfolio_decision_simulator.csv`
- `outputs/portfolio_feature_family_lift.csv`
- `docs/CASE_STUDY.md`
- `docs/DASHBOARD_AND_SIMULATOR.md`
- `docs/LIMITATIONS.md`

This layer turns the forecasting artifacts into a compact story for hiring
reviewers. It shows the full-year proof, cluster-level model lift, a
feature-family explanation, and scenario-based rebalancing review tiers.

The simulator is intentionally not an optimizer. It is a planning index built
from demand scale, model error, WAPE, and lift versus baseline. A production
optimizer still needs capacity, availability, truck, and service-level data.

## High-Value Next Work

### 1. Add Capacity And Availability Context

Why it matters:

- Rebalancing decisions depend on available bikes and docks, not just starts.
- Station capacity turns demand pressure into a measurable operating risk.
- Availability snapshots would let the model predict stockout or full-dock risk.

Measures to add:

- Station capacity
- Available bikes
- Available docks
- Stockout minutes
- Full-dock minutes
- Starts per available bike
- Demand pressure per dock
- Forecasted risk by cluster

### 2. Calibrate A Rebalancing Watchlist

Why it matters:

- The current report ranks planning priorities, but it does not set an alert
  threshold.
- A decision-ready operating model should say which clusters deserve action and
  how confident the alert is.

Measures to add:

- Alert threshold
- Precision and recall against stockout/full-dock outcomes
- False-alert rate
- Missed-risk rate
- Peak-hour alert quality
- Event-window alert quality

### 3. Add Stronger Model And Uncertainty Layers

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
- Cluster-level interval width

### 4. Make Anomalies Explainable

Why it matters:

- An anomaly detector is more useful when it helps explain what happened.

Context to add:

- Severe weather warnings
- Local events
- Station outages
- System-wide availability
- Public status feeds
- Rebalancing activity

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
applied forecasting and operations case study. The current station-cluster
layer answers the first half of that question; the next version should prove
the operational action with capacity and availability outcomes.
