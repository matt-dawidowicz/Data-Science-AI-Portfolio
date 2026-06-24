# Citi Bike Demand Forecasting

Time-series profiling and forecasting project built from public Citi Bike
trip-history data. The project starts with a January 2024 methods showcase, then
adds a full-2024 proof layer with 12 public monthly archives, a complete hourly
panel, leakage-aware rolling validation, transparent baselines, and a simple
calendar-lag ridge model. The latest layer adds station-cluster forecasting:
stable station groups from station IDs and observed metadata, weather and event
features, rolling validation by segment, and a rebalancing/capacity-planning
decision frame.

## Portfolio Fit

This belongs in the portfolio as a standalone analytics case study:

```text
Time Series Forecasting / Urban Mobility Analytics
```

It complements a code-heavy portfolio project because it shows a different
skill set:

- Public data acquisition and reproducible processing
- Data quality filtering and metric definition
- Time-series feature engineering
- Autocorrelation, lag screening, and rolling-window diagnostics
- Baseline forecasting and holdout evaluation
- Rolling-origin forecast validation across one month and a full year
- A stronger lag-regression benchmark against transparent baselines
- Stable station ID grouping and station-cluster forecast evaluation
- Weather, holiday, and event features tested in rolling validation
- Anomaly detection against a seasonal profile
- Business-facing reporting and documentation

## Headline Result

The January 2024 profile shows the core methods: regular hourly indexing,
commute seasonality, weather context, anomalies, lag diagnostics, and simple
calendar baselines. Citi Bike demand has a visible commute pattern: rush-hour
volume averaged 2.23x off-hour volume, weekends averaged 0.71x weekday hourly
volume, and a weekday/hour calendar profile beat the previous-day and
previous-week baselines on MAE over the Jan. 25-31 holdout.

The full-2024 proof layer strengthens the claim. It profiles 44.25M valid trip
rows across 8,784 hourly observations with zero missing hours, then scores 44
weekly 24-hour rolling forecast origins from Mar. 1 through Dec. 27, 2024. The
best aggregate model is the calendar-lag ridge model with MAE of 750 rides per
hour, beating the previous-week baseline's 918 MAE and the previous-day
baseline's 1,034 MAE.

The station-cluster layer turns that aggregate proof into an operational case
study. It clusters the top 120 station IDs into 6 stable demand groups, models
the system total plus each cluster, joins 8,784 hourly weather observations and
holiday/event windows, and scores the richer model across the same 44 rolling
24-hour origins. The weather/event ridge model improves system MAE to 711 rides
per hour, beating previous week by 22.7% and the calendar-lag ridge by 5.2%.
It also beats both baselines for all 6 station clusters. The decision target is
rebalancing and station-capacity planning, with Cluster 01 - W 21 St & 6 Ave
area as the highest-priority planning cluster in this run.

## Key Measures

| Measure | Current Value | Why It Matters |
| --- | ---: | --- |
| Valid trips | 1,886,109 | Confirms the analysis has portfolio-scale data |
| Valid rate | 99.90% | Shows the timestamp and duration filter retained nearly all rows |
| Hourly observations | 744 | One complete January hourly panel |
| Total fixed-window rides | 1,885,763 | Main demand denominator for hourly analysis |
| Average daily rides | 60,831 | Simple scale measure for stakeholder context |
| Average hourly rides | 2,535 | Main hourly demand level |
| Peak hour | 8,635 rides | Highest-demand hour in the fixed window |
| Rush/off-hour ratio | 2.23x | Evidence of commute-driven seasonality |
| Weekend/weekday ratio | 0.71x | Evidence that weekend demand is lower in this winter month |
| Missing hourly periods | 0 | Confirms the fixed hourly panel is regular |
| Lag 24h autocorrelation | 0.753 | Daily repetition signal |
| Lag 168h autocorrelation | 0.710 | Weekly repetition signal |
| Best baseline | Calendar profile | Weekday/hour profile is the strongest simple model |
| Best baseline MAE | 796 rides/hour | Primary forecast error measure |
| Best baseline RMSE | 1,075 rides/hour | Penalizes large misses more than MAE |
| Best rolling-origin baseline | Previous day | Daily 24-hour rolling-origin validation winner |
| Best rolling-origin MAE | 774 rides/hour | Repeated-origin error measure |
| Top station | W 21 St & 6 Ave | Operational extension hook |
| Top 10 station share | 3.25% | Station concentration context |

For the full metric dictionary, see [docs/MEASURES.md](docs/MEASURES.md).

## Full-Year Proof Measures

