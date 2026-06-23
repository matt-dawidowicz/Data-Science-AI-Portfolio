# Chart Map

This document records the purpose of each generated visual. It is meant to help
reviewers understand why each chart exists and to keep the visual system from
turning into decoration.

## Existing Profile Charts

| Chart | File | Chart Family | Question | Supported Takeaway |
| --- | --- | --- | --- | --- |
| Daily demand | `outputs/charts/daily_demand.png` | Trend line | How does total daily demand move across the month? | Demand varies materially by day, so date context matters. |
| Seasonality heatmap | `outputs/charts/seasonality_heatmap.png` | Heatmap | Which weekday/hour combinations carry the most demand? | Commute-period seasonality is a visible first-order signal. |
| Forecast backtest | `outputs/charts/forecast_backtest.png` | Multi-series trend | How does the selected baseline compare with actual holdout demand? | Calendar-profile baseline tracks broad shape but misses some spikes. |
| Top stations | `outputs/charts/top_stations.png` | Ranked horizontal bar | Which stations account for the most starts? | Station concentration is low but useful for an operational extension. |

## Showcase Charts

| Chart | File | Chart Family | Question | Supported Takeaway |
| --- | --- | --- | --- | --- |
| Autocorrelation profile | `outputs/charts/autocorrelation_profile.png` | Trend line | Which lags retain relationship with hourly rides? | Daily and weekly lags should be considered before heavier models. |
| Lag feature correlations | `outputs/charts/lag_feature_correlations.png` | Diverging horizontal bar | Which lag, rolling, and weather candidates are most associated with demand? | Lag and rolling features provide stronger simple signal than raw weather correlations. |
| Rolling backtest MAE | `outputs/charts/rolling_backtest_mae.png` | Ranked horizontal bar | Which baseline performs best across rolling origins? | Rolling-origin scoring gives a more honest model comparison than one split alone. |
| Decomposition proxy | `outputs/charts/decomposition_proxy.png` | Multi-series trend | How do actual demand, rolling trend, and seasonal expected value relate? | The project can explain level, seasonality, and residual movement separately. |
| Seasonal residual distribution | `outputs/charts/seasonal_residual_distribution.png` | Histogram | How large are deviations after accounting for weekday/hour seasonality? | Residual spread identifies anomaly candidates without claiming root cause. |

## Palette And Encoding Notes

- Trend and lag structure use blue as the primary analytical color.
- Model evaluation uses gold.
- Signed or residual-oriented views use orange, olive, or pink with explicit
  zero/reference lines.
- Static HTML reports use PNG images so the project remains portable on GitHub.

## Quality Checks

Before publishing:

- Open each HTML report locally.
- Confirm every image renders.
- Confirm titles and subtitles state metric grain and time window.
- Confirm no chart implies causality from descriptive weather correlations.
- Confirm one-month limitations are visible near the chart narrative.

