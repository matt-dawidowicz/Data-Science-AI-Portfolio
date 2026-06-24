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

## `station_cluster_source_inventory.csv`

Monthly source and quality inventory for the station-cluster layer.

| Column | Type | Definition |
| --- | --- | --- |
| `month` | string | Archive month |
| `source_url` | string | Public Citi Bike archive URL |
| `archive_file` | string | Cached archive filename |
| `archive_size_mb` | float | Downloaded archive size in megabytes |
| `rows_total` | integer | Raw rows read for the month |
| `rows_valid` | integer | Rows passing timestamp and duration filters |
| `rows_valid_fixed_window` | integer | Valid rows inside the fixed calendar-month modeling window |
| `rows_with_station_id` | integer | Fixed-window valid rows with usable start station ID |
| `valid_rate` | float | Valid rows divided by total rows |
| `station_id_coverage` | float | Fixed-window valid rows with station ID divided by fixed-window valid rows |
| `first_started_at` | datetime | Earliest valid start timestamp in the archive |
| `last_started_at` | datetime | Latest valid start timestamp in the archive |
| `valid_rides_in_fixed_window` | integer | Valid starts inside the calendar month panel |

## `station_cluster_station_metadata.csv`

Observed station metadata derived from valid trip rows.

| Column | Type | Definition |
| --- | --- | --- |
| `station_id` | string | Stable start station ID from the Citi Bike trip archive |
| `station_name` | string | Most common observed station name for the station ID |
| `annual_starts` | integer | Fixed-window valid 2024 starts from the station ID |
| `months_active` | integer | Count of archive months where the station ID appeared |
| `first_started_at` | datetime | Earliest valid trip start for the station ID |
| `last_started_at` | datetime | Latest valid trip start for the station ID |
| `latitude` | float | Average observed start latitude after coordinate filtering |
| `longitude` | float | Average observed start longitude after coordinate filtering |
| `coordinate_rows` | integer | Valid coordinate observations used for the averages |
| `share_of_system_starts` | float | Station starts divided by fixed-window system starts |

## `station_cluster_assignments.csv`

Top station IDs assigned to deterministic geographic clusters.

| Column | Type | Definition |
| --- | --- | --- |
| `station_id` | string | Stable station ID |
| `station_name` | string | Most common observed station name |
| `annual_starts` | integer | Fixed-window valid 2024 starts |
| `months_active` | integer | Active archive months observed |
| `latitude` | float | Observed station latitude |
| `longitude` | float | Observed station longitude |
| `cluster_id` | string | Deterministic cluster ID |
| `cluster_label` | string | Reader-friendly cluster label anchored on the top station |

## `station_cluster_summary.csv`

Cluster-level station count, volume, and geography.

| Column | Type | Definition |
| --- | --- | --- |
| `cluster_id` | string | Deterministic cluster ID |
| `cluster_label` | string | Reader-friendly cluster label |
| `annual_starts` | integer | Fixed-window valid 2024 starts from stations in the cluster |
| `station_count` | integer | Count of station IDs in the cluster |
| `center_latitude` | float | Mean station latitude inside the cluster |
| `center_longitude` | float | Mean station longitude inside the cluster |
| `top_station` | string | Highest-volume station name inside the cluster |
| `share_of_system_starts` | float | Cluster starts divided by fixed-window system starts |
| `rank` | integer | Cluster rank by annual starts |
| `segment_id` | string | Segment key used in forecast outputs |
| `segment_label` | string | Segment label used in forecast outputs |
| `segment_type` | string | `station_cluster` |

## `station_cluster_hourly_profile.csv`

Long hourly model panel for the system total and station clusters.

| Column | Type | Definition |
| --- | --- | --- |
| `segment_id` | string | `system_total` or station cluster ID |
| `segment_label` | string | Reader-friendly segment label |
| `segment_type` | string | `system` or `station_cluster` |
| `hour` | datetime | Hour timestamp in the 2024 panel |
| `rides` | integer | Valid trip starts for the segment and hour |
| `date`, `month`, `day_name` | string | Calendar labels |
| `day_of_week`, `hour_of_day`, `day_of_year` | integer | Calendar fields used for features |
| `is_weekend`, `is_federal_holiday` | boolean | Calendar flags |
| `temperature_2m` | float | Open-Meteo temperature in Celsius |
| `precipitation` | float | Open-Meteo precipitation in millimeters |
| `snowfall` | float | Open-Meteo snowfall in centimeters |
| `wind_speed_10m` | float | Open-Meteo wind speed in km/h |
| `weather_code` | float | Open-Meteo weather code |
| `event_intensity` | float | Holiday/event feature weight after windowing |
| `event_names`, `event_types`, `event_windows` | string | Event labels joined to the hour |
| `lag_24h`, `lag_168h` | float | Segment rides 24 and 168 hours earlier |
| `rolling_24h_prior_day` | float | Segment 24-hour rolling mean anchored one day back |
| `rolling_168h_prior_day` | float | Segment 168-hour rolling mean anchored one day back |

