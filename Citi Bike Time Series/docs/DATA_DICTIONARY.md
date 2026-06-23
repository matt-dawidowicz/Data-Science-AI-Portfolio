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
