# Examples

These scripts show where the linked structures appear in real product and
systems work. They are intentionally small enough to read in one sitting.

Run any example from the repository root:

```powershell
python examples/job_queue.py
python examples/leaderboard.py
python examples/sparse_recommender.py
```

| Example | Structure | Real-world pattern |
| --- | --- | --- |
| `round_robin_scheduler.py` | Circular `LinkedList` | Worker rotation and turn scheduling |
| `job_queue.py` | `LinkedDeque` | Producer-consumer queues and retry buffers |
| `leaderboard.py` | `SkipList` | Ordered rankings and nearest-score lookup |
| `document_outline.py` | `MultilevelLinkedList` | Nested outlines, menus, and file trees |
| `text_cursor.py` | `PositionalLinkedList` | Editing around a stable cursor |
| `lru_cache.py` | `PositionalLinkedList` | Recency tracking for cache eviction |
| `adaptive_command_palette.py` | `SelfOrganizingLinkedList` | Frequently used commands moving forward |
| `text_buffer_blocks.py` | `UnrolledLinkedList` | Chunked text buffers |
| `sparse_recommender.py` | `SparseMatrixLinkedList` | Mostly-empty ratings matrices |
