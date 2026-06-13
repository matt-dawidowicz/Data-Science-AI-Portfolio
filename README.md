# Data Science AI Portfolio

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)

This repository is organized as a portfolio workspace. Each substantial
project lives in its own folder so the repository can grow into a showcase of
data structures, data science, machine learning, analytics, and AI projects
without turning the root directory into one large mixed codebase.

## Projects

| Project | Location | Type | Status |
| --- | --- | --- | --- |
| Linked Structure Lab | `linked-structure-lab` | Installable Python package | Active |

## Linked Structure Lab

`Linked Structure Lab` is an educational Python package for linked data
structures. It includes singly, doubly, circular, sorted, skip-list,
deque-backed, unrolled, multilevel, positional, self-organizing, and sparse
matrix linked structures, with extensive tests, documentation, examples, and
benchmarks.

Work with it from its package folder:

```bash
cd linked-structure-lab
python -m pip install -e ".[dev]"
python -m pytest
python -m unittest discover -s tests -t . -v
```

The package documentation, examples, benchmarks, changelog, and packaging
metadata are all inside `linked-structure-lab`.

## Repository Layout

```text
.github/
  workflows/
    ci.yml
    tests.yml
linked-structure-lab/
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

## Adding More Portfolio Projects

Add future projects as separate top-level folders, for example:

```text
dashboard-project/
customer-segmentation/
forecasting-case-study/
another-python-package/
```

Keep each project self-contained with its own README, dependencies,
instructions, tests, and artifacts. The root README should stay a concise map
of the portfolio rather than becoming the full documentation for every
project.
