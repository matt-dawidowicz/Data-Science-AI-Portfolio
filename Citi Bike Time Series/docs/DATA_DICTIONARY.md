# Data Dictionary

This dictionary describes the generated outputs in `outputs/`.

## `hourly_profile.csv`

One row per hour in the fixed January 2024 panel.

| Column | Type | Definition |
| --- | --- | --- |
| `hour` | datetime | Hour timestamp in the fixed Jan. 1-31 panel |
| `rides` | integer | Count of valid trip starts in the hour |
| `date` | string | Calendar date for the hour |
| `day_name` | string | Day name such as Monday or Tuesday |
| `day_of_week` | integer | Monday = 0, Sunday = 6 |
| `hour_of_day` | integer | Hour from 0 to 23 |
| `is_weekend` | boolean | True for Saturday or Sunday |
| `is_federal_holiday` | boolean | True for Jan. 1 or Jan. 15, 2024 |
| `temperature_c` | float | Open-Meteo hourly temperature in Celsius |
| `precipitation_mm` | float | Open-Meteo hourly precipitation in millimeters |
| `snowfall_cm` | float | Open-Meteo hourly snowfall in centimeters |
| `wind_speed_kmh` | float | Open-Meteo hourly wind speed in kilometers per hour |

## `seasonality_profile.csv`

Average hourly rides by weekday and hour of day.

| Column | Type | Definition |
| --- | --- | --- |
| `day_of_week` | integer | Monday = 0, Sunday = 6 |
| `day_name` | string | Day name |
| `hour_of_day` | integer | Hour from 0 to 23 |
| `rides` | float | Average rides for the weekday/hour bucket |

## `forecast_backtest_metrics.csv`

Model-level backtest metrics for the Jan. 25-31 holdout.

| Column | Type | Definition |
| --- | --- | --- |
| `model` | string | Baseline model name |
| `n` | integer | Number of holdout hours used in scoring |
| `mae` | float | Mean absolute error in rides per hour |
| `rmse` | float | Root mean squared error in rides per hour |
| `mape` | float | Mean absolute percentage error |
| `mean_actual` | float | Average actual rides per holdout hour |

## `forecast_backtest_scored.csv`

Hour-level actuals, baseline forecasts, and reference bands for the holdout.

| Column | Type | Definition |
| --- | --- | --- |
| `hour` | datetime | Holdout hour |
| `rides` | integer | Actual rides in the holdout hour |
| `day_of_week` | integer | Monday = 0, Sunday = 6 |
| `hour_of_day` | integer | Hour from 0 to 23 |
| `previous_day` | float | Previous-day baseline forecast |
| `previous_week` | float | Previous-week baseline forecast |
| `calendar_profile` | float | Weekday/hour profile baseline forecast |
| `forecast` | float | Forecast from the best model by MAE |
| `forecast_lower` | float | Lower residual reference band |
| `forecast_upper` | float | Upper residual reference band |

## `anomaly_hours.csv`

Largest deviations from the weekday/hour seasonal profile.

| Column | Type | Definition |
| --- | --- | --- |
| `hour` | datetime | Hour being scored |
| `rides` | integer | Actual hourly rides |
| `expected_profile_rides` | float | Expected rides from weekday/hour profile |
| `absolute_gap` | float | Actual minus expected rides |
| `robust_z` | float | Robust z-score for the gap |
| `day_name` | string | Day name |
| `hour_of_day` | integer | Hour from 0 to 23 |

## `top_stations.csv`

Top start stations by valid trip starts.

| Column | Type | Definition |
| --- | --- | --- |
| `station` | string | Start station name |
| `rides` | integer | Valid trip starts from that station |
| `share_of_valid_trips` | float | Station starts divided by valid rows |

## `member_mix.csv`

Trip mix by rider type.

| Column | Type | Definition |
| --- | --- | --- |
| `rider_type` | string | Citi Bike rider type |
| `rides` | integer | Valid trips for that type |
| `share` | float | Share of valid trips |

## `bike_mix.csv`

Trip mix by bike type.

| Column | Type | Definition |
| --- | --- | --- |
| `bike_type` | string | Citi Bike rideable type |
| `rides` | integer | Valid trips for that type |
| `share` | float | Share of valid trips |

## `profile_summary.json`

Compact summary used by the reports. It includes headline measures, top days,
forecast metrics, top stations, mix measures, anomaly rows, and weather
correlations.

## `autocorrelation_profile.csv`

