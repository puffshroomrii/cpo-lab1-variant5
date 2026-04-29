from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Generic, TypeVar, cast
T = TypeVar("T")
R = TypeVar("R")


class HashSet(Generic[T]):
    """Mutable hash set based on open addressing."""

    _EMPTY = object()
    _TOMBSTONE = object()
    _MAX_LOAD_FACTOR = 0.7

    def __init__(self, growth_factor: float = 2.0,
                 initial_capacity: int = 8) -> None:
        if growth_factor <= 1.0:
            raise ValueError("growth_factor must be greater than 1.0")
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be at least 1")

        self._growth_factor: float = growth_factor
        self._capacity: int = initial_capacity
        self._table: list[object] = [self._EMPTY] * self._capacity
        self._size: int = 0

    def _hash(self, value: T) -> int:
        return hash(value) % self._capacity

    def _find_index(self, value: T) -> tuple[int, bool]:
        start_index = self._hash(value)
        first_tombstone = -1

        for offset in range(self._capacity):
            index = (start_index + offset) % self._capacity
            slot = self._table[index]

            if slot is self._EMPTY:
                insert_index = (
                    first_tombstone
                    if first_tombstone != -1
                    else index
                )
                return insert_index, False

            if slot is self._TOMBSTONE:
                if first_tombstone == -1:
                    first_tombstone = index
                continue

            if slot == value:
                return index, True

        return first_tombstone, False

    def _resize(self) -> None:
        old_values = self.to_list()
        new_capacity = max(self._capacity + 1,
                           int(self._capacity * self._growth_factor))

        self._capacity = new_capacity
        self._table = [self._EMPTY] * self._capacity
        self._size = 0

        for value in old_values:
            self.add(value)

    def add(self, value: T) -> None:
        if (self._size + 1) > self._capacity * self._MAX_LOAD_FACTOR:
            self._resize()

        index, found = self._find_index(value)
        if found:
            return

        if index == -1:
            self._resize()
            index, found = self._find_index(value)
            if found:
                return

        self._table[index] = value
        self._size += 1

    def remove(self, value: T) -> None:
        index, found = self._find_index(value)
        if not found:
            raise KeyError(value)

        self._table[index] = self._TOMBSTONE
        self._size -= 1

    def member(self, value: T) -> bool:
        _, found = self._find_index(value)
        return found

    def size(self) -> int:
        return self._size

    def from_list(self, values: Iterable[T]) -> None:
        self.clear()
        for value in values:
            self.add(value)

    def to_list(self) -> list[T]:
        result: list[T] = []
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                result.append(cast(T, slot))
        return result

    def clear(self) -> None:
        self._table = [self._EMPTY] * self._capacity
        self._size = 0

    def filter(self, predicate: Callable[[T], bool]) -> None:
        for index, slot in enumerate(self._table):
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                value = cast(T, slot)
                if not predicate(value):
                    self._table[index] = self._TOMBSTONE
                    self._size -= 1

    def map(self, function: Callable[[T], T]) -> None:
        new_values = [function(value) for value in self]
        self.clear()
        for value in new_values:
            self.add(value)

    def reduce(self, function: Callable[[R, T], R], initial_state: R) -> R:
        state = initial_state
        for value in self:
            state = function(state, value)
        return state

    def concat(self, other: "HashSet[T]") -> None:
        for value in other:
            self.add(value)

    @staticmethod
    def empty() -> "HashSet[T]":
        return HashSet()

    def __iter__(self) -> Iterator[T]:
        for slot in self._table:
            if slot is not self._EMPTY and slot is not self._TOMBSTONE:
                yield cast(T, slot)

    def __contains__(self, value: object) -> bool:
        try:
            return self.member(cast(T, value))
        except TypeError:
            return False

    def __len__(self) -> int:
        return self.size()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashSet):
            return False
        return set(self.to_list()) == set(other.to_list())