| Measure | Current Value | Why It Matters |
| --- | ---: | --- |
| Months profiled | 12 | Moves beyond a one-month winter snapshot |
| Raw rows read | 44,303,209 | Confirms the proof uses portfolio-scale public data |
| Valid trips | 44,247,816 | Main quality-filtered source population |
| Fixed-window rides | 44,247,470 | Demand total across the complete 2024 hourly panel |
| Hourly observations | 8,784 | One full leap-year hourly panel |
| Missing hourly periods | 0 | Confirms the longer panel is regular |
| Rolling origins | 44 | Weekly 24-hour forecast starts after 60 training days |
| Best full-year model | Calendar + lag ridge | Simple regularized model using calendar and prior-demand features |
| Best full-year MAE | 750 rides/hour | Primary repeated-origin forecast error measure |
| Previous-week MAE | 918 rides/hour | Strong transparent benchmark the richer model beats |
| Peak hour | 2024-10-22 17:00 | Highest-demand hour in the 2024 panel |
| Peak hourly rides | 19,563 | Scale of the largest observed hourly demand |

## Station-Cluster Forecast Measures

| Measure | Current Value | Why It Matters |
| --- | ---: | --- |
| Top station IDs clustered | 120 | Moves from station names to stable station IDs |
| Station clusters | 6 | Creates operational demand pools for planning |
| Segments modeled | 7 | System total plus 6 station clusters |
| Fixed-window modeled starts | 44,241,607 | Demand denominator used for station shares and forecast panels |
| Rows with station ID | 44,212,111 | Rows available for station grouping after fixed-window filtering |
| Station ID coverage | 99.93% | Confirms nearly all fixed-window rows support station grouping |
| Weather hours joined | 8,784 | Adds full-year exogenous context at hourly grain |
| Event feature dates | 42 | Adds holiday/event windows without hiding the assumptions |
| Weather/event ridge system MAE | 711 rides/hour | Richer full-year aggregate model result |
| Lift vs previous week | 22.7% | Tests against the simplest operating baseline |
| Lift vs calendar-lag ridge | 5.2% | Tests whether weather/events add value beyond lags |
| Clusters beating both baselines | 6 of 6 | Confirms the richer model helped every station cluster in this run |

## Reviewer Path

If you are reviewing this as a portfolio project, start here:

1. Open [outputs/station_cluster_forecast.html](outputs/station_cluster_forecast.html)
   to see the operational upgrade: station ID clusters, weather/event features,
   segment-level rolling validation, and the rebalancing/capacity-planning
   recommendation.
2. Open [outputs/multi_month_proof.html](outputs/multi_month_proof.html)
   to see the stronger proof layer: 12 monthly archives, full-year hourly
   coverage, rolling origins, model comparison, and final forecast trace.
3. Open [outputs/time_series_showcase.html](outputs/time_series_showcase.html)
   to see the time-series methods proof: regular index, autocorrelation, lag
   features, rolling validation, and residual diagnostics.
4. Open [outputs/decision_report.html](outputs/decision_report.html) to see the
   business-facing interpretation and recommendation.
5. Read [docs/STATION_CLUSTER_FORECASTING.md](docs/STATION_CLUSTER_FORECASTING.md),
   [docs/MULTI_MONTH_PROOF.md](docs/MULTI_MONTH_PROOF.md), and
   [docs/TIME_SERIES_SHOWCASE.md](docs/TIME_SERIES_SHOWCASE.md) for the
   interview narrative: what the project proves, what it does not prove, and
   how it should be extended.
6. Read [docs/CODE_QUALITY.md](docs/CODE_QUALITY.md) to see the PEP8, PEP257,
   Ruff, `pydocstyle`, pytest, and coverage checks used before publishing.

## Reports

- [outputs/report.html](outputs/report.html): first-pass time-series profile
  with charts and findings.
- [outputs/decision_report.html](outputs/decision_report.html): portfolio-ready
  recommendation report.
- [outputs/time_series_showcase.html](outputs/time_series_showcase.html):
  expanded time-series methods showcase with autocorrelation, lag features,
  rolling validation, and decomposition-style diagnostics.
- [outputs/multi_month_proof.html](outputs/multi_month_proof.html): full-2024
  forecasting proof with rolling model comparison and source inventory.
- [outputs/station_cluster_forecast.html](outputs/station_cluster_forecast.html):
  station-cluster forecasting report with weather/event features and a
  rebalancing/capacity-planning decision frame.
- [outputs/decision_report_source_notes.md](outputs/decision_report_source_notes.md):
  source and validation notes for the decision report.

## Project Layout

