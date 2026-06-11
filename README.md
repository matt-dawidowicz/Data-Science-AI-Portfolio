# Data Science AI Portfolio

This repository currently contains a Python linked-list project with singly, doubly, singly circular, and doubly circular linked-list variants, plus a linked deque implementation.

## Project Layout

```text
Linked Lists/
  linked_list/
    __init__.py
    deque.py
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
  test_linked_deque.py
  test_linked_list.py
```

## Features

- Singly and doubly linked lists
- Singly circular and doubly circular linked lists
- Linked deque backed by a doubly linked list
- Append, prepend, insert, remove, pop, and pop-front operations
- Deque operations: `append_left`, `append_right`, `pop_left`, `pop_right`, `peek_left`, `peek_right`, `extend`, `extend_left`, and `rotate`
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
python -m unittest discover -v
```

The GitHub Actions workflow runs the same unittest suite on pushes and pull requests targeting `master`.

## Example

```python
from linked_list import LinkedDeque, LinkedList

linked_list = LinkedList("doubly_circular")
for value in [3, 1, 2]:
    linked_list.append(value)

linked_list.sort()
linked_list.insert_sorted(4)

print(linked_list.to_list())  # [1, 2, 3, 4]

linked_deque = LinkedDeque([2, 3])
linked_deque.append_left(1)
linked_deque.append_right(4)
linked_deque.rotate(1)

print(linked_deque.to_list())  # [4, 1, 2, 3]
```
