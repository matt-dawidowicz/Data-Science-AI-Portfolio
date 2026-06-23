# Model Card

This model card covers the baseline forecasting component of the Citi Bike
time-series project.

## Model Purpose

The forecasting component is designed to create a transparent benchmark for a
portfolio time-series showcase. It is not intended to be a production
operations model.

## Forecast Target

- Target: hourly valid Citi Bike trip starts
- Grain: hour
- Forecast period: Jan. 25-31, 2024
- Training period: Jan. 1-24, 2024
- Unit: rides per hour

## Baselines

| Baseline | Description | Strength | Weakness |
| --- | --- | --- | --- |
| Previous day | Uses the value from 24 hours earlier | Simple and reactive | Weak when weekday pattern changes |
| Previous week | Uses the value from 168 hours earlier | Captures weekly rhythm | Needs enough prior history |
| Calendar profile | Uses average training volume for same weekday and hour | Captures commute shape | Smooths event spikes and unusual weather |

## Evaluation Metrics

| Metric | Why It Is Used |
| --- | --- |
| MAE | Main stakeholder-friendly error measure in rides per hour |
| RMSE | Penalizes larger misses more than MAE |
| MAPE | Shows percentage error, but can be unstable in low-volume hours |
| Mean actual | Gives denominator context for the holdout |

## Current Results

| Model | MAE | RMSE | MAPE |
| --- | ---: | ---: | ---: |
| Calendar profile | 796 | 1,075 | 36.2% |
| Previous week | 872 | 1,277 | 29.7% |
| Previous day | 1,001 | 1,581 | 56.3% |

The calendar profile is the best baseline by MAE and RMSE. Previous week has a
lower MAPE, which should be noted when explaining the model choice.

## Intended Use

Use this baseline to answer:

- Is there enough regular temporal structure to forecast?
- What simple benchmark should a stronger model beat?
- Where do actuals depart from expected weekday/hour behavior?
- Which model errors are large enough to warrant anomaly context?

## Not Intended For

Do not use this baseline as:

- A live rebalancing model
- A staffing forecast
- A station-level production forecast
- A causal weather model
- A calibrated uncertainty model

## Risks And Caveats

- One holdout window is not enough to estimate stable future performance.
- One winter month cannot measure annual seasonality.
- Overnight low-volume hours can distort percentage error.
- Events, outages, and severe weather are not explicitly modeled.
- Station-level modeling needs stable station identifiers.

## Recommended Next Model Step

The next modeling step should be:

1. Extend to 12-24 months.
2. Add rolling holdout windows.
3. Keep the calendar profile as the benchmark.
4. Add one stronger model, such as SARIMAX or a gradient-boosted lag-feature
   model.
5. Compare aggregate and station-cluster performance separately.
