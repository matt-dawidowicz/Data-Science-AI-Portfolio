# Limitations And Failure Modes

This page makes the project stronger by being explicit about what the current
forecasting layer does not prove.

## Target Limitation

The model forecasts hourly trip starts. It does not forecast:

- available bikes,
- available docks,
- station capacity,
- stockout minutes,
- full-dock minutes,
- actual truck routes,
- unmet rider demand.

This matters because a demand spike is only an operating problem when it
interacts with inventory and station capacity.

## Data Coverage Limitation

The project now uses all 12 months of 2024, which is a much stronger proof than
the original January-only profile. It is still one calendar year. A production
model should test multiple years to check regime changes, station-network
changes, extreme weather, and long-run recovery or growth patterns.

## Station Metadata Limitation

Station clusters are built from observed station IDs, observed names, and
observed coordinates in trip-history records. This is stronger than station
names alone, but it is not the same as an official slowly changing station
dimension.

Known risk:

- stations can move,
- stations can be renamed,
- station capacity can change,
- stations can open or close,
- observed coordinates can vary slightly by trip.

## Weather Limitation

The weather/event ridge uses historical observed weather in the proof layer.
An operating forecast would need weather information that is available before
the forecast horizon, such as forecasted precipitation and temperature.

The project treats weather features as forecast inputs that must be evaluated
out of sample. It does not claim that weather correlations are causal.

## Event Calendar Limitation

The event features are intentionally compact. They include federal holiday
windows and selected public event windows. They are not a complete New York
City events database, and they do not include service outages, transit
incidents, protests, street closures, or neighborhood-level events.

## Model Limitation

The ridge models are transparent benchmarks, not a claim of best-possible
forecast accuracy. They are useful because they show feature discipline and
baseline comparison, but stronger candidates could include:

- gradient-boosted lag-feature models,
- hierarchical or grouped forecasting models,
- calibrated quantile models,
- SARIMAX-style exogenous regressions,
- models trained directly on availability or stockout outcomes.

## Uncertainty Limitation

The current reports focus on point forecast error. They do not yet provide
calibrated prediction intervals or alert-threshold precision/recall.

Before using the project as an alerting system, the next version should
measure:

- interval coverage,
- false-alert rate,
- missed-risk rate,
- precision and recall by cluster,
- precision and recall during peak hours,
- precision and recall during event/weather windows.

## Simulator Limitation

The portfolio decision simulator is a planning index. It ranks station clusters
for review under scenario assumptions using annual scale, model error, WAPE,
and baseline lift.

It should not be presented as an operations optimizer. A true optimizer would
need:

- station capacity,
- current bike inventory,
- available docks,
- truck capacity,
- travel time,
- service-level targets,
- a cost function.

## Honest Portfolio Claim

The defensible claim is:

> I built a reproducible, full-year, station-cluster time-series forecasting
> workflow that evaluates richer weather/event features against transparent
> baselines and turns the result into a rebalancing/capacity-planning watchlist.

The project should not claim to be a live Citi Bike operations model.
