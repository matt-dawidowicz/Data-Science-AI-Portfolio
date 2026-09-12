# Data Science & Applied AI Portfolio

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

This repository collects selected projects in applied data science, forecasting,
software verification, and AI-assisted engineering.

The goal is not to treat raw code volume as proof of ability. Modern development
workflows can generate large amounts of code quickly. The portfolio therefore
emphasizes the parts of technical work that remain reviewable: problem framing,
experimental design, model evaluation, invariants, tests, benchmarks,
tradeoffs, reproducibility, and clear technical explanation.

## Start Here

| Project | Primary signal | Reviewer path |
| --- | --- | --- |
| [Citi Bike Demand Forecasting](Citi%20Bike%20Time%20Series) | Applied data science, time-series modeling, rolling validation, operational decision framing, and large public-data processing | [Project README](Citi%20Bike%20Time%20Series/README.md) |
| [Linked Structure Lab](Linked_List_Showcase) | Engineering fundamentals, invariants, property-based testing, typed APIs, CI, benchmarks, and software verification | [Project README](Linked_List_Showcase/README.md) |

## Featured Applied Data Science Project: Citi Bike Demand Forecasting

The Citi Bike project is the primary data-science case study in this portfolio.
It processes a full year of public trip history, builds regular hourly demand
panels, compares transparent forecasting baselines, performs leakage-aware
rolling validation, evaluates calendar/lag/weather/event features, models
station clusters, and connects the results to rebalancing and capacity-planning
decisions.

The current full-year proof layer covers more than 44 million valid trip rows
and 8,784 hourly observations. The project intentionally documents limitations
and distinguishes a reproducible portfolio case study from a production demand
forecasting system.

Useful entry points:

- [Project README](Citi%20Bike%20Time%20Series/README.md)
- [Portfolio dashboard](Citi%20Bike%20Time%20Series/outputs/portfolio_dashboard.html)
- [Station-cluster forecast report](Citi%20Bike%20Time%20Series/outputs/station_cluster_forecast.html)
- [Full-year proof report](Citi%20Bike%20Time%20Series/outputs/multi_month_proof.html)
- [Case study](Citi%20Bike%20Time%20Series/docs/CASE_STUDY.md)
- [Limitations](Citi%20Bike%20Time%20Series/docs/LIMITATIONS.md)

## Engineering Fundamentals Project: Linked Structure Lab

The linked-structure project began as a deliberately exhaustive response to
classic data-structure interview preparation. It is now kept as an engineering
fundamentals and verification lab rather than as the portfolio's flagship
project.

The package includes classic and specialized linked structures, typed public
APIs, examples, benchmarks, CI, regression tests, and property-based tests.
The interesting part is not that linked lists were implemented from scratch;
it is that structural invariants and observable behavior are made explicit and
then verified across mutations and randomized operation sequences.

Development of this project used AI coding assistance. That is intentional and
is not presented as manual authorship of every line. The engineering signal is
in defining the required behavior, reviewing implementations, constructing
strong tests, checking invariants, benchmarking results, and being able to
explain the design and failure modes.

Useful entry points:

- [Project README](Linked_List_Showcase/README.md)
- [Verification-focused portfolio summary](Linked_List_Showcase/docs/portfolio_showcase.md)
- [Benchmark results](Linked_List_Showcase/docs/benchmark_results.md)
- [Source walkthrough](Linked_List_Showcase/docs/linked_structures_walkthrough.md)
- [Reviewer demo script](Linked_List_Showcase/docs/demo_script.md)

## Development Philosophy

This portfolio treats AI coding tools as part of a modern engineering workflow,
not as evidence by themselves. A generated implementation is not considered
finished because it looks plausible or because a test suite is green.

Projects should make the following inspectable whenever practical:

- the problem and constraints;
- baselines and comparison points;
- validation methodology;
- tests that establish meaningful properties rather than merely execute code;
- benchmarks and measured tradeoffs;
- failure cases and limitations;
- reproducible run instructions;
- the reasoning behind architecture, modeling, or evaluation choices.

The next major portfolio addition should extend this evidence model into applied
AI: retrieval, reranking, embeddings, evaluation, latency/cost measurement, and
failure analysis rather than a generic chatbot demo.

## Repository Layout

```text
.github/
  workflows/
    ci.yml
Citi Bike Time Series/
  docs/
  outputs/
  src/
  tests/
  README.md
Linked_List_Showcase/
  benchmarks/
  docs/
  examples/
  src/
    linked_list/
  tests/
  README.md
PORTFOLIO_ROADMAP.md
README.md
```

See [PORTFOLIO_ROADMAP.md](PORTFOLIO_ROADMAP.md) for the current portfolio
priorities and the contract for future projects.