## `station_cluster_model_metrics.csv`

Aggregate rolling-origin metrics by segment and model.

| Column | Type | Definition |
| --- | --- | --- |
| `segment_id`, `segment_label`, `segment_type` | string | Forecast target segment |
| `model`, `model_label` | string | Internal and reader-facing model name |
| `origins` | integer | Number of rolling origins scored |
| `holdout_hours` | integer | Segment/model forecast rows scored |
| `mean_actual` | float | Average actual rides in scored rows |
| `total_actual` | float | Total actual rides in scored rows |
| `median_origin_mae` | float | Median per-origin MAE |
| `origin_wins` | integer | Count of segment origins where this model had lowest MAE |
| `n` | integer | Non-null scored forecast rows |
| `mae`, `rmse`, `mape`, `wape` | float | Forecast error metrics |
| `origin_win_rate` | float | Origin wins divided by origins for the segment |

## `station_cluster_model_lift.csv`

Wide comparison of previous-week, calendar-lag ridge, and weather/event ridge.

| Column | Type | Definition |
| --- | --- | --- |
| `segment_id`, `segment_label`, `segment_type` | string | Forecast target segment |
| `mae_*`, `rmse_*`, `wape_*` | float | Error metrics by model |
| `mae_lift_vs_previous_week` | float | Previous-week MAE minus weather/event ridge MAE |
| `mae_lift_pct_vs_previous_week` | float | MAE lift divided by previous-week MAE |
| `mae_lift_vs_calendar_lag_ridge` | float | Calendar-lag ridge MAE minus weather/event ridge MAE |
| `mae_lift_pct_vs_calendar_lag_ridge` | float | MAE lift divided by calendar-lag ridge MAE |
| `best_model`, `best_model_label` | string | Lowest-MAE model for the segment |

## `station_cluster_capacity_priorities.csv`

Decision table for rebalancing and capacity-planning review.

| Column | Type | Definition |
| --- | --- | --- |
| `cluster_id`, `cluster_label` | string | Station-cluster identifiers |
| `annual_starts`, `station_count`, `share_of_system_starts` | numeric | Cluster scale measures |
| `mae`, `rmse`, `wape`, `mean_actual` | float | Weather/event ridge forecast metrics |
| `mae_lift_pct_vs_previous_week` | float | Weather/event ridge lift versus previous week |
| `mae_lift_pct_vs_calendar_lag_ridge` | float | Weather/event ridge lift versus calendar-lag ridge |
| `priority_score` | float | Heuristic rank combining scale and forecast-error context |
| `capacity_planning_use` | string | Reader-facing planning recommendation |

## `station_cluster_origin_metrics.csv`

Per-origin model metrics for every segment.

| Column | Type | Definition |
| --- | --- | --- |
| `segment_id`, `segment_label`, `segment_type` | string | Forecast target segment |
| `origin` | datetime | Forecast origin timestamp |
| `model`, `model_label` | string | Forecast model |
| `n` | integer | Scored hours for that segment/model/origin |
| `mae`, `rmse`, `mape`, `wape` | float | Forecast error metrics |

## `station_cluster_backtest_scored.csv`

Hour-level forecast rows for the station-cluster validation.

| Column | Type | Definition |
| --- | --- | --- |
| `segment_id`, `segment_label`, `segment_type` | string | Forecast target segment |
| `origin` | datetime | Forecast origin timestamp |
| `hour` | datetime | Forecasted hour |
| `model`, `model_label` | string | Forecast model |
| `actual` | float | Actual segment rides |
| `forecast` | float | Forecasted segment rides |
| `error` | float | Actual minus forecast |
| `abs_error` | float | Absolute error |

## `station_cluster_forecast_summary.json`

Compact metadata and headline measures for `station_cluster_forecast.html`,
including station-cluster coverage, weather coverage, rolling-origin settings,
model lift, and the rebalancing/capacity-planning recommendation.
