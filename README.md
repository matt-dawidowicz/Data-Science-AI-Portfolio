# Data Science AI Portfolio

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Coverage 100%](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](Linked_List_Showcase/README.md#testing-strategy)

This repository is organized as a portfolio workspace. Each major top-level
folder is intended to stand on its own as a project with its own README,
dependencies, examples, tests, and technical writeup.

The first completed project is a Python data-structures showcase. It is not
trying to replace Python's standard library. It is built to demonstrate
implementation skill, type-aware package design, regression testing,
documentation, CI discipline, and the ability to explain tradeoffs clearly.

## Projects

| Project | Location | What it demonstrates | Status |
| --- | --- | --- | --- |
| Linked List Showcase | [`Linked_List_Showcase`](Linked_List_Showcase) | Python package design, linked data structures, typed APIs, 100% coverage, CI, examples, benchmarks, and educational documentation | Complete showcase |

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

Best entry points:

- [Project README](Linked_List_Showcase/README.md): install, examples, API
  overview, edge cases, and testing strategy.
- [Portfolio Showcase](Linked_List_Showcase/docs/portfolio_showcase.md):
  reviewer-facing summary of what the project proves.
- [Benchmark Results](Linked_List_Showcase/docs/benchmark_results.md):
  measured output and interpretation for the educational structures.
- [Source Walkthrough](Linked_List_Showcase/docs/linked_structures_walkthrough.md):
  beginner-friendly explanation of invariants and pointer repair.

## Repository Layout

```text
.github/
  workflows/
    ci.yml
    tests.yml
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
specific project.
