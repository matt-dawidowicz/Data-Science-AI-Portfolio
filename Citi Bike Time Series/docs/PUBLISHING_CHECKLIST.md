# Publishing Checklist

Use this before adding the project to the portfolio repository.

## Files To Include

- `README.md`
- `requirements.txt`
- `.gitignore`
- `.coveragerc`
- `src/citibike_time_series_profile.py`
- `src/citibike_decision_report.py`
- `src/citibike_time_series_showcase.py`
- `src/citibike_multi_month_proof.py`
- `src/citibike_station_cluster_forecast.py`
- `src/citibike_portfolio_dashboard.py`
- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`
- `outputs/multi_month_proof.html`
- `outputs/station_cluster_forecast.html`
- `outputs/portfolio_dashboard.html`
- `outputs/profile_summary.json`
- `outputs/forecast_backtest_metrics.csv`
- `outputs/rolling_backtest_metrics.csv`
- `outputs/autocorrelation_profile.csv`
- `outputs/lag_feature_correlations.csv`
- `outputs/decomposition_components.csv`
- `outputs/time_series_showcase_metrics.csv`
- `outputs/time_series_showcase_coverage.csv`
- `outputs/multi_month_proof_summary.json`
- `outputs/multi_month_hourly_profile.csv`
- `outputs/multi_month_daily_profile.csv`
- `outputs/multi_month_source_inventory.csv`
- `outputs/multi_month_model_metrics.csv`
- `outputs/multi_month_origin_metrics.csv`
- `outputs/multi_month_backtest_scored.csv`
- `outputs/multi_month_top_stations.csv`
- `outputs/station_cluster_forecast_summary.json`
- `outputs/station_cluster_source_inventory.csv`
- `outputs/station_cluster_station_metadata.csv`
- `outputs/station_cluster_assignments.csv`
- `outputs/station_cluster_summary.csv`
- `outputs/station_cluster_hourly_profile.csv`
- `outputs/station_cluster_weather_hourly.csv`
- `outputs/station_cluster_events.csv`
- `outputs/station_cluster_model_metrics.csv`
- `outputs/station_cluster_model_lift.csv`
- `outputs/station_cluster_capacity_priorities.csv`
- `outputs/portfolio_feature_family_lift.csv`
- `outputs/portfolio_decision_simulator.csv`
- `outputs/station_cluster_origin_metrics.csv`
- `outputs/station_cluster_backtest_scored.csv`
- `outputs/anomaly_hours.csv`
- `outputs/top_stations.csv`
- `outputs/member_mix.csv`
- `outputs/bike_mix.csv`
- `outputs/charts/*.png`
- `data/sample_outputs/*.csv`
- `data/sample_outputs/profile_summary.json`
- `docs/*.md`
- `tests/*.py`

## Files To Exclude

- `work/`
- Downloaded raw Citi Bike ZIP files
- Downloaded weather cache files
- `__pycache__/`
- `.coverage`
- `htmlcov/`
- Local notebook checkpoints
- Any temporary rendering screenshots

## Pre-Push Checks

Run these from the project folder:

```bash
python -m ruff format src
python -m ruff check src
python -m pydocstyle src
python -m coverage run -m pytest
python -m coverage report
python -m py_compile src/citibike_time_series_profile.py
python -m py_compile src/citibike_decision_report.py
python -m py_compile src/citibike_time_series_showcase.py
python -m py_compile src/citibike_multi_month_proof.py
python -m py_compile src/citibike_station_cluster_forecast.py
python -m py_compile src/citibike_portfolio_dashboard.py
python src/citibike_decision_report.py
python src/citibike_time_series_showcase.py
python src/citibike_multi_month_proof.py --start-month 2024-01 --end-month 2024-12 --skip-download
python src/citibike_station_cluster_forecast.py --start-month 2024-01 --end-month 2024-12 --skip-download --skip-weather-download
python src/citibike_portfolio_dashboard.py
```

Then manually open:

- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`
- `outputs/multi_month_proof.html`
- `outputs/station_cluster_forecast.html`
- `outputs/portfolio_dashboard.html`

Check:

- All images render.
- The executive summary is visible near the top.
- Measure values match `docs/MEASURES.md`.
- The caveats are not hidden.
- No raw local absolute paths appear in the visible report body.
- The showcase report labels decomposition as descriptive/proxy analysis.
- Rolling-origin metrics are described as validation practice, not production
  performance.
- The multi-month proof clearly says it is a stronger benchmark, not a
  production operations model.
- The station-cluster report says trip-start forecasts are not bike inventory,
  station capacity, or dock availability.
- Weather/event lift is shown against both previous-week and calendar-lag ridge
  baselines.
- The portfolio dashboard scenario buttons filter the simulator table.
- The simulator is described as a planning index, not an operations optimizer.
- Feature-family lift is explained as out-of-sample improvement, not causal
  attribution.
- `docs/CODE_QUALITY.md` reflects the exact style checks that passed locally.
- Coverage reports 100% for the configured deterministic unit-test layer, and
  the `.coveragerc` exclusions are limited to integration/reporting paths.

## Suggested Portfolio Repository Placement

Place the folder beside the existing linked-list project:

```text
Data-Science-AI-Portfolio/
  Linked_List_Showcase/
  Citi Bike Time Series/
```

The repository README should add a short project card under a new analytics or
time-series section.

## Suggested Repository README Entry

```md
### Citi Bike Demand Forecasting

Time-series profiling and forecasting project built from public Citi Bike
trip-history data. The analysis starts with a January methods layer, then adds
a full-2024 proof with 44.25M valid rows, 8,784 hourly observations, 44 rolling
forecast origins, transparent baselines, a calendar-lag ridge benchmark, and a
station-cluster layer for rebalancing/capacity planning.

- Skills: pandas, time-series features, baseline forecasting, grouped time
  series, weather/event features, anomaly framing, Seaborn/Matplotlib, report
  generation
- Main report: `Citi Bike Time Series/outputs/station_cluster_forecast.html`
- Documentation: `Citi Bike Time Series/docs/`
```

## Future Enhancements Before A Public Showcase

The current project is publishable as a stronger portfolio case study. To make
it more operational:

1. Add station capacity and live availability snapshots.
2. Evaluate stockout or full-dock risk after forecasted demand pressure.
3. Add calibrated alert thresholds for rebalancing review.
4. Compare performance by commute peak, weather pressure, and event windows.
5. Add outage and station-status context for anomaly interpretation.
