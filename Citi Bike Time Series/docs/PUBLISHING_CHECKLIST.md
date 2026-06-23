# Publishing Checklist

Use this before adding the project to the portfolio repository.

## Files To Include

- `README.md`
- `requirements.txt`
- `.gitignore`
- `src/citibike_time_series_profile.py`
- `src/citibike_decision_report.py`
- `src/citibike_time_series_showcase.py`
- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`
- `outputs/profile_summary.json`
- `outputs/forecast_backtest_metrics.csv`
- `outputs/rolling_backtest_metrics.csv`
- `outputs/autocorrelation_profile.csv`
- `outputs/lag_feature_correlations.csv`
- `outputs/decomposition_components.csv`
- `outputs/time_series_showcase_metrics.csv`
- `outputs/time_series_showcase_coverage.csv`
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
python src/citibike_decision_report.py
python src/citibike_time_series_showcase.py
```

Then manually open:

- `outputs/report.html`
- `outputs/decision_report.html`
- `outputs/time_series_showcase.html`

Check:

- All images render.
- The executive summary is visible near the top.
- Measure values match `docs/MEASURES.md`.
- The caveats are not hidden.
- No raw local absolute paths appear in the visible report body.
- The showcase report labels decomposition as descriptive/proxy analysis.
- Rolling-origin metrics are described as validation practice, not production
  performance.

## Suggested Portfolio Repository Placement

Place the folder beside the existing linked-list project:

```text
Data-Science-AI-Portfolio/
  Linked Lists/
  Citi Bike Time Series/
```

The repository README should add a short project card under a new analytics or
time-series section.

## Suggested Repository README Entry

```md
### Citi Bike Demand Forecasting

Time-series profiling and baseline forecasting project built from public Citi
Bike trip-history data. The analysis processes 1.89M trips, creates an hourly
demand panel, evaluates calendar and lag baselines, detects anomaly candidates,
and produces portfolio-ready HTML reports.

- Skills: pandas, time-series features, baseline forecasting, anomaly
  detection, Seaborn/Matplotlib, report generation
- Main report: `Citi Bike Time Series/outputs/decision_report.html`
- Documentation: `Citi Bike Time Series/docs/`
```

## Future Enhancements Before A Public Showcase

The current project is publishable as a first-pass portfolio case study. To make
it stronger:

1. Extend the data pull to 12-24 months.
2. Add station IDs and station metadata.
3. Add rolling holdout windows.
4. Add a stronger model after the baseline.
5. Add event and outage context for anomaly interpretation.