Autocorrelation values for lagged hourly rides from 1 through 168 hours.

| Column | Type | Definition |
| --- | --- | --- |
| `lag_hours` | integer | Number of hours between current rides and lagged rides |
| `autocorrelation` | float | Pearson autocorrelation between rides and rides at the lag |
| `lag_family` | string | Descriptive label such as short lag, daily seasonal lag, weekly seasonal lag, or other lag |

## `lag_feature_correlations.csv`

Simple correlation screen for lag, rolling, and weather feature candidates.

| Column | Type | Definition |
| --- | --- | --- |
| `feature` | string | Candidate feature name |
| `concept` | string | Feature family such as lag, rolling feature, or exogenous weather |
| `correlation_with_rides` | float | Pearson correlation between the feature and hourly rides |
| `abs_correlation` | float | Absolute value of the correlation, used for ranking |

## `rolling_backtest_metrics.csv`

Aggregate rolling-origin forecast metrics. Each origin forecasts the next 24
hours using only prior history.

| Column | Type | Definition |
| --- | --- | --- |
| `model` | string | Baseline model name |
| `origins` | integer | Number of daily rolling forecast origins |
| `holdout_hours` | integer | Total scored forecast hours |
| `mean_actual` | float | Average actual hourly rides across scored windows |
| `n` | integer | Number of non-null forecast rows used in scoring |
| `mae` | float | Mean absolute error in rides per hour |
| `rmse` | float | Root mean squared error in rides per hour |
| `mape` | float | Mean absolute percentage error |

## `rolling_backtest_origin_metrics.csv`

Per-origin rolling forecast metrics.

| Column | Type | Definition |
| --- | --- | --- |
| `origin` | datetime | Forecast origin timestamp |
| `model` | string | Baseline model name |
| `n` | integer | Number of scored hours for that origin and model |
| `mae` | float | Mean absolute error in rides per hour |
| `rmse` | float | Root mean squared error in rides per hour |
| `mape` | float | Mean absolute percentage error |

## `rolling_backtest_scored.csv`

Hour-level rolling-origin forecast rows.

| Column | Type | Definition |
| --- | --- | --- |
| `origin` | datetime | Forecast origin timestamp |
| `hour` | datetime | Forecasted hour |
| `model` | string | Baseline model name |
| `actual` | float | Actual hourly rides |
| `forecast` | float | Forecasted hourly rides |
| `error` | float | Actual minus forecast |
| `abs_error` | float | Absolute forecast error |

## `decomposition_components.csv`

Descriptive decomposition-style output for trend, seasonality, and residual
analysis.

| Column | Type | Definition |
| --- | --- | --- |
| `hour` | datetime | Hour in the fixed January panel |
| `rides` | float | Actual hourly ride starts |
| `day_of_week` | integer | Monday = 0, Sunday = 6 |
| `hour_of_day` | integer | Hour from 0 to 23 |
| `day_name` | string | Day name |
| `is_weekend` | boolean | True for Saturday or Sunday |
| `trend_24h` | float | Centered 24-hour rolling average of rides |
| `trend_168h` | float | Centered 168-hour rolling average of rides |
| `seasonal_expected` | float | Average rides for the same weekday and hour |
| `seasonal_component` | float | Seasonal expected rides minus overall mean rides |
| `seasonal_residual` | float | Actual rides minus seasonal expected rides |
| `residual_robust_z` | float | Robust z-score of the seasonal residual |

This is a descriptive proxy, not formal STL decomposition.

## `time_series_showcase_metrics.csv`

Compact headline metrics for `time_series_showcase.html`.

| Column | Type | Definition |
| --- | --- | --- |
| `category` | string | Metric family |
| `measure` | string | Metric name |
| `value` | string or numeric | Current metric value |
| `interpretation` | string | Reader-facing explanation |

## `time_series_showcase_coverage.csv`

Coverage map connecting time-series concepts to portfolio artifacts.

| Column | Type | Definition |
| --- | --- | --- |
| `time_series_area` | string | Time-series concept or practice |
| `artifact` | string | Project file that demonstrates the concept |
| `status` | string | Implemented or documented extension |
| `reviewer_value` | string | Why the artifact matters for a reviewer |
| `caveat` | string | Limitation or responsible interpretation note |

## `multi_month_hourly_profile.csv`

One row per hour in the full-2024 panel.

