# Package Readiness

This checklist explains how to work with the package as an installable
educational library.

## Install Locally

From this package directory:

```powershell
python -m pip install -e .
```

For development tools and optional property-based tests:

```powershell
python -m pip install -e ".[dev]"
```

If you opened the full portfolio repository in PyCharm, the package will not
be importable until the nested project is installed or its `src` folder is
marked as a source root. The importable package name is `linked_list`; the
installable distribution name is `linked-structure-lab`.

Recommended PyCharm setup:

```powershell
cd Linked_List_Showcase
python -m pip install -e ".[dev]"
```

Then select the same Python 3.12+ interpreter in PyCharm. As an alternative,
mark `Linked_List_Showcase/src` as `Sources Root`.

## Run Quality Gates

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest
python -m coverage run -m pytest
python -m coverage report
```

## Run Examples

Each file in `examples/` is standalone:

```powershell
python examples/job_queue.py
python examples/leaderboard.py
python examples/sparse_recommender.py
```

## Run Benchmarks

Benchmarks are intentionally lightweight and use the standard library only:

```powershell
python benchmarks/benchmark_structures.py
```

The benchmark output is a teaching aid, not a formal performance claim. It
helps readers compare the educational linked implementations with Python's
optimized built-in containers.

For the current benchmark snapshot and interpretation, see
`benchmark_results.md`.

## Portfolio Review

For a reviewer-facing overview of what the project demonstrates, see
`portfolio_showcase.md`.
