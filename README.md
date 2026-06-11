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
- Python-style deque aliases: `append`, `appendleft`, `pop`, `popleft`, and `extendleft`
- Indexing, slicing, membership checks, equality, and iteration
- Reverse, rotate, sort, merge, and sorted insertion
- Functional helpers: `map`, `filter`, and `reduce`
- Utility helpers: `to_list`, `from_list`, `copy`, `deep_copy`, `count`, and `clear`

## Project Explanation

This project is meant to show that I understand linked data structures from the
inside out, not just how to call a built-in list or deque. I implemented the
core linked-list behavior myself, then separated the code into focused modules
so each part of the data structure is easier to explain, test, and maintain.

At the highest level, the project has two public containers:

- `LinkedList`, which supports singly linked, doubly linked, singly circular,
  and doubly circular list variants.
- `LinkedDeque`, which is a double-ended queue built on top of doubly linked
  nodes.

The two structures are related, but they are not the same thing. A doubly
linked list is a general-purpose sequence where operations like indexing,
insertion, removal, sorting, merging, and traversal matter. A deque is focused
on efficient access at both ends. With `LinkedDeque`, the main design goal is
to make left-side and right-side operations direct and predictable:
`append_left`, `append_right`, `pop_left`, and `pop_right` all work by updating
only the head, tail, and neighboring links.

## How the LinkedList Is Organized

The `LinkedList` class is assembled from mixins in `linked_list/list_functions`.
I used this structure so each behavior group has a clear purpose:

- `base.py` stores shared list state such as `head`, `tail`, `_size`,
  `_list_type`, and `_is_circular`.
- `access.py` handles indexing, slicing, containment checks, equality,
  string conversion, and `nth_from_end`.
- `iteration.py` handles forward iteration for every list type and reverse
  iteration for doubly linked lists.
- `mutation.py` handles operations that change the list, including append,
  prepend, insert, remove, pop, rotate, reverse, merge, extend, and duplicate
  removal.
- `sort_merge.py` implements merge sort helpers for linked lists.
- `functional.py` adds `map`, `filter`, and `reduce`.
- `utility.py` adds conversion, copying, counting, and clearing helpers.

This organization makes the class easier to reason about because each file has
one main responsibility. Instead of one large class containing every operation,
the final `LinkedList` class combines smaller behavior groups into one public
type.

## Node Design

The node classes live in `linked_list/nodes`. They are the building blocks for
all list variants:

- `BaseNode` stores the data value.
- `NextMixin` adds a `next` pointer.
- `PrevMixin` adds a `prev` pointer.
- `CircularMixin` makes missing links point back to the node itself.
- `SinglyLinkedNode` has only a forward link.
- `DoublyLinkedNode` has both forward and backward links.
- `SinglyCircularLinkedNode` starts with its `next` pointer linked to itself.
- `DoublyCircularLinkedNode` starts with both `next` and `prev` linked to
  itself.

This setup avoids repeating the same pointer fields in every node class. It
also makes the differences between singly, doubly, and circular structures
visible in the code.

## Circular List Handling

Circular lists need extra care because there is no natural `None` endpoint
during traversal. To prevent infinite loops, operations that walk a circular
list either use the list size as a boundary or stop when they return to the
starting node.

When a mutation changes a circular list, the implementation restores the
head-tail connection afterward:

- For singly circular lists, `tail.next` points back to `head`.
- For doubly circular lists, `tail.next` points to `head` and `head.prev`
  points back to `tail`.

This is especially important in operations like `remove`, `pop`, `pop_front`,
`reverse`, `merge`, `sort`, `remove_duplicates`, and `clear`, because those
operations temporarily move or detach nodes.

## LinkedDeque Design

`LinkedDeque` is backed by `DoublyLinkedNode` objects. It keeps direct
references to both ends of the structure:

- `head` is the left side of the deque.
- `tail` is the right side of the deque.
- `_size` tracks the number of stored values.

