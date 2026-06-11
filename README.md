# Data Science AI Portfolio

This repository currently contains a Python linked-list project with singly, doubly, singly circular, and doubly circular linked-list variants.

## Project Layout

```text
Linked Lists/
  linked_list/
    list_functions/
      access.py
      base.py
      functional.py
      iteration.py
      linked_list.py
      mutation.py
      sort_merge.py
      utility.py
    nodes/
      base_node.py
      doubly.py
      mixins.py
      singly.py
  test_linked_list.py
```

## Features

- Singly and doubly linked lists
- Singly circular and doubly circular linked lists
- Append, prepend, insert, remove, pop, and pop-front operations
- Indexing, slicing, membership checks, equality, and iteration
- Reverse, rotate, sort, merge, and sorted insertion
- Functional helpers: `map`, `filter`, and `reduce`
- Utility helpers: `to_list`, `from_list`, `copy`, `deep_copy`, `count`, and `clear`

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies

## Running Tests

From the repository root:

```bash
cd "Linked Lists"
python -m unittest -v test_linked_list.py
```

The GitHub Actions workflow runs the same unittest suite on pushes and pull requests targeting `master`.

## Example

```python
from linked_list.list_functions.linked_list import LinkedList

linked_list = LinkedList("doubly_circular")
for value in [3, 1, 2]:
    linked_list.append(value)

linked_list.sort()
linked_list.insert_sorted(4)

print(linked_list.to_list())  # [1, 2, 3, 4]
```
