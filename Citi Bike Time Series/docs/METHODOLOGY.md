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

## Data Acquisition

The profile script downloads the public January 2024 Citi Bike trip-history
archive:

```text
https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip
```

It also optionally pulls hourly New York City weather from Open-Meteo for the
same month. Downloaded raw files are cached under `work/data/`, which is
excluded from Git.

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

## Validation

Current validation checks include:

- Required raw columns are present.
- No output is produced if no valid trips remain after filtering.
- Fixed hourly panel has 744 rows.
- Forecast backtest produces metrics for all three baselines.
- Generated report references chart files that exist.

## Limitations

- One winter month is too narrow for production forecasting.
- Station names are not stable identifiers.
- Weather is joined from a single city coordinate.
- Forecast intervals are simple residual bands.
- Anomaly rows are descriptive until external context is joined.

## Next Methodological Upgrade

The strongest next upgrade is not a more complex model first. It is a stronger
evaluation design:

1. Extend to 12-24 months.
2. Add rolling holdout windows.
3. Add station IDs and station metadata.
4. Compare the calendar baseline with one stronger model.
5. Evaluate aggregate and station-cluster accuracy separately.
