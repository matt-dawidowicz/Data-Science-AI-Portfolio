# Dashboard And Decision Simulator

The portfolio dashboard is a reviewer-first surface built from generated,
source-backed outputs. It does not retrain the forecasting models. It reads the
validated CSV and JSON artifacts in `outputs/` and creates a compact dashboard,
decision simulator, and feature-family explainability table.

## Generated Files

Run:

```bash
python src/citibike_portfolio_dashboard.py
```

The command writes:

| File | Purpose |
| --- | --- |
| `outputs/portfolio_dashboard.html` | Static dashboard for reviewers |
| `outputs/portfolio_decision_simulator.csv` | Scenario-level rebalancing review table |
| `outputs/portfolio_feature_family_lift.csv` | Feature-family lift and interpretation table |

## Dashboard Sections

The dashboard includes:

- full-year proof KPIs,
- station-cluster forecast KPIs,
- model lift against the previous-week baseline,
- a scenario simulator,
- feature-family explainability,
- model comparison tables,
- core charts from the forecasting reports,
- source and limitation notes.

The dashboard is intentionally static HTML so it can live inside the portfolio
repo without requiring a running server or Streamlit deployment.

## Simulator Scenarios

The simulator has three built-in scenarios:

| Scenario | Meaning |
| --- | --- |
| Normal weekday | Standard planning review |
| Rain or snow pressure | Weather-pressure review where observed weather tends to affect demand |
| Major event window | Event-window review where local demand may concentrate around clusters |

Each scenario scores station clusters using:

- annual cluster demand scale,
- weather/event model MAE,
- weather/event model WAPE,
- lift versus the previous-week baseline,
- scenario demand pressure.

The output tier is:

- `High`: pre-review capacity and bike positioning,
- `Medium`: monitor against the previous-week baseline during peak hours,
- `Monitor`: keep on the watchlist without demand-only action.

## Feature Explainability

The feature-family table explains model value through out-of-sample lift rather
than in-sample coefficients. It compares:

1. Calendar and lag features against the previous-week baseline.
2. Weather and event features against the calendar + lag ridge.

This is the right explanation for a portfolio project because it answers:

> Did the extra feature family reduce validation error?

It avoids overclaiming causality or treating coefficients as operational truth.

## Caveat

The simulator is not an optimizer. It is a planning-review surface. A production
rebalancing tool would need station capacity, live availability, available
docks, truck constraints, and service-level targets.
