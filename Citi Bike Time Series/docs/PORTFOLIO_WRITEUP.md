# Portfolio Writeup

This document gives a polished project narrative for a portfolio page,
interview discussion, or README summary.

## Project Title

Citi Bike Demand Forecasting: Station-Cluster Time-Series Forecasting

## One-Line Summary

Built a reproducible time-series forecasting showcase from public Citi Bike
archives, starting with a January methods layer and expanding to a full-2024
proof with 44.25M valid trips, 8,784 hourly observations, 44 rolling forecast
origins, transparent baselines, a calendar-lag ridge benchmark, and a
station-cluster forecasting layer for rebalancing/capacity planning.

## Portfolio Category

Time Series Forecasting / Urban Mobility Analytics

## Problem Framing

Citi Bike trip activity has strong temporal patterns, but a useful forecasting
showcase needs to prove those patterns before introducing complex models. This
project starts with a clean January 2024 hourly panel, defines valid trip-start
metrics, builds calendar and weather features, evaluates simple baselines, then
extends the aggregate proof across all of 2024 with rolling validation. The
latest layer moves from systemwide demand to station-cluster demand so the
forecast supports a concrete operating decision.

## What I Built

- A Python pipeline that downloads and validates public Citi Bike trip-history
  data.
- An hourly demand profile with calendar, holiday, weekend, and weather
  features.
- A weekday/hour seasonality profile that explains the commute pattern.
- Autocorrelation and lag-feature screens to identify candidate forecasting
  signal.
- Baseline forecasts using previous-day, previous-week, and weekday/hour
  calendar-profile models.
- Daily rolling-origin 24-hour backtests for stronger validation practice.
- A full-2024 proof layer that streams 12 monthly archives and builds a
  complete leap-year hourly panel.
- Weekly rolling 24-hour validation from Mar. 1 through Dec. 27, 2024.
- A calendar-lag ridge model compared against previous-day, previous-week,
  hour-of-day, weekday/hour, and blend baselines.
- Stable station groups built from station IDs, observed station names, and
  observed coordinates.
- A station-cluster hourly panel for the system total plus 6 top demand
  clusters.
- Weather, holiday, and major-event features evaluated inside the rolling
  validation loop.
- A weather/event ridge model compared against previous-week and calendar-lag
  ridge baselines for every segment.
- A rebalancing/capacity-planning priority table that turns forecast output
  into a decision frame.
- A decomposition-style output that separates rolling trend, seasonal expected
  demand, and residual movement.
- Anomaly candidates based on deviations from the weekday/hour profile.
- Static report visuals and five HTML reports: profile, recommendation,
  time-series showcase, multi-month proof, and station-cluster forecast reports.
- An expanded time-series showcase report that maps each time-series concept to
  a concrete artifact.
- Documentation for measures, methodology, outputs, model behavior, caveats,
  and publishing readiness.

## Business Interpretation

The project shows that the first useful signal is not a black-box model. It is
the calendar structure of demand. Rush-hour volume averaged 2.23x off-hour
volume, weekends averaged 0.71x weekday hourly volume, and the calendar-profile
baseline beat weaker baselines on MAE over the Jan. 25-31 holdout.

The full-year layer confirms that the project can move beyond a compact methods
demo. The calendar-lag ridge model reached 750 MAE across 44 rolling origins,
beating previous-week and previous-day baselines on aggregate MAE. That suggests
the next version should focus on station-aware operations rather than simply
adding model complexity.

The station-cluster layer makes that next step real. It clusters the top 120
station IDs into 6 demand pools, joins full-year weather and event features,
and shows that the weather/event ridge model beats both the previous-week and
calendar-lag ridge baselines for the system total and all 6 clusters. The
highest-priority planning cluster is Cluster 01 - W 21 St & 6 Ave area, with
3.97M annual starts and 71.7 MAE under the weather/event model.

## Key Results