| Column | Type | Definition |
| --- | --- | --- |
| `hour` | datetime | Hour timestamp in the fixed full-year panel |
| `rides` | integer | Count of valid trip starts in the hour |
| `date` | string | Calendar date for the hour |
| `month` | string | Calendar month in YYYY-MM form |
| `day_name` | string | Day name |
| `day_of_week` | integer | Monday = 0, Sunday = 6 |
| `hour_of_day` | integer | Hour from 0 to 23 |
| `day_of_year` | integer | Calendar day number within the year |
| `is_weekend` | boolean | True for Saturday or Sunday |
| `is_federal_holiday` | boolean | True for simple U.S. federal holiday dates |
| `hour_sin`, `hour_cos` | float | Cyclical hour-of-day encodings |
| `dow_sin`, `dow_cos` | float | Cyclical day-of-week encodings |
| `month_sin`, `month_cos` | float | Cyclical month encodings |
| `is_weekend_int` | integer | Weekend flag converted to 0/1 for modeling |
| `is_federal_holiday_int` | integer | Holiday flag converted to 0/1 for modeling |
| `days_since_start` | float | Days elapsed from the first panel hour |
| `lag_24h` | float | Rides 24 hours earlier |
| `lag_168h` | float | Rides 168 hours earlier |
| `rolling_24h_prior_day` | float | 24-hour rolling mean anchored one day back |
| `rolling_168h_prior_day` | float | 168-hour rolling mean anchored one day back |

The prior-day rolling features are designed for a 24-hour forecast horizon and
avoid using values from inside the future forecast window.

## `multi_month_source_inventory.csv`

Monthly source and quality inventory for the full-year proof.

| Column | Type | Definition |
| --- | --- | --- |
| `month` | string | Archive month |
| `source_url` | string | Public Citi Bike archive URL |
| `archive_file` | string | Cached archive filename |
| `archive_size_mb` | float | Downloaded archive size in megabytes |
| `rows_total` | integer | Raw rows read for the month |
| `rows_valid` | integer | Rows passing timestamp and duration filters |
| `valid_rate` | float | Valid rows divided by total rows |
| `first_started_at` | datetime | Earliest valid start timestamp in the archive |
| `last_started_at` | datetime | Latest valid start timestamp in the archive |
| `valid_rides_in_fixed_window` | integer | Valid starts inside the calendar month panel |

## `multi_month_model_metrics.csv`

Aggregate full-year rolling-origin model metrics.

| Column | Type | Definition |
| --- | --- | --- |
| `model` | string | Internal model name |
| `model_label` | string | Reader-friendly model name |
| `origins` | integer | Number of rolling forecast origins |
| `holdout_hours` | integer | Scored forecast hours for the model |
| `mean_actual` | float | Average actual hourly rides across scored windows |
| `median_origin_mae` | float | Median MAE across forecast origins |
| `origin_wins` | integer | Number of origins where the model had the lowest MAE |
| `n` | integer | Number of non-null forecast rows used in scoring |
| `mae` | float | Mean absolute error in rides per hour |
| `rmse` | float | Root mean squared error in rides per hour |
| `mape` | float | Mean absolute percentage error |
| `origin_win_rate` | float | Origin wins divided by total origins |

## `multi_month_origin_metrics.csv`

Per-origin full-year model metrics.

| Column | Type | Definition |
| --- | --- | --- |
| `origin` | datetime | Forecast origin timestamp |
| `model` | string | Internal model name |
| `n` | integer | Number of scored forecast hours for the origin |
| `mae` | float | Mean absolute error in rides per hour |
| `rmse` | float | Root mean squared error in rides per hour |
| `mape` | float | Mean absolute percentage error |

## `multi_month_backtest_scored.csv`

Hour-level full-year rolling forecast rows.

| Column | Type | Definition |
| --- | --- | --- |
| `origin` | datetime | Forecast origin timestamp |
| `hour` | datetime | Forecasted hour |
| `model` | string | Internal model name |
| `actual` | float | Actual hourly rides |
| `forecast` | float | Forecasted hourly rides |
| `error` | float | Actual minus forecast |
| `abs_error` | float | Absolute forecast error |

## `multi_month_top_stations.csv`

Top start station IDs/names across the full-year valid trip rows.

| Column | Type | Definition |
| --- | --- | --- |
| `station_id_name` | string | Combined start station ID and start station name |
| `rides` | integer | Valid starts from that station key |

## `multi_month_proof_summary.json`

Compact metadata and headline measures for `multi_month_proof.html`, including
the date range, row counts, fixed-window totals, rolling-origin settings, and
best full-year model.
