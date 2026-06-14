# Portfolio Roadmap

This repository is organized as a portfolio workspace. Each major top-level
folder should be a complete project that can be reviewed on its own, with its
own setup instructions, tests, examples, and documentation.

The goal is to show range without turning the repository into one tangled
application. A reviewer should be able to open one folder, understand the
problem it solves, run it locally, and see what engineering skill it
demonstrates.

## Project Folder Contract

Every major project folder should include:

- a focused `README.md` with setup, run commands, and reviewer entry points
- source code in a predictable project-specific layout
- tests or validation scripts that prove the core behavior
- examples, sample data, screenshots, notebooks, or reports when useful
- a short writeup explaining tradeoffs and what the project demonstrates
- no hidden dependency on another portfolio project unless explicitly stated

## Current Showcase

| Project | Folder | Portfolio signal | Status |
| --- | --- | --- | --- |
| Linked List Showcase | `Linked_List_Showcase` | Python packaging, typed APIs, data structures, CI, 100% coverage, examples, and educational docs | Complete showcase |

## Future Project Slots

These are good candidates for future top-level folders. They are intentionally
different from the linked-list project so the portfolio shows breadth.

| Candidate | Possible folder | What it would demonstrate |
| --- | --- | --- |
| Applied analytics dashboard | `Analytics_Dashboard_Showcase` | KPI design, source-backed charts, filtering, and business recommendations |
| Machine-learning case study | `ML_Case_Study_Showcase` | data cleaning, feature engineering, model evaluation, and honest error analysis |
| Forecasting project | `Forecasting_Showcase` | time-series splits, baselines, uncertainty, and decision-focused interpretation |
| NLP or search assistant | `NLP_Search_Showcase` | text processing, retrieval, ranking, evaluation, and user-facing workflow design |
| Model monitoring project | `Model_Monitoring_Showcase` | drift checks, alerts, dashboards, and production-minded ML operations |
| Data pipeline project | `Data_Pipeline_Showcase` | ingestion, validation, transformation, logging, and repeatable local runs |

## Root README Role

The root `README.md` should stay concise. It is the map, not the full tour.
For each completed project, add one row to the projects table and link to the
project's own README, demo script, and validation notes.

## Versioning Approach

Use lightweight tags when a project reaches a reviewer-ready milestone, for
example:

```text
linked-list-showcase-v1.0
analytics-dashboard-showcase-v1.0
```

That makes the portfolio easy to discuss in interviews because each project
has a stable checkpoint.