- 1,886,109 valid trips after timestamp and duration filtering.
- 744 hourly observations in the fixed January panel.
- 1,885,763 fixed-window trip starts.
- 60,831 average daily rides.
- 8,635 rides in the peak hour.
- 2.23x rush/off-hour ratio.
- Calendar-profile baseline MAE: 796 rides per hour.
- Top 10 stations represented 3.25% of valid trip starts.
- 44,247,816 valid trips in the full-2024 proof layer.
- 8,784 hourly observations with 0 missing hours in the full-year panel.
- 44 weekly rolling forecast origins from Mar. 1-Dec. 27, 2024.
- Calendar + lag ridge full-year MAE: 750 rides per hour.
- Previous-week full-year MAE: 918 rides per hour.
- 120 top station IDs grouped into 6 station clusters.
- 99.93% of valid rows had a usable station ID.
- Weather/event ridge system MAE: 711 rides per hour.
- Weather/event ridge improved system MAE by 22.7% versus previous week and
  5.2% versus calendar-lag ridge.
- Weather/event ridge beat both baselines for all 6 station clusters.

## Technical Skills Demonstrated

- Python data processing with pandas and NumPy
- Chunked CSV processing from a large public ZIP archive
- Time-series feature engineering
- Regular time-index validation
- Autocorrelation analysis
- Lag feature screening
- Rolling-window smoothing
- Calendar and holiday feature creation
- Weather enrichment from a public API
- Baseline forecasting and holdout scoring
- Rolling-origin backtesting
- Regularized lag-regression benchmark
- Multi-month archive streaming and aggregation
- Station ID normalization and metadata-derived clustering
- Grouped time-series forecasting
- Weather, holiday, and event feature engineering
- Residual analysis and anomaly framing
- Anomaly scoring with seasonal expected values
- Seaborn/Matplotlib charting
- HTML report generation
- Documentation and reproducibility practices

## Interview Talking Points

1. I started with transparent baselines because a strong time-series project
   needs a benchmark before model complexity.
2. I used hourly trip starts as the core grain because that grain supports
   commuter seasonality, weather joins, and operational decisions.
3. I separated valid raw rows from fixed-window hourly rides because a few
   valid starts can fall outside the fixed January panel.
4. I added rolling-origin backtests because repeated forecast starts are more
   convincing than one lucky or unlucky holdout split.
5. I treated anomalies as candidates, not causes, because root-cause claims
   need external event or operations context.
6. I improved the project beyond the first month by adding a full-2024 proof
   layer, then pushed it into station-cluster forecasting tied to
   rebalancing/capacity planning.

## Resume Bullets

- Built a reproducible Citi Bike time-series pipeline over 44.25M valid public
  trip records, producing hourly demand features, quality metrics, charts, and
  HTML reports.
- Evaluated previous-day, previous-week, and weekday/hour calendar baselines on
  a 168-hour holdout; the calendar profile achieved the best MAE at 796 rides
  per hour.
- Extended the project to a full-2024 rolling validation proof with 44 forecast
  origins; a calendar-lag ridge benchmark achieved 750 MAE versus 918 for the
  previous-week baseline.
- Built station-cluster forecasts from the top 120 station IDs and full-year
  weather/event features; the richer model improved system MAE to 711 and beat
  both baselines across all 6 clusters.
- Added autocorrelation, lag-feature, decomposition-style residual, and
  rolling-origin diagnostics to demonstrate end-to-end time-series workflow
  design.
- Documented data quality rules, metric definitions, model caveats, and a
  roadmap for extending the project toward capacity and availability outcomes.

## Recommended Portfolio Card

**Citi Bike Demand Forecasting**

Analyzed 44.25M valid public Citi Bike trips to build January, full-year, and
station-cluster hourly demand profiles; evaluate transparent baselines; compare
calendar-lag and weather/event ridge models across rolling origins; inspect
autocorrelation and lag structure; detect anomaly candidates; and frame the
forecast as a rebalancing/capacity-planning watchlist.

**Tools:** Python, pandas, NumPy, Seaborn, Matplotlib, HTML reporting

**Methods:** Time-series profiling, calendar features, autocorrelation, lag
features, grouped time series, rolling-origin backtesting, baseline forecasting,
regularized lag-regression, weather/event regressors, residual analysis,
anomaly detection, data documentation
