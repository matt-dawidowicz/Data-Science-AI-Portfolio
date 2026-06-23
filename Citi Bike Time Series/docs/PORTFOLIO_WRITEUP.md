# Portfolio Writeup

This document gives a polished project narrative for a portfolio page,
interview discussion, or README summary.

## Project Title

Citi Bike Demand Forecasting: Time-Series Profile and Baseline Forecasts

## One-Line Summary

Built a reproducible time-series analysis of 1.89M public Citi Bike trips,
showing commute-driven demand seasonality, autocorrelation and lag diagnostics,
rolling-origin baseline validation, residual analysis, and the roadmap for
station-aware forecasting.

## Portfolio Category

Time Series Forecasting / Urban Mobility Analytics

## Problem Framing

Citi Bike trip activity has strong temporal patterns, but a useful forecasting
showcase needs to prove those patterns before introducing complex models. This
project starts with a clean January 2024 hourly panel, defines valid trip-start
metrics, builds calendar and weather features, evaluates simple baselines, and
turns the results into a decision-ready report.

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
- A decomposition-style output that separates rolling trend, seasonal expected
  demand, and residual movement.
- Anomaly candidates based on deviations from the weekday/hour profile.
- Static report visuals and three HTML reports: profile, recommendation, and
  time-series showcase reports.
- An expanded time-series showcase report that maps each time-series concept to
  a concrete artifact.
- Documentation for measures, methodology, outputs, model behavior, caveats,
  and publishing readiness.

## Business Interpretation

The project shows that the first useful signal is not a black-box model. It is
the calendar structure of demand. Rush-hour volume averaged 2.23x off-hour
volume, weekends averaged 0.71x weekday hourly volume, and the calendar-profile
baseline beat weaker baselines on MAE over the Jan. 25-31 holdout.

That suggests the next version should focus on more history and station-aware
operations rather than immediately jumping to a heavier model.

## Key Results

- 1,886,109 valid trips after timestamp and duration filtering.
- 744 hourly observations in the fixed January panel.
- 1,885,763 fixed-window trip starts.
- 60,831 average daily rides.
- 8,635 rides in the peak hour.
- 2.23x rush/off-hour ratio.
- Calendar-profile baseline MAE: 796 rides per hour.
- Top 10 stations represented 3.25% of valid trip starts.

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
6. I would improve this project next by adding 12-24 months, yearly seasonality,
   station metadata, and station-cluster forecasts.

## Resume Bullets

- Built a reproducible Citi Bike time-series pipeline over 1.89M public trip
  records, producing hourly demand features, quality metrics, charts, and HTML
  reports.
- Evaluated previous-day, previous-week, and weekday/hour calendar baselines on
  a 168-hour holdout; the calendar profile achieved the best MAE at 796 rides
  per hour.
- Added autocorrelation, lag-feature, decomposition-style residual, and
  rolling-origin diagnostics to demonstrate end-to-end time-series workflow
  design.
- Documented data quality rules, metric definitions, model caveats, and a
  roadmap for extending the project to multi-month station-aware forecasting.

## Recommended Portfolio Card

**Citi Bike Demand Forecasting**

Analyzed 1.89M public Citi Bike trips to build an hourly demand profile,
evaluate baseline forecasts, inspect autocorrelation and lag structure, run
rolling-origin validation, detect anomaly candidates, and identify the next
modeling path for station-aware urban mobility forecasting.

**Tools:** Python, pandas, NumPy, Seaborn, Matplotlib, HTML reporting

**Methods:** Time-series profiling, calendar features, autocorrelation, lag
features, rolling-origin backtesting, baseline forecasting, residual analysis,
anomaly detection, data documentation