That design makes end operations straightforward:

- `append_left` creates a new node before the current head.
- `append_right` creates a new node after the current tail.
- `pop_left` removes the head node and repairs the new head's `prev` link.
- `pop_right` removes the tail node and repairs the new tail's `next` link.
- `peek_left` and `peek_right` read values without mutating the deque.
- `clear` detaches every node so old node references do not keep stale links.

The deque also includes Python-style aliases:

- `append` maps to `append_right`.
- `appendleft` maps to `append_left`.
- `pop` maps to `pop_right`.
- `popleft` maps to `pop_left`.
- `extendleft` maps to `extend_left`.

These aliases make `LinkedDeque` feel familiar to anyone who has used
`collections.deque`, while still keeping the explicit left/right method names.

## Deque Edge Cases I Handled

The deque implementation intentionally handles several edge cases:

- Empty `pop` and `peek` operations raise `IndexError`.
- Popping from a one-item deque clears both `head` and `tail`.
- Appending to an empty deque sets both `head` and `tail` to the new node.
- `extend(self)` snapshots the deque before appending to avoid self-extension
  problems.
- Iterating over a deque is bounded by the size captured when iteration starts,
  which prevents `extend(iter(deque))` from walking newly appended nodes
  forever.
- `repr` and `str` handle direct and mutual self-references without infinite
  recursion.
- Equality works symmetrically between `LinkedDeque` and subclasses.
- `rotate` matches the same direction convention as `collections.deque`:
  positive values rotate right, and negative values rotate left.

These cases matter because linked structures can be easy to corrupt if a method
updates one pointer but forgets the matching pointer on the neighboring node.
Most of the deque tests check both the visible values and the internal links.

## Style and Documentation Standards

I also cleaned the Python code so it follows standard Python style more
closely, especially PEP 8 formatting and PEP 257-style documentation
conventions:

- Added module docstrings to the package, node modules, linked-list modules,
  and test modules.
- Added class and method docstrings to the implementation so each public
  behavior explains its purpose.
- Wrapped long lines to stay within a 79-character style target.
- Normalized imports and blank lines.
- Removed noisy test docstrings that repeated obvious information like
  `Args: self` or `Returns: None`.
- Replaced default comparison lambdas with `operator.lt` for clearer,
  reusable default ordering behavior.
- Preserved existing public behavior while making the code easier to read.

This cleanup is important for portfolio code because readability is part of
the implementation. The goal is not only for the data structures to work, but
also for someone reviewing the repository to understand how the design is
organized and why each piece exists.

## Testing Strategy

The test suite uses Python's built-in `unittest` module. It covers both
high-level behavior and low-level structural correctness.

For `LinkedList`, the tests cover:

- Appending, prepending, inserting, removing, popping, and popping from the
  front.
- Indexing, negative indexing, slicing, membership checks, and equality.
- Sorted insertion, merge sort, merging, reversing, rotating, and duplicate
  removal.
- Functional helpers like `map`, `filter`, and `reduce`.
- Circular-list behavior, including head-tail links and doubly circular
  `prev` links.
- Empty-list and out-of-bounds error handling.
- Copy independence and clearing behavior.

For `LinkedDeque`, the tests cover:

- Empty, singleton, and multi-node states.
- Appending and popping from both ends.
- Peeking without mutation.
- Forward and reverse iteration.
- Python-style deque aliases.
- Copy behavior and subclass-preserving constructors.
- Self-extension and iterator-bounded extension.
- Self-referential and mutually referential string representations.
- Rotating right, rotating left, large rotations, and no-op rotations.
- Internal link integrity after repeated alternating operations.

The tests do more than check final lists of values. For the linked deque, they
also walk the nodes forward and backward to verify that `next` and `prev`
connections are correct. That is important because a linked structure can look
correct from one direction while still having broken backward links.

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
