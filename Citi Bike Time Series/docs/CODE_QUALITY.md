# Code Quality

This project is written as a portfolio artifact, so the code needs to be
auditable as well as correct. The source files are structured as reproducible
scripts with small helper functions, explicit inputs and outputs, and
reviewer-friendly docstrings.

## Standards

The source code follows two visible standards:

- PEP8 style through Ruff formatting and lint checks.
- PEP257 docstring conventions through `pydocstyle`.
- A 100% unit coverage gate for the configured deterministic source layer
  through `coverage` and `pytest`.

Docstrings are intentionally concise. Most functions use one-line imperative
docstrings because the code already carries the implementation detail, while
the HTML reports and Markdown docs carry the business narrative.

## Source Files Covered

The quality pass covers every Python source file in `src/`:

- `citibike_time_series_profile.py`
- `citibike_decision_report.py`
- `citibike_time_series_showcase.py`
- `citibike_multi_month_proof.py`
- `citibike_station_cluster_forecast.py`

Each public module, class, and function now has a PEP257-compatible docstring.
Internal comments are kept only where they explain leakage prevention,
forecasting assumptions, or non-obvious chart/report behavior.

## Test Coverage Scope

The test suite focuses on deterministic portfolio logic: calendar features,
lag features, forecast scoring, rolling validation behavior, station ID
normalization, station clustering, weather/event feature joins, model-lift
calculation, capacity-priority ranking, table helpers, formatting helpers, and
JSON-safe conversions.

The `.coveragerc` gate is not a full end-to-end package coverage claim. It
excludes code that is intentionally integration-heavy: raw ZIP streaming,
network downloads, command-line entrypoints, chart rendering, full report
rendering, and filesystem write orchestration. Those paths are validated by
the reproducible run commands and manual report checks in
`docs/PUBLISHING_CHECKLIST.md`.

## Reproducible Checks

Run these commands from the `Citi Bike Time Series/` folder:

```bash
python -m ruff format src
python -m ruff check src
python -m pydocstyle src
python -m coverage run -m pytest
python -m coverage report
python -m py_compile \
  src/citibike_time_series_profile.py \
  src/citibike_decision_report.py \
  src/citibike_time_series_showcase.py \
  src/citibike_multi_month_proof.py \
  src/citibike_station_cluster_forecast.py
```

Current status after the polish pass:

- `ruff check src`: passing.
- `pydocstyle src`: passing.
- `coverage report`: 100% on the configured deterministic unit-test layer.
- `py_compile` for all five scripts: passing.

## Review Notes

The scripts are designed to run from a clean checkout after installing
`requirements.txt`. Raw Citi Bike archives and weather caches are downloaded
or read from `work/`, which is ignored by Git. Generated artifacts are written
under `outputs/` so reviewers can inspect both the code path and the rendered
portfolio reports.

The station-cluster script is the most complete current layer. It demonstrates
full-year processing, station ID grouping, weather/event feature engineering,
rolling validation, baseline comparison, and decision framing for rebalancing
or capacity planning.
