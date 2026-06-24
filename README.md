# Data Science AI Portfolio

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Coverage 100%](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](Linked_List_Showcase/README.md#testing)

This repository is organized as a portfolio workspace. Each major top-level
folder is intended to stand on its own as a project with its own README,
dependencies, examples, tests, and technical writeup.

The portfolio currently includes a code-heavy data-structures showcase and an
analytics-heavy time-series forecasting showcase. Together, they demonstrate
implementation skill, reproducible analysis, baseline modeling, documentation,
CI discipline, and the ability to explain technical tradeoffs clearly.

## Projects

| Project | Location | What it demonstrates | Status |
| --- | --- | --- | --- |
| Linked List Showcase | [`Linked_List_Showcase`](Linked_List_Showcase) | Python package design, linked data structures, typed APIs, 100% coverage, CI, examples, benchmarks, and educational documentation | Complete showcase |
| Citi Bike Demand Forecasting | [`Citi Bike Time Series`](Citi%20Bike%20Time%20Series) | Public data acquisition, hourly time-series profiling, seasonality, leakage-aware baselines, rolling validation, anomaly screening, and business-facing reporting | Complete showcase; ready for longer-horizon extension |

## Featured Project: Linked List Showcase

`Linked_List_Showcase` contains the installable `linked-structure-lab`
package. It implements and tests:

- singly, doubly, singly circular, and doubly circular linked lists
- linked deque
- sorted linked list
- skip list
- unrolled linked list
- multilevel linked list
- positional linked list
- self-organizing linked list
- sparse matrix linked list

Fast reviewer path:

```bash
cd Linked_List_Showcase
python -m pip install -e ".[dev]"
python -m pytest
python -m coverage run -m pytest
python -m coverage report
```

PyCharm setup note:

The import package is `linked_list`, but it lives in the nested
`Linked_List_Showcase/src` directory. If PyCharm says it cannot find
`linked_list`, use a Python 3.12+ interpreter and install the showcase project
in editable mode:

```bash
cd Linked_List_Showcase
python -m pip install -e ".[dev]"
```

Alternatively, mark `Linked_List_Showcase/src` as a PyCharm Sources Root.

Best entry points:

- [Project README](Linked_List_Showcase/README.md): install, examples, API
  overview, edge cases, and testing strategy.
- [Reviewer Demo Script](Linked_List_Showcase/docs/demo_script.md): a 3-5
  minute run path for checks, examples, and source-test inspection.
- [Portfolio Showcase](Linked_List_Showcase/docs/portfolio_showcase.md):
  reviewer-facing summary of what the project proves.
- [Benchmark Results](Linked_List_Showcase/docs/benchmark_results.md):
  measured output and interpretation for the educational structures.
- [Source Walkthrough](Linked_List_Showcase/docs/linked_structures_walkthrough.md):
  beginner-friendly explanation of invariants and pointer repair.
- [Portfolio Roadmap](PORTFOLIO_ROADMAP.md): how future top-level projects
  should be organized.

## Featured Project: Citi Bike Demand Forecasting

`Citi Bike Time Series` is a public-data analytics case study built around New
York City Citi Bike trip history. It turns January 2024 trip starts into a
regular hourly demand panel, then profiles seasonality, autocorrelation, lag
signals, baseline forecasts, rolling-origin validation, anomaly candidates, and
decision-ready reports.

The project is intentionally honest about scope: it is a portfolio-grade
time-series showcase, not a production forecasting system. Its best next
extension would be a 12-24 month panel with stable station identifiers,
seasonal backtests, and station-cluster forecasts tied to a concrete operational
decision.

Fast reviewer path:

```bash
cd "Citi Bike Time Series"
python -m pip install -r requirements.txt
python src/citibike_time_series_showcase.py
```

Best entry points:

- [Project README](Citi%20Bike%20Time%20Series/README.md): project purpose,
  key measures, source data, caveats, and reproduction steps.
- [Time-Series Showcase Report](Citi%20Bike%20Time%20Series/outputs/time_series_showcase.html):
  reviewer-ready HTML report covering regular indexing, seasonality,
  autocorrelation, lag features, rolling validation, and residual diagnostics.
- [Decision Report](Citi%20Bike%20Time%20Series/outputs/decision_report.html):
  business-facing interpretation of the current January 2024 profile.
- [Time-Series Showcase Notes](Citi%20Bike%20Time%20Series/docs/TIME_SERIES_SHOWCASE.md):
  interview narrative explaining what the project proves, what it does not
  prove, and how it should be extended.
- [Measures](Citi%20Bike%20Time%20Series/docs/MEASURES.md): metric definitions,
  formulas, outputs, and caveats.

## Repository Layout

```text
.github/
  workflows/
    ci.yml
    tests.yml
Citi Bike Time Series/
  docs/
  outputs/
    charts/
  src/
    citibike_decision_report.py
    citibike_time_series_profile.py
    citibike_time_series_showcase.py
  README.md
  requirements.txt
Linked_List_Showcase/
  benchmarks/
  docs/
  examples/
  src/
    linked_list/
  tests/
  CHANGELOG.md
  pyproject.toml
  README.md
  requirements-dev.txt
.gitignore
.pre-commit-config.yaml
LICENSE
PORTFOLIO_ROADMAP.md
README.md
```

## Portfolio Structure

Future projects should be added as separate top-level folders, for example:

```text
analytics-dashboard/
customer-segmentation/
forecasting-case-study/
ml-model-monitoring/
```

The root README stays a concise map. Each project folder should carry the
full explanation, setup instructions, validation notes, and artifacts for that
specific project. See [Portfolio Roadmap](PORTFOLIO_ROADMAP.md) for the
folder contract and future project slots.
