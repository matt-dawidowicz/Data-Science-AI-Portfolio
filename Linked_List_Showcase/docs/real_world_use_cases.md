# Real-World Use Cases

This package is educational, so the examples are intentionally small. The
structures still map to real product and systems problems that engineers see
in everyday software.

## LinkedList

Use a linked list when the lesson or product model is about local insertion,
local deletion, and explicit node traversal.

Real situations:

- A media playlist editor where the current track can move to the next or
  previous track and circular playback matters.
- A browser-style history model where navigation is naturally expressed as a
  chain of pages.
- A round-robin scheduler that cycles through active workers or accounts.
- A tutorial or interview-prep tool that needs to show exactly how pointer
  repair works after inserting or removing a node.

In production Python, a plain `list` is usually better unless node identity or
teaching pointer behavior is the point.

## LinkedDeque

Use a linked deque for systems that repeatedly add and remove work at both
ends.

Real situations:

- A job runner where urgent tasks can be pushed to the front and normal tasks
  go to the back.
- A breadth-first search frontier in a crawler, dependency explorer, or graph
  tool.
- A sliding-window processor that expires old events from the left while new
  telemetry arrives on the right.
- A retry queue where failed items can be moved to one end without shifting a
  whole array.

In production Python, `collections.deque` is the practical choice. This class
exists to show how a deque works internally.

## SortedLinkedList

Use a sorted linked list when a small collection must remain ordered after
every insertion.

Real situations:

- A small ranked waitlist in a booking or support workflow.
- A simple timer queue in a teaching scheduler where the next deadline stays
  near the front.
- A live "top few" view for a demo leaderboard where correctness and
  readability matter more than large-scale performance.

For large or performance-critical ordered data, use `heapq`, `bisect` with a
list, a database index, or a specialized sorted container.

## SkipList

Use a skip list when the product needs ordered membership, fast expected
search, and range-style access without a tree implementation.

Real situations:

- A leaderboard service that needs to keep player scores ordered and support
  quick membership checks.
- A sorted in-memory index for event timestamps, feature IDs, or document IDs.
- A range-lookup teaching demo where probabilistic shortcuts are easier to
  inspect than a balanced tree.
- A storage-engine lesson that compares tree indexes with probabilistic linked
  levels.

For production systems, prefer the database, cache, or indexing library that
already owns ordering, persistence, and concurrency.

## UnrolledLinkedList

Use an unrolled linked list when nearby values should be stored together, but
the structure should still be linked by chunks.

Real situations:

- A text editor buffer that edits chunks of text rather than one character per
  node.
- A log viewer that pages through batches of events while still allowing
  chunk-level insertion and deletion.
- A packet or message batcher where each node represents a small fixed-size
  block.
- A visualization of why cache locality can matter even inside linked
  structures.

For production text editing, use a rope, gap buffer, piece table, or the data
structure provided by the editor framework.

## MultilevelLinkedList

Use a multilevel linked list when each item can own a child chain and the
product needs flattening or nested traversal.

Real situations:

- A file explorer where folders contain child entries but still appear in a
  sibling order.
- A nested comment thread where each comment may have replies.
- A document outline where sections contain subsections and the app can
  flatten the outline for export.
- A menu builder where top-level menu items may contain child menu items.

For general-purpose hierarchical data, a tree model is usually clearer. This
structure is useful when the linked representation itself is the lesson.

## PositionalLinkedList

Use a positional list when callers need stable handles to items they already
found.

Real situations:

- A text editor cursor or selection handle that should remain tied to a node
  even after nearby inserts.
- A kanban board where the UI holds a card handle and moves that exact card
  before or after another card.
- A playlist editor where drag-and-drop code gets a position object instead of
  repeatedly searching for an index.
- A simulation where entities move within an ordered chain and external code
  keeps references to them.

In production apps, object IDs and database rows often play this role. The
positional list is a compact in-memory version for learning and demos.

## SelfOrganizingLinkedList

Use a self-organizing list when the access pattern is skewed and the structure
should adapt after successful searches.

Real situations:

- A command palette that moves frequently used commands toward the top.
- A help menu or settings panel where recently or frequently chosen items
  become easier to find.
- A contact picker that favors people a user repeatedly selects.
- A teaching tool that compares move-to-front, transpose, and frequency-count
  heuristics.

Modern products often use ranking models or analytics-backed personalization.
This list is a transparent, local version of the same adaptive-search idea.

## SparseMatrixLinkedList

Use a sparse matrix when most cells are empty and only meaningful coordinates
should be stored.

Real situations:

- A recommender prototype where rows are users, columns are products, and most
  user-product pairs have no interaction.
- A graph adjacency matrix for a network with many possible edges but few
  actual edges.
- A machine-learning feature matrix where most features are zero for most
  examples.
- A search index lesson where documents and terms form a mostly empty
  term-document matrix.

For production numerical work, use SciPy sparse matrices, NumPy, pandas, or a
database/vector system. This implementation is for understanding the linked
row and column chains behind the idea.
