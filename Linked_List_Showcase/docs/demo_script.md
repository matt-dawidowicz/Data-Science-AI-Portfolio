# Reviewer Demo Script

This script gives a reviewer a 3-5 minute path through Linked Structure Lab.
It is designed for someone who wants proof that the project runs, but does not
have time to inspect every linked-list variant in detail.

## 1. Start From The Package Folder

From the repository root:

```powershell
cd Linked_List_Showcase
python -m pip install -e ".[dev]"
```

If you are using PyCharm, select the same Python 3.12+ interpreter that ran
the install command. If imports still fail, mark `Linked_List_Showcase/src` as
a Sources Root.

## 2. Run The Core Checks

```powershell
python -m pytest -q
python -m coverage run -m pytest
python -m coverage report
```

Expected signal:

- the test suite passes
- coverage reports 100% for `src/linked_list`
- tests cover both public behavior and internal pointer invariants

## 3. Run The Product Ops Demo

```powershell
python examples/product_ops_demo.py
```

This scenario uses several structures together in one realistic mini system:

- `LinkedDeque` for urgent and normal work intake
- `SkipList` for ordered escalation deadlines
- `SelfOrganizingLinkedList` for a command palette that adapts to repeated use
- `MultilevelLinkedList` for a nested incident-response playbook
- `SparseMatrixLinkedList` for sparse service-by-region incident impact
- `UnrolledLinkedList` for chunked event-log storage

The point is not that this package should replace production queues,
databases, or monitoring tools. The point is that the structures are usable,
composable, and easy to explain in product/system terms.

## 4. Inspect One Source-Test Pair

Pick one pair based on what you want to review:

| Topic | Source | Tests |
| --- | --- | --- |
| Core pointer repair | `src/linked_list/list_functions/mutation.py` | `tests/test_linked_list.py` |
| Double-ended queue | `src/linked_list/deque.py` | `tests/test_linked_deque.py` |
| Ordered probabilistic search | `src/linked_list/skip_list.py` | `tests/test_skip_list.py` |
| Sparse row and column chains | `src/linked_list/sparse_matrix.py` | `tests/test_sparse_matrix_linked_list.py` |
| Block-based linked storage | `src/linked_list/unrolled_list.py` | `tests/test_unrolled_linked_list.py` |

## 5. Interview Talking Points

- The package uses a `src/` layout, typed public APIs, and a PEP 561 marker.
- The project is educational and portfolio-oriented, so clarity beats raw
  speed.
- Tests check internal link integrity, not only returned lists of values.
- The examples connect abstract data structures to real product and systems
  workflows.
- The benchmark output is framed honestly against Python's optimized
  built-ins.
