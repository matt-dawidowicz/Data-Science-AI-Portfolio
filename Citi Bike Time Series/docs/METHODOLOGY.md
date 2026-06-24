# Methodology

This document explains how the Citi Bike time-series project turns raw public
trip data into a portfolio-ready demand profile and baseline forecast.

## Analytical Question

The project asks:

> Does Citi Bike January 2024 trip history contain enough temporal structure to
> make a strong time-series forecasting showcase?

The answer is yes for a portfolio profile. The data has enough volume and a
visible weekday/hour pattern to support demand profiling, simple baseline
forecasting, anomaly candidates, and a clear next-step roadmap.

The project now also asks:

> Does the approach still hold when extended to a full year of public data and
> repeated forecast origins?

The answer is also yes for a stronger portfolio proof. The full-2024 layer
profiles 44.25M valid rows, builds a complete 8,784-hour panel, and evaluates
44 weekly 24-hour forecast origins.

The project now asks a third, more operational question:

> Can the full-year forecast be pushed from aggregate demand into station
> clusters with weather, holiday, and event features?

The answer is yes for a portfolio-grade rebalancing and capacity-planning
watchlist. The station-cluster layer models the system total plus 6 station
clusters built from the top 120 station IDs, then validates previous-week,
calendar-lag ridge, and weather/event ridge models across the same 44 weekly
24-hour origins.

## Data Acquisition

The profile script downloads the public January 2024 Citi Bike trip-history
archive:

```text
https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip
```

It also optionally pulls hourly New York City weather from Open-Meteo for the
same month. Downloaded raw files are cached under `work/data/`, which is
excluded from Git.

The multi-month proof script downloads public monthly archives for an inclusive
month range:

```text
https://s3.amazonaws.com/tripdata/YYYYMM-citibike-tripdata.zip
```

The full-2024 run uses Jan.-Dec. 2024. Raw multi-month archives are cached under
`work/data/multi_month/`, which is also excluded from Git.

The station-cluster script reuses those monthly archives and adds full-year
Open-Meteo historical weather for New York City:

```text
https://archive-api.open-meteo.com/v1/archive
```

Weather JSON is cached under `work/data/weather/`, which is excluded from Git.

## Required Raw Columns

The script expects these Citi Bike columns:

- `ride_id`
- `rideable_type`
- `started_at`
- `ended_at`
- `start_station_name`
- `member_casual`

If one of those columns is missing, the script raises an error instead of
silently producing a partial profile.

The station-cluster script additionally uses these optional raw columns when
they are present:

- `start_station_id`
- `start_station_name`
- `start_lat`
- `start_lng`

Station IDs anchor the longitudinal grouping. Station names are used only for
readable labels, because names can change.

## Quality Filter

A raw row is counted as valid only when:

1. `started_at` parses as a timestamp.
2. `ended_at` parses as a timestamp.
3. Trip duration is from 1 to 240 minutes.

This filter removes broken timestamps and implausible durations while retaining
99.90% of the raw rows in the current run.

## Time Grain

The main unit of analysis is an hourly trip-start count:

```text
hour = floor(started_at to the hour)
rides = count(valid trip starts in that hour)
```

The fixed panel covers Jan. 1, 2024 00:00 through Jan. 31, 2024 23:00, which
creates 744 hourly observations.

## Feature Engineering

The hourly table adds:

- Date
- Day name
- Day of week
- Hour of day
- Weekend flag
- Federal holiday flag for Jan. 1 and Jan. 15
- Temperature C
- Precipitation mm
- Snowfall cm
- Wind speed km/h

These features are intentionally transparent. The goal of this version is to
prove the time-series structure before introducing heavier models.

## Seasonality Profile

The seasonality profile groups the hourly data by day of week and hour of day.
It supports:

- The heatmap in the report
- The calendar-profile forecast baseline
- The expected value used for anomaly detection

This is a one-month descriptive profile. It should not be treated as a stable
annual seasonal model until more months are added.

## Expanded Time-Series Diagnostics

The showcase script adds diagnostics that make the project read as a broader
time-series case study.

Run:

```text
python src/citibike_time_series_showcase.py
```

The script reads `outputs/hourly_profile.csv` and creates additional outputs.
It does not redownload the raw trip archive.

### Regular Index Checks

The showcase validates the generated hourly panel by checking:

- first hour
- last hour
- observed hourly rows
- expected hourly rows
- missing hours
- duplicate hours

This is the first time-series quality gate. Forecasting logic assumes a regular
time index with one value per hour.

### Autocorrelation

`outputs/autocorrelation_profile.csv` reports correlations between hourly rides
and lagged hourly rides from lag 1 through lag 168. It is used to inspect:

