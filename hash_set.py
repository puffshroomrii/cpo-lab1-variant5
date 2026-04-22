"""
Mutable set based on hash map with open addressing.
Supports None as a valid element.
"""


class HashSet:
    _EMPTY = object()  # 标记空槽
    _TOMBSTONE = object()  # 标记已删除（探测链不断）

    def __init__(self, growth_factor: float = 2.0, initial_capacity: int = 8):
        if growth_factor <= 1.0:
            raise ValueError("growth_factor must be > 1.0")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be >= 1")
        self._growth_factor = growth_factor
        self._capacity = initial_capacity
        self._table = [self._EMPTY] * self._capacity
        self._size = 0

    def _hash(self, value):
        return hash(value) % self._capacity

    def _find_index(self, value):
        """
        Find the index of value in the table.
        Returns (index, found) where found is True if exists.
        """
        h = self._hash(value)
        first_tombstone = -1
        for i in range(self._capacity):
            idx = (h + i) % self._capacity
            slot = self._table[idx]
            if slot is self._EMPTY:
                # 如果找到空槽，停止探测
                idx = first_tombstone if first_tombstone != -1 else -1
                return idx, False
            if slot is self._TOMBSTONE:
                if first_tombstone == -1:
                    first_tombstone = idx
                continue
            if slot == value:
                return idx, True
        # 表满了（理论上不会，因为会扩容）
        return (first_tombstone if first_tombstone != -1 else -1), False

    def _resize(self):
        old_table = self._table
        old_capacity = self._capacity
        self._capacity = int(self._capacity * self._growth_factor)
        self._table = [self._EMPTY] * self._capacity
        self._size = 0

        for slot in old_table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                self.add(slot)

    def add(self, value):
        """Add an element to the set."""
        if self._size / self._capacity > 0.7:
            self._resize()

        idx, found = self._find_index(value)
        if found:
            return
        self._table[idx] = value
        self._size += 1

    def remove(self, value):
        """Remove an element from the set. Raise KeyError if not found."""
        idx, found = self._find_index(value)
        if not found:
            raise KeyError(value)
        self._table[idx] = self._TOMBSTONE
        self._size -= 1

    def member(self, value) -> bool:
        """Check if value is in the set."""
        _, found = self._find_index(value)
        return found

    def size(self) -> int:
        return self._size

    def from_list(self, lst):
        """Replace current set with elements from a Python list."""
        self.clear()
        for v in lst:
            self.add(v)

    def to_list(self):
        """Return a Python list of all elements (order not guaranteed)."""
        result = []
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                result.append(slot)
        return result

    def clear(self):
        """Remove all elements."""
        self._table = [self._EMPTY] * self._capacity
        self._size = 0

    def filter(self, predicate):
        """Remove elements that do NOT satisfy predicate."""
        for i in range(self._capacity):
            slot = self._table[i]
            if (
                slot is not self._EMPTY
                and slot is not self._TOMBSTONE
                and not predicate(slot)
            ):
                self._table[i] = self._TOMBSTONE
                self._size -= 1

    def map(self, func):
        """
        Replace each element with func(element).
        After mapping, ensure no duplicates (set property).
        """
        # 收集所有映射后的值，去重后再放回
        new_values = set()
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                new_values.add(func(slot))
        # 清空并重新添加
        self.clear()
        for v in new_values:
            self.add(v)

    def reduce(self, func, initial_state):
        """Apply func cumulatively to all elements."""
        state = initial_state
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                state = func(state, slot)
        return state

    def __iter__(self):
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                yield slot

    @staticmethod
    def empty():
        """Monoid identity."""
        return HashSet()

    def concat(self, other):
        """Monoid concat: add all elements from other to self."""
        for v in other:
            self.add(v)

    def __contains__(self, value):
        return self.member(value)

    def __len__(self):
        return self.size()
