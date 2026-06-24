# Publishing Checklist

Use this before adding the project to the portfolio repository.

## Files To Include

- `README.md`
- `requirements.txt`
- `.gitignore`
- `src/citibike_time_series_profile.py`
- `src/citibike_decision_report.py`
- `src/citibike_time_series_showcase.py`
- `src/citibike_multi_month_proof.py`
- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`
- `outputs/multi_month_proof.html`
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
- `outputs/anomaly_hours.csv`
- `outputs/top_stations.csv`
- `outputs/member_mix.csv`
- `outputs/bike_mix.csv`
- `outputs/charts/*.png`
- `data/sample_outputs/*.csv`
- `data/sample_outputs/profile_summary.json`
- `docs/*.md`

## Files To Exclude

- `work/`
- Downloaded raw Citi Bike ZIP files
- Downloaded weather cache files
- `__pycache__/`
- Local notebook checkpoints
- Any temporary rendering screenshots

## Pre-Push Checks

Run these from the project folder:

```bash
python -m py_compile src/citibike_time_series_profile.py
python -m py_compile src/citibike_decision_report.py
python -m py_compile src/citibike_time_series_showcase.py
python -m py_compile src/citibike_multi_month_proof.py
python src/citibike_decision_report.py
python src/citibike_time_series_showcase.py
python src/citibike_multi_month_proof.py --start-month 2024-01 --end-month 2024-12 --skip-download
```

Then manually open:

- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`
- `outputs/multi_month_proof.html`

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
forecast origins, transparent baselines, and a calendar-lag ridge benchmark.

- Skills: pandas, time-series features, baseline forecasting, anomaly
  detection, Seaborn/Matplotlib, report generation
- Main report: `Citi Bike Time Series/outputs/multi_month_proof.html`
- Documentation: `Citi Bike Time Series/docs/`
```

## Future Enhancements Before A Public Showcase

The current project is publishable as a stronger portfolio case study. To make
it more operational:

1. Add station IDs and station metadata.
2. Build station-cluster forecasts.
3. Add weather and event features to the rolling validation loop.
4. Compare aggregate and station-cluster error separately.
5. Add event and outage context for anomaly interpretation.