- short-memory lags
- daily repetition
- weekly repetition

Autocorrelation is descriptive. It identifies candidate signal but does not
prove forecast lift by itself.

### Lag Feature Screening

`outputs/lag_feature_correlations.csv` ranks candidate lag, rolling, and weather
features by correlation with hourly rides.

Included candidates:

- 1, 2, 3, 6, 12, 24, 48, 72, and 168 hour lags
- rolling 3, 6, 12, 24, and 168 hour means
- temperature, precipitation, snowfall, and wind speed

These correlations are feature-screening inputs, not final feature-selection
proof. A candidate should still be tested in rolling validation before being
presented as useful in a model.

### Decomposition Proxy

`outputs/decomposition_components.csv` creates a descriptive decomposition-style
table:

- actual hourly rides
- centered 24-hour rolling trend
- centered 168-hour rolling trend
- weekday/hour expected demand
- seasonal residual
- robust residual z-score

This is intentionally called a proxy because one month of data is too short for
a full annual decomposition. It is still useful because it demonstrates the
reasoning pattern behind trend, seasonality, and anomaly analysis.

## Forecast Backtest

The holdout starts at:

```text
2024-01-25 00:00:00
```

The training period is everything before that timestamp. The test period covers
168 holdout hours.

Three simple baselines are evaluated:

| Model | Definition |
| --- | --- |
| Previous day | Forecast equals the value from 24 hours earlier |
| Previous week | Forecast equals the value from 168 hours earlier |
| Calendar profile | Forecast equals the training-period average for the same weekday and hour |

The project reports MAE, RMSE, MAPE, and mean actual holdout volume. MAE is the
primary comparison because it is easy to explain as rides per hour and is less
distorted by low-volume overnight percentage errors than MAPE.

## Rolling-Origin Backtest

The expanded showcase adds daily rolling 24-hour forecast origins from the
second half of the month. For each origin:

1. Train only on history before the origin.
2. Forecast the next 24 hours.
3. Score MAE, RMSE, and MAPE.
4. Aggregate performance across origins.

Models included:

| Model | Definition |
| --- | --- |
| Previous day | Forecast equals the value from 24 hours earlier |
| Previous week | Forecast equals the value from 168 hours earlier |
| Hour-of-day profile | Forecast equals the expanding training average for the same hour of day |
| Weekday/hour profile | Forecast equals the expanding training average for the same weekday and hour |

Rolling-origin validation is more robust than a single split because it asks
whether a baseline works across repeated forecast starts. The current version is
still limited by one month of data, so it should be presented as validation
practice rather than production evidence.

## Full-Year Rolling Proof

Run:

```text
python src/citibike_multi_month_proof.py --start-month 2024-01 --end-month 2024-12
```

This script streams the monthly archives, applies the same timestamp and
duration validity rules, aggregates trip starts to an hourly panel, and scores
weekly 24-hour forecast origins.

Current full-year validation settings:

| Setting | Value |
| --- | ---: |
| Training warmup | 60 days |
| Origin cadence | 7 days |
| First origin | 2024-03-01 |
| Last origin | 2024-12-27 |
| Origins scored | 44 |
| Forecast horizon | 24 hours |

The leakage boundary is:

```text
train = rows where hour < origin
test = rows where origin <= hour < origin + 24 hours
```

Models compared:

| Model | Definition |
| --- | --- |
| Previous day | Forecast equals the value from 24 hours earlier |
| Previous week | Forecast equals the value from 168 hours earlier |
| Hour-of-day profile | Expanding training average for the same hour of day |
| Weekday/hour profile | Expanding training average for the same weekday and hour |
| Seasonal lag blend | 65% weekday/hour profile plus 35% previous-week forecast |
| Calendar + lag ridge | Regularized linear model using calendar and prior-demand features |

The ridge features are deliberately restricted to values known before the
24-hour horizon: calendar cycles, weekend and holiday flags, elapsed time, lag
24h, lag 168h, and rolling means anchored one day back.

The current full-year run makes the project materially stronger: the calendar +
lag ridge model scores 750 MAE across 44 origins, versus 918 MAE for previous
week and 1,034 MAE for previous day.

## Station-Cluster Forecasting

Run:

```text
python src/citibike_station_cluster_forecast.py --start-month 2024-01 --end-month 2024-12 --skip-download
```

This script adds the station-aware operating layer:

1. Stream valid trip rows from the 2024 monthly archives.
2. Build station metadata from observed station IDs, names, and coordinates.
3. Select the top 120 station IDs by annual starts.
4. Build 6 deterministic geographic station clusters using weighted k-means.
5. Create a long hourly panel for the system total plus each station cluster.
6. Join hourly weather, holiday windows, and selected public event windows.
7. Score previous-week, calendar-lag ridge, and weather/event ridge models
   across weekly 24-hour rolling origins.
