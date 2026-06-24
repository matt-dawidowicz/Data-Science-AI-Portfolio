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
- Expanded validation: daily rolling 24-hour origins in the second half of
  January
- Full-year validation: weekly 24-hour origins from Mar. 1 through Dec. 27,
  2024 after a 60-day training warmup
- Unit: rides per hour

## Baselines

| Baseline | Description | Strength | Weakness |
| --- | --- | --- | --- |
| Previous day | Uses the value from 24 hours earlier | Simple and reactive | Weak when weekday pattern changes |
| Previous week | Uses the value from 168 hours earlier | Captures weekly rhythm | Needs enough prior history |
| Calendar profile | Uses average training volume for same weekday and hour | Captures commute shape | Smooths event spikes and unusual weather |

The expanded showcase script also evaluates an `hour_of_day_profile` baseline
across rolling origins. That baseline uses the expanding training average for
the same hour of day, without separating weekdays from weekends.

The full-year proof adds two more models:

| Model | Description | Strength | Weakness |
| --- | --- | --- | --- |
| Seasonal lag blend | 65% weekday/hour profile plus 35% previous-week forecast | Combines smooth seasonality with a recent seasonal anchor | Still hand-weighted and simple |
| Calendar + lag ridge | Regularized linear model using calendar cycles, holiday/weekend flags, elapsed time, lag 24h, lag 168h, and rolling means anchored one day back | Transparent stronger benchmark with leakage-aware features | Does not include weather, events, or station-level context |

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

## Rolling-Origin Validation

The expanded showcase adds rolling 24-hour forecast origins. These outputs are:

- `outputs/rolling_backtest_metrics.csv`
- `outputs/rolling_backtest_origin_metrics.csv`
- `outputs/rolling_backtest_scored.csv`

This shows stronger time-series evaluation practice than a single holdout
alone. It is still constrained by the one-month source window, so the results
should be presented as portfolio validation evidence rather than production
performance.

## Full-Year Rolling Validation

The multi-month proof outputs are:

- `outputs/multi_month_model_metrics.csv`
- `outputs/multi_month_origin_metrics.csv`
- `outputs/multi_month_backtest_scored.csv`
- `outputs/multi_month_proof.html`

Current full-year results:

| Model | MAE | RMSE | MAPE | Origin Win Rate |
| --- | ---: | ---: | ---: | ---: |
| Calendar + lag ridge | 750 | 1,163 | 28.1% | 36.4% |
| Previous week | 918 | 1,538 | 22.9% | 36.4% |
| Previous day | 1,034 | 1,547 | 23.4% | 11.4% |
| Seasonal lag blend | 1,350 | 1,831 | 29.0% | 9.1% |
| Weekday/hour profile | 1,792 | 2,369 | 36.7% | 6.8% |
| Hour-of-day profile | 1,970 | 2,550 | 38.5% | 0.0% |

The calendar + lag ridge model is best by MAE and RMSE across 44 origins.
Previous week has lower MAPE, so the report explicitly keeps MAE as the primary
portfolio metric and treats percentage error as a secondary diagnostic.

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

- One January holdout window is not enough to estimate stable future
  performance; the full-year proof addresses this with 44 rolling origins.
- The full-year proof measures annual pattern better than January alone, but it
  still does not prove production performance under future regime changes.
- Overnight low-volume hours can distort percentage error.
- Events, outages, and severe weather are not explicitly modeled.
- Station-level modeling needs stable station identifiers.
- The decomposition output is a descriptive proxy, not formal STL or annual
  decomposition.
- The full-year ridge model is a transparent benchmark, not a claim of
  best-possible accuracy.

## Recommended Next Model Step

The next modeling step should be station-cluster forecasting:

1. Add stable station IDs, station metadata, and station grouping.
2. Keep previous-week and calendar + lag ridge as benchmarks.
3. Add weather and event features only after they are tested in rolling
   validation.
4. Compare aggregate, station-cluster, and top-station performance separately.
5. Choose one operating decision, such as rebalancing or capacity planning, and
   tune the target grain and error metric to that decision.
