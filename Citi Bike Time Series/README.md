# Citi Bike Demand Forecasting

Time-series profiling and baseline forecasting project built from public Citi
Bike trip-history data. The project turns raw January 2024 trip starts into an
hourly demand profile, calendar features, weather context, anomaly candidates,
baseline forecast evaluation, rolling-origin validation, autocorrelation and lag
diagnostics, charts, and decision-ready HTML reports.

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
- Rolling-origin forecast validation
- Anomaly detection against a seasonal profile
- Business-facing reporting and documentation

## Headline Result

The current January 2024 profile shows enough temporal structure to justify a
larger forecasting project. Citi Bike demand has a visible commute pattern:
rush-hour volume averaged 2.23x off-hour volume, weekends averaged 0.71x
weekday hourly volume, and a simple weekday/hour calendar profile beat the
previous-day and previous-week baselines on MAE over the Jan. 25-31 holdout.

The project now has a dedicated time-series showcase layer. It demonstrates
regular time indexing, seasonality, smoothing, autocorrelation, lag features,
rolling backtests, residual analysis, and forecast governance. The recommended
next portfolio step is to extend the dataset to 12-24 months, add stable station
identifiers, and build station-cluster forecasts or anomaly alerts around a
specific decision such as rebalancing or station planning.

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

## Reviewer Path

If you are reviewing this as a portfolio project, start here:

1. Open [outputs/time_series_showcase.html](outputs/time_series_showcase.html)
   to see the time-series methods proof: regular index, autocorrelation, lag
   features, rolling validation, and residual diagnostics.
2. Open [outputs/decision_report.html](outputs/decision_report.html) to see the
   business-facing interpretation and recommendation.
3. Read [docs/TIME_SERIES_SHOWCASE.md](docs/TIME_SERIES_SHOWCASE.md) for the
   interview narrative: what the project proves, what it does not prove, and
   how it should be extended.

## Reports

- [outputs/report.html](outputs/report.html): first-pass time-series profile
  with charts and findings.
- [outputs/decision_report.html](outputs/decision_report.html): portfolio-ready
  recommendation report.
- [outputs/time_series_showcase.html](outputs/time_series_showcase.html):
  expanded time-series methods showcase with autocorrelation, lag features,
  rolling validation, and decomposition-style diagnostics.
- [outputs/decision_report_source_notes.md](outputs/decision_report_source_notes.md):
  source and validation notes for the decision report.

## Project Layout

```text
Citi Bike Time Series/
  README.md
  requirements.txt
  src/
    citibike_time_series_profile.py
    citibike_decision_report.py
    citibike_time_series_showcase.py
  outputs/
    report.html
    decision_report.html
    time_series_showcase.html
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
  data/
    sample_outputs/
  docs/
    DATA_DICTIONARY.md
    CHART_MAP.md
    MEASURES.md
    METHODOLOGY.md
    MODEL_CARD.md
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

The profile script downloads the public Citi Bike archive and stores local
cache files under `work/data/`. Those raw downloaded files are intentionally
ignored by Git because the source archive is large and public.

## Data Sources

- Citi Bike public trip-history archive:
  `https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.zip`
- Open-Meteo historical weather archive for New York City, Jan. 1-31, 2024

## Important Caveats

- This is a one-month winter profile, not a production forecast.
- Citi Bike timestamps are parsed as timezone-naive by pandas in this version.
- Station outputs currently use station names, not stable station IDs.
- Weather correlations are descriptive and should not be read as causal.
- Forecast intervals are simple residual reference bands, not calibrated
  prediction intervals.