8. Produce a rebalancing/capacity-planning priority table.

The weather/event ridge uses the calendar-lag ridge feature set plus:

- temperature
- precipitation
- snowfall
- wind speed
- weather code
- precipitation and snow flags
- temperature comfort transforms
- federal holiday windows
- holiday eve and holiday window flags
- selected major event windows
- event peak-hour flags

Observed historical weather is used as a stand-in for weather forecasts. A
production version should replace it with forecast weather available before the
origin.

Current station-cluster validation result:

| Segment | Previous Week MAE | Calendar-Lag MAE | Weather/Event MAE |
| --- | ---: | ---: | ---: |
| System total | 918.9 | 749.7 | 710.7 |
| Cluster 01 - W 21 St & 6 Ave area | 90.8 | 74.7 | 71.6 |
| Cluster 02 - 11 Ave & W 41 St area | 55.6 | 47.4 | 45.6 |
| Cluster 03 - West St & Chambers St area | 61.0 | 48.7 | 45.7 |
| Cluster 04 - Ave A & E 14 St area | 28.0 | 23.5 | 22.4 |
| Cluster 05 - E 72 St & York Ave area | 18.2 | 15.2 | 14.6 |
| Cluster 06 - Hanson Pl & Ashland Pl area | 4.3 | 3.4 | 3.4 |

The richer model beats both baselines for every modeled segment in this run.
The decision implication is to use the station-cluster output as a planning
watchlist, not as direct proof of station inventory risk.

## Forecast Reference Band

The forecast chart uses a simple residual reference band built from previous
week residual quantiles. It is useful for a visual reference, but it is not a
calibrated prediction interval.

## Anomaly Detection

The anomaly table compares each actual hourly value with its weekday/hour
expected value. It ranks hours by absolute robust z-score.

This creates anomaly candidates, not root-cause explanations. External context
is needed before interpreting an anomaly:

- Severe weather
- Station status
- Local events
- System outages
- Operations notes

## Visualization Choices

| Chart | Why This Form |
| --- | --- |
| Daily demand line | Shows month-level movement and smoothed direction |
| Weekday/hour heatmap | Shows dense seasonality in one view |
| Forecast backtest line | Compares actuals with the best baseline over the holdout |
| Ranked station bars | Makes station concentration easy to scan |
| Station cluster map | Shows how top station IDs were grouped from observed coordinates |
| Station cluster lift bars | Shows whether weather/event ridge beat previous-week baseline by segment |
| Station-cluster MAE bars | Compares previous-week, calendar-lag ridge, and weather/event ridge by target |

## Validation

Current validation checks include:

- Required raw columns are present.
- No output is produced if no valid trips remain after filtering.
- Fixed hourly panel has 744 rows.
- Forecast backtest produces metrics for all three baselines.
- Generated report references chart files that exist.
- Showcase diagnostics check for missing and duplicate hourly periods.
- Rolling-origin outputs are regenerated from the existing hourly profile.
- Static showcase charts are exported as PNG files for portable HTML review.
- The full-year proof verifies a complete 8,784-hour 2024 panel with zero
  missing hours.
- The full-year proof compares six models across 44 weekly rolling origins.
- Full-year raw archives remain ignored under `work/data/multi_month/`.
- The station-cluster layer verifies 99.93% station ID coverage across
  fixed-window modeled starts.
- The station-cluster layer joins 8,784 weather hours with 0 missing hours.
- The station-cluster layer compares weather/event ridge against previous-week
  and calendar-lag ridge baselines for every modeled segment.
- The station-cluster charts and HTML report are exported as portable PNG/HTML
  artifacts.

## Limitations

- The January report is one winter month; the full-year proof is stronger but
  still not a production operations model.
- Station names are not stable identifiers; the station-cluster layer uses
  station IDs for grouping and names only for readable labels.
- Weather is joined from a single city coordinate.
- Forecast intervals are simple residual bands.
- Anomaly rows are descriptive until external context is joined.
- The station-cluster layer includes selected weather and event features, but
  it does not include station capacity, live availability, or rebalancing logs.
- The weather/event ridge uses observed historical weather as a stand-in for
  weather forecasts that would be available before an operating day.

## Next Methodological Upgrade

The strongest next upgrade is now operational validation tied to inventory and
capacity outcomes:

1. Join station capacity, live availability, and station-status snapshots.
2. Measure stockout or full-dock risk after high-demand forecast windows.
3. Add calibrated alert thresholds for a rebalancing watchlist.
4. Compare error and alert quality by commute peak, event window, and weather
   pressure.
5. Convert the report into a lightweight dashboard or notebook walkthrough.
