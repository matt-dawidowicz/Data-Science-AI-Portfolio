# Measures

This document defines the measures used in the Citi Bike time-series project.
It is written as the source a reviewer should use before reading the reports or
reusing the outputs.

## Measurement Scope

- Dataset month: January 2024
- Raw source: Citi Bike public trip-history archive
- Weather source: Open-Meteo historical archive for New York City
- Time grain: hour
- Main event: valid trip start
- Main fixed window: Jan. 1, 2024 00:00 through Jan. 31, 2024 23:00
- Holdout window: Jan. 25, 2024 00:00 through Jan. 31, 2024 23:00

## Quality Measures

| Measure | Definition | Current Value | Source |
| --- | --- | ---: | --- |
| Rows total | Raw rows read from the January archive | 1,888,085 | `profile_summary.json` |
| Valid rows | Rows with parseable `started_at`, parseable `ended_at`, and duration from 1 to 240 minutes | 1,886,109 | `profile_summary.json` |
| Valid rate | Valid rows divided by total rows | 99.90% | `profile_summary.json` |
| First parsed start | Earliest valid start timestamp observed in the archive | 2023-12-31 21:40:09.191000 | `profile_summary.json` |
| Last parsed start | Latest valid start timestamp observed in the archive | 2024-01-31 23:58:30.270000 | `profile_summary.json` |

The analysis keeps a fixed January hourly panel after filtering. A small number
of valid raw rows can fall outside the fixed Jan. 1-31 hourly panel, so the
valid-row count and fixed-window ride total are not expected to match exactly.

## Demand Measures

| Measure | Definition | Current Value | Source |
| --- | --- | ---: | --- |
| Hourly observations | Number of hourly rows in the fixed window | 744 | `hourly_profile.csv` |
| Total fixed-window rides | Sum of hourly valid trip starts in the fixed window | 1,885,763 | `profile_summary.json` |
| Average daily rides | Mean of daily summed hourly rides | 60,831 | `profile_summary.json` |
| Average hourly rides | Mean hourly ride starts across the fixed window | 2,535 | `profile_summary.json` |
| Median hourly rides | Median hourly ride starts across the fixed window | 2,175 | `profile_summary.json` |
| Peak hour | Hour with the highest ride count | 2024-01-11 17:00 | `profile_summary.json` |
| Peak hour rides | Ride starts in the peak hour | 8,635 | `profile_summary.json` |

## Duration Measures

| Measure | Definition | Current Value | Source |
| --- | --- | ---: | --- |
| Median duration | Median valid trip duration in minutes | 7.7 min | `profile_summary.json` |
| P90 duration | 90th percentile valid trip duration in minutes | 21.0 min | `profile_summary.json` |
| P99 duration | 99th percentile valid trip duration in minutes | 49.4 min | `profile_summary.json` |

Duration measures are calculated after the valid-trip filter, so trips under 1
minute and over 240 minutes are excluded.

## Seasonality Measures

| Measure | Definition | Current Value | Source |
| --- | --- | ---: | --- |
| Weekday average hourly rides | Average hourly rides where day is Monday-Friday | 2,737 | `profile_summary.json` |
| Weekend average hourly rides | Average hourly rides where day is Saturday or Sunday | 1,953 | `profile_summary.json` |
| Weekend/weekday ratio | Weekend hourly average divided by weekday hourly average | 0.71x | `profile_summary.json` |
| Rush-hour average | Average hourly rides during 7, 8, 9, 16, 17, and 18 | 4,328 | `profile_summary.json` |
| Off-hour average | Average hourly rides outside the rush-hour definition | 1,937 | `profile_summary.json` |
| Rush/off-hour ratio | Rush-hour average divided by off-hour average | 2.23x | `profile_summary.json` |

The current rush-hour definition is deliberately simple and commuter-oriented:
7-9 AM plus 4-6 PM. If the business decision changes, this definition should be
revisited.

## Forecasting Measures

| Model | Holdout Hours | MAE | RMSE | MAPE | Mean Actual |
| --- | ---: | ---: | ---: | ---: | ---: |
| Calendar profile | 168 | 796 | 1,075 | 36.2% | 2,908 |
| Previous week | 168 | 872 | 1,277 | 29.7% | 2,908 |
| Previous day | 168 | 1,001 | 1,581 | 56.3% | 2,908 |

Model definitions:

- Calendar profile: training-period average for the same weekday and hour.
- Previous week: the value from 168 hours earlier.
- Previous day: the value from 24 hours earlier.

Interpretation:

- Calendar profile is best on MAE and RMSE in this run.
- Previous week has lower MAPE, which is a caveat. MAPE can behave differently
  when low-volume overnight hours dominate percentage error.
- This is a single holdout window, not rolling validation.

## Operational Texture Measures

| Measure | Definition | Current Value | Source |
| --- | --- | ---: | --- |
| Top station | Start station with the most valid trip starts | W 21 St & 6 Ave | `top_stations.csv` |
| Top station rides | Starts at the top station | 8,325 | `top_stations.csv` |
| Top station share | Top station starts divided by valid rows | 0.44% | `top_stations.csv` |
| Top 10 station share | Top 10 station starts divided by valid rows | 3.25% | `top_stations.csv` |
| Member share | Member trips divided by valid rows | 88.99% | `member_mix.csv` |
| Casual share | Casual trips divided by valid rows | 11.01% | `member_mix.csv` |
| Electric-bike share | Electric-bike trips divided by valid rows | 64.37% | `bike_mix.csv` |
| Classic-bike share | Classic-bike trips divided by valid rows | 35.63% | `bike_mix.csv` |

Station measures currently use station names. A station-level production model
should add stable station IDs and station metadata.

## Anomaly Measures

The anomaly table compares actual hourly rides with the weekday/hour seasonal
profile. It reports:

- Hour
- Actual rides
- Expected profile rides
- Absolute gap
- Robust z-score
- Day name
- Hour of day

Largest current flagged gap:

| Hour | Actual Rides | Expected Rides | Absolute Gap | Robust Z |
| --- | ---: | ---: | ---: | ---: |
| 2024-01-18 12:00 | 2,248 | 3,678.5 | -1,430.5 | -42.88 |

These are anomaly candidates, not root causes. Before claiming why an anomaly
happened, join event, weather warning, station status, outage, or operations
context.

## Weather Measures

Weather was joined at hourly grain for:

- Temperature C
- Precipitation mm
- Snowfall cm
- Wind speed km/h

Current descriptive correlations with hourly rides:

| Weather Field | Correlation |
| --- | ---: |
| Temperature C | 0.351 |
| Precipitation mm | -0.196 |
| Snowfall cm | -0.113 |
| Wind speed km/h | -0.100 |

These are descriptive correlations only. They should be evaluated as model
features with rolling holdouts before being described as predictive lift.
