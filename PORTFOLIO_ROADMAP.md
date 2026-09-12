# Portfolio Roadmap

This repository is organized as a portfolio workspace. Each major top-level
folder should be reviewable on its own, with setup instructions, validation,
artifacts, and a concise explanation of what the project demonstrates.

The portfolio should prioritize evidence of technical judgment over raw code
volume. In an AI-assisted development environment, the strongest projects make
problem framing, baselines, experiments, validation, benchmarks, failure modes,
and tradeoffs inspectable.

## Current Portfolio Priority

1. Applied data science and forecasting work.
2. A production-oriented applied-AI / retrieval project with explicit evaluation.
3. Software-engineering evidence centered on correctness, testing, and systems thinking.
4. Engineering-fundamentals material as supporting evidence rather than the lead story.

## Project Folder Contract

Every major project folder should include:

- a focused `README.md` with setup, run commands, and reviewer entry points;
- source code in a predictable project-specific layout;
- tests or validation scripts that establish the core claims;
- examples, sample data, screenshots, notebooks, reports, or benchmark output when useful;
- a short writeup explaining architecture/model choices, tradeoffs, and limitations;
- explicit baselines or comparison points when the project makes performance or quality claims;
- enough reproducibility that a reviewer can verify important results;
- no hidden dependency on another portfolio project unless explicitly stated.

## Current Showcase

| Project | Folder | Portfolio role | Status |
| --- | --- | --- | --- |
| Citi Bike Demand Forecasting | `Citi Bike Time Series` | Primary applied-data-science case study: public-data ingestion, time-series modeling, rolling validation, station segmentation, exogenous features, and operational decision framing | Complete showcase; strong lead project |
| Linked Structure Lab | `Linked_List_Showcase` | Supporting engineering-fundamentals lab: invariants, property-based testing, reference-model comparison, typing, CI, benchmarks, and verification of AI-assisted code | Complete; feature expansion intentionally stopped |

## Highest-Value Next Project

The next major addition should directly substantiate current applied-AI skills
rather than add another generic application.

### Retrieval / RAG Evaluation System

Recommended evidence:

- reproducible document ingestion and corpus construction;
- multiple chunking strategies with measured comparison;
- embedding-model comparison, such as BGE and E5;
- vector indexing with FAISS or HNSW;
- retrieval metrics such as Recall@K, MRR, or nDCG;
- reranking experiments and measured lift;
- end-to-end answer evaluation with a clearly defined test set;
- latency and cost measurements;
- failure taxonomy and examples of queries that remain difficult;
- regression tests for previously discovered failures;
- Docker or similarly reproducible execution;
- a short architecture-decision log documenting experiments that were rejected.

The goal should not be "build a chatbot." The goal should be to demonstrate
ownership of retrieval quality, evaluation, performance, and failure analysis.

## Secondary Future Project Slots

| Candidate | Possible folder | What it should demonstrate |
| --- | --- | --- |
| Model monitoring system | `Model_Monitoring_Showcase` | drift checks, alert thresholds, evaluation windows, false-positive tradeoffs, and operational response |
| Data pipeline / data-quality system | `Data_Pipeline_Showcase` | ingestion, schema validation, idempotency, logging, retries, reproducibility, and failure recovery |
| Applied ML case study | `ML_Case_Study_Showcase` | feature engineering, baselines, error analysis, calibration, and honest model comparison |
| Systems/performance case study | `Performance_Engineering_Showcase` | baseline benchmarks, profiling, bottleneck identification, optimization, and correctness-preserving regression checks |

## AI-Assisted Development Policy

Using AI coding tools is allowed and expected. Portfolio projects should not
imply that code volume alone proves engineering ability.

When AI materially assists implementation, the project should make the owner's
technical responsibility visible through some combination of:

- explicit requirements and constraints;
- architecture decisions;
- tests tied to meaningful invariants;
- benchmarks before and after changes;
- documented failed experiments;
- bug reproductions and regression tests;
- manual review of generated changes;
- reproducible evaluation artifacts;
- clear explanation of why the final approach was accepted.

The standard is technical ownership, not manual keystroke count.

## Root README Role

The root `README.md` is the portfolio landing page, not a catalog of every file.
It should lead with the strongest current applied project, give each completed
project a clear role, and provide a fast reviewer path.

Engineering-fundamentals projects should remain available but should not crowd
out work that directly supports current target roles.

## Versioning Approach

Use lightweight tags when a project reaches a stable reviewer-ready milestone,
for example:

```text
linked-list-showcase-v1.0
citibike-forecasting-v1.0
rag-evaluation-showcase-v1.0
```

Stable checkpoints make projects easier to discuss in interviews and prevent
later experiments from obscuring the version originally reviewed.
