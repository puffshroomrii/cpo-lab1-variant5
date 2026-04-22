# GROUP-5 - lab 1 - variant 5

This is a mutable set implementation based on a hash table with
**open addressing** (linear probing).  
It supports `None` as a valid element and uses tombstone markers for deletion.  
The set can grow dynamically with a user‑specified growth factor.

## Project structure

- `hash_set.py` -- HashSet implementation.
- `test_hashset.py` -- Unit tests + property‑based tests.

## Features

- Add, remove, membership test, size
- Convert to/from Python list
- In‑place filter and map
- Reduce (fold) over elements
- Iterator support
- Monoid: `empty()` and `concat()`
- Handles `None` correctly
- Configurable growth factor (default 2.0)
- Automatic resize when load factor > 0.7

## Contribution

- Aleksandr Penskoi (EMAIL) -- all work.
- Luo Mengyao – Core implementation: `HashSet` class, open addressing logic,
  tombstone handling, resize policy, `add`, `remove`, `member`, `size`,
  `from_list`, `to_list`, `filter`, `map`, `reduce`, `concat`, `empty`,
  iterator.
- Du Huilin – Testing and documentation: unit tests, property‑based tests
  (Hypothesis), test coverage, `README.md` (project description, design notes,
  changelog), and GitHub Actions configuration.

## Changelog

- 08.04.2026 - 1
   - Update README. Add formal sections.
- 08.04.2026 - 0
   - Initial

## Design notes

- Sentinel objects: `_EMPTY` and `_TOMBSTONE` are used to distinguish free
  slots, deleted slots, and actual `None` values. Using `None` as empty would
  conflict with storing `None` as a valid element.
- Open addressing with linear probing: Simple to implement and cache-friendly.
  Deletion marks a slot as `_TOMBSTONE` to keep probe chains intact for future
  lookups.
- Resize policy: When load factor exceeds 0.7, the table size is multiplied by
  `growth_factor` (default 2.0). This balances memory usage and performance.
- Map implementation: Directly modifying slots in-place could create duplicate
  values, breaking the set property. The implementation collects all mapped
  values into a Python set (deduplication), clears the table, then re-adds
  them.