```text
Citi Bike Time Series/
  README.md
  requirements.txt
  .coveragerc
  src/
    citibike_time_series_profile.py
    citibike_decision_report.py
    citibike_time_series_showcase.py
    citibike_multi_month_proof.py
    citibike_station_cluster_forecast.py
  tests/
    test_profile_core.py
    test_decision_and_showcase_core.py
    test_multi_month_core.py
    test_station_cluster_core.py
  outputs/
    report.html
    decision_report.html
    time_series_showcase.html
    multi_month_proof.html
    station_cluster_forecast.html
    decision_report_source_notes.md
    profile_summary.json
    hourly_profile.csv
    forecast_backtest_metrics.csv
    forecast_backtest_scored.csv
    rolling_backtest_metrics.csv
    rolling_backtest_origin_metrics.csv
    rolling_backtest_scored.csv
    autocorrelation_profile.csv
    lag_feature_correlations.csv
    decomposition_components.csv
    time_series_showcase_metrics.csv
    time_series_showcase_coverage.csv
    multi_month_hourly_profile.csv
    multi_month_daily_profile.csv
    multi_month_source_inventory.csv
    multi_month_model_metrics.csv
    multi_month_origin_metrics.csv
    multi_month_backtest_scored.csv
    multi_month_proof_summary.json
    station_cluster_forecast_summary.json
    station_cluster_source_inventory.csv
    station_cluster_station_metadata.csv
    station_cluster_assignments.csv
    station_cluster_summary.csv
    station_cluster_hourly_profile.csv
    station_cluster_weather_hourly.csv
    station_cluster_events.csv
    station_cluster_model_metrics.csv
    station_cluster_model_lift.csv
    station_cluster_capacity_priorities.csv
    station_cluster_origin_metrics.csv
    station_cluster_backtest_scored.csv
    anomaly_hours.csv
    seasonality_profile.csv
    top_stations.csv
    member_mix.csv
    bike_mix.csv
    charts/
      daily_demand.png
      forecast_backtest.png
      seasonality_heatmap.png
      top_stations.png
      autocorrelation_profile.png
      lag_feature_correlations.png
      rolling_backtest_mae.png
      decomposition_proxy.png
      seasonal_residual_distribution.png
      multi_month_daily_demand.png
      multi_month_monthly_volume.png
      multi_month_model_mae.png
      multi_month_origin_mae.png
      multi_month_forecast_example.png
      station_cluster_map.png
      station_cluster_volume.png
      station_cluster_model_lift.png
      station_cluster_segment_mae.png
      station_cluster_forecast_example.png
  data/
    sample_outputs/
  docs/
    CODE_QUALITY.md
    DATA_DICTIONARY.md
    CHART_MAP.md
    MEASURES.md
    METHODOLOGY.md
    MODEL_CARD.md
    STATION_CLUSTER_FORECASTING.md
    PORTFOLIO_WRITEUP.md
    PROJECT_STRUCTURE.md
    PUBLISHING_CHECKLIST.md
    ROADMAP.md
    TIME_SERIES_SHOWCASE.md
```

## Reproduce

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Verify code quality:

```bash
python -m ruff format src
python -m ruff check src
python -m pydocstyle src
python -m coverage run -m pytest
python -m coverage report
```

Run the profile pipeline:

```bash
python src/citibike_time_series_profile.py
```

Build the decision report:

```bash
python src/citibike_decision_report.py
```

Build the expanded time-series showcase report:

```bash
python src/citibike_time_series_showcase.py
```

Build the full-2024 proof layer:

```bash
python src/citibike_multi_month_proof.py --start-month 2024-01 --end-month 2024-12
```

Build the station-cluster forecasting layer:

```bash
python src/citibike_station_cluster_forecast.py --start-month 2024-01 --end-month 2024-12 --skip-download
```

The profile and multi-month scripts download public Citi Bike archives and
store local cache files under `work/data/`. Those raw downloaded files are
intentionally ignored by Git because the source archives are large and public.

## Data Sources

- Citi Bike public trip-history archive:
  `https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip`
- Citi Bike public monthly trip-history archives for Jan.-Dec. 2024:
  `https://s3.amazonaws.com/tripdata/YYYYMM-citibike-tripdata.zip`
- Open-Meteo historical weather archive for New York City, Jan. 1-Dec. 31, 2024

## Important Caveats

- The January method layer is a one-month winter profile; the multi-month proof
  extends forecast validation but is still not a production operations model.
- Citi Bike timestamps are parsed as timezone-naive by pandas in this version.
- Station-cluster forecasts model trip starts, not live bike inventory, station
  capacity, dock availability, or rebalancing truck moves.
- Weather correlations are descriptive and should not be read as causal.
- Forecast intervals are simple residual reference bands, not calibrated
  prediction intervals.
- The full-year ridge model is intentionally simple and transparent; it is a
  stronger benchmark, not a claim of best-possible accuracy.
- The weather/event ridge layer uses observed historical weather as a stand-in
  for forecast weather that would need to be available before an operating day.
