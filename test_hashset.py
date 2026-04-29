from __future__ import annotations
import pytest
from hypothesis import given
from hypothesis import strategies as st

from hash_set import HashSet


@st.composite
def hash_sets(draw: st.DrawFn) -> HashSet[int]:
    values = draw(st.lists(st.integers()))
    result: HashSet[int] = HashSet()
    result.from_list(values)
    return result


def test_empty_set() -> None:
    data: HashSet[int] = HashSet()
    assert data.size() == 0
    assert data.to_list() == []


def test_add_member_and_duplicate() -> None:
    data: HashSet[int | None] = HashSet()
    data.add(1)
    data.add(1)
    data.add(None)

    assert data.size() == 2
    assert data.member(1)
    assert data.member(None)
    assert not data.member(2)


def test_remove() -> None:
    data: HashSet[int] = HashSet()
    data.from_list([10, 20])

    data.remove(10)

    assert not data.member(10)
    assert data.member(20)
    assert data.size() == 1

    with pytest.raises(KeyError):
        data.remove(999)


def test_from_list_to_list() -> None:
    data: HashSet[int | None] = HashSet()
    data.from_list([1, 2, 2, 3, None, None])

    assert set(data.to_list()) == {1, 2, 3, None}
    assert data.size() == 4


def test_filter() -> None:
    data: HashSet[int] = HashSet()
    data.from_list([1, 2, 3, 4, 5])

    data.filter(lambda value: value % 2 == 0)

    assert data == make_hash_set([2, 4])


def test_map() -> None:
    data: HashSet[int] = HashSet()
    data.from_list([1, 2, 3])

    data.map(lambda value: value * 2)

    assert data == make_hash_set([2, 4, 6])

    data.map(lambda value: 1)

    assert data == make_hash_set([1])


def test_reduce() -> None:
    data: HashSet[int] = HashSet()
    data.from_list([1, 2, 3, 4])

    assert data.reduce(lambda acc, value: acc + value, 0) == 10


def test_iterator() -> None:
    data: HashSet[int] = HashSet()
    data.from_list([10, 20, 30])

    assert set(iter(data)) == {10, 20, 30}


def test_concat() -> None:
    left: HashSet[int] = HashSet()
    right: HashSet[int] = HashSet()

    left.from_list([1, 2])
    right.from_list([2, 3])

    left.concat(right)

    assert left == make_hash_set([1, 2, 3])


def test_empty_monoid() -> None:
    data = make_hash_set([7, 8])
    empty: HashSet[int] = HashSet.empty()

    data.concat(empty)

    assert data == make_hash_set([7, 8])


def test_growth_factor() -> None:
    data: HashSet[int] = HashSet(growth_factor=2.0, initial_capacity=4)

    for value in range(100):
        data.add(value)

    assert data.size() == 100
    for value in range(100):
        assert data.member(value)


def test_eq() -> None:
    first = make_hash_set([1, 2, 3])
    second = make_hash_set([3, 2, 1])
    third = make_hash_set([1, 2])

    assert first == second
    assert first != third
    assert first != [1, 2, 3]


def make_hash_set(values: list[int]) -> HashSet[int]:
    result: HashSet[int] = HashSet()
    result.from_list(values)
    return result


@given(hash_sets())
def test_pbt_to_list_contains_all_elements(data: HashSet[int]) -> None:
    assert len(data.to_list()) == data.size()
    assert set(data.to_list()) == set(iter(data))


@given(hash_sets())
def test_pbt_add_existing_element_does_not_change_size(
        data: HashSet[int]) -> None:
    for value in data.to_list():
        old_size = data.size()
        data.add(value)
        assert data.size() == old_size


@given(hash_sets(), hash_sets(), hash_sets())
def test_pbt_concat_associativity(
    first: HashSet[int],
    second: HashSet[int],
    third: HashSet[int],
) -> None:
    left = make_hash_set(first.to_list())
    left.concat(second)
    left.concat(third)

    right = make_hash_set(first.to_list())
    second_copy = make_hash_set(second.to_list())
    second_copy.concat(third)
    right.concat(second_copy)

    assert left == right


@given(hash_sets())
def test_pbt_concat_identity(data: HashSet[int]) -> None:
    left_identity: HashSet[int] = HashSet.empty()
    left_identity.concat(data)

    right_identity = make_hash_set(data.to_list())
    right_identity.concat(HashSet.empty())

    assert left_identity == data
    assert right_identity == data


@given(hash_sets())
def test_pbt_filter_keeps_only_matching_values(data: HashSet[int]) -> None:
    data.filter(lambda value: value % 2 == 0)

    for value in data:
        assert value % 2 == 0


@given(hash_sets())
def test_pbt_map_preserves_size_for_injective_function(
        data: HashSet[int]) -> None:
    old_size = data.size()

    data.map(lambda value: value + 1)

    assert data.size() == old_size


@given(hash_sets())
def test_pbt_reduce_sum(data: HashSet[int]) -> None:
    assert data.reduce(
        lambda acc,
        value: acc +
        value,
        0) == sum(
        data.to_list())
