"""
Unit tests and property-based tests for HashSet (open addressing).
"""

import pytest
from hypothesis import given, strategies as st
from hash_set import HashSet


# ========== 1. 单元测试 (Unit Tests) ==========


def test_empty_set():
    s = HashSet()
    assert s.size() == 0
    assert s.to_list() == []
    assert not s.member(1)
    assert not s.member(None)


def test_add_and_member():
    s = HashSet()
    s.add(1)
    s.add(None)
    s.add("hello")
    assert s.size() == 3
    assert s.member(1)
    assert s.member(None)
    assert s.member("hello")
    assert not s.member(2)


def test_add_duplicate():
    s = HashSet()
    s.add(1)
    s.add(1)  # duplicate
    assert s.size() == 1
    assert s.member(1)


def test_remove():
    s = HashSet()
    s.add(10)
    s.add(20)
    s.remove(10)
    assert not s.member(10)
    assert s.member(20)
    assert s.size() == 1

    with pytest.raises(KeyError):
        s.remove(999)


def test_remove_none():
    s = HashSet()
    s.add(None)
    s.remove(None)
    assert not s.member(None)
    assert s.size() == 0


def test_from_list():
    s = HashSet()
    lst = [1, 2, 2, 3, None, None]
    s.from_list(lst)
    # 重复元素只会保留一个，None 也只有一个
    assert sorted(s.to_list(), key=lambda x: (x is None, x)) == [1, 2, 3, None]
    assert s.size() == 4


def test_to_list():
    s = HashSet()
    s.add(5)
    s.add(3)
    s.add(3)  # duplicate ignored
    lst = s.to_list()
    assert set(lst) == {5, 3}
    assert len(lst) == 2


def test_filter():
    s = HashSet()
    s.from_list([1, 2, 3, 4, 5])
    s.filter(lambda x: x % 2 == 0)  # keep evens
    assert set(s.to_list()) == {2, 4}
    assert s.size() == 2


def test_map():
    s = HashSet()
    s.from_list([1, 2, 3])
    s.map(lambda x: x * 2)
    assert set(s.to_list()) == {2, 4, 6}
    # 如果映射后产生重复，set 会去重
    s.map(lambda x: 1)
    assert s.to_list() == [1]
    assert s.size() == 1


def test_reduce():
    s = HashSet()
    s.from_list([1, 2, 3, 4])
    total = s.reduce(lambda acc, val: acc + val, 0)
    assert total == 10

    # 空集 reduce
    empty = HashSet()
    assert empty.reduce(lambda acc, val: acc + val, 100) == 100


def test_iter():
    s = HashSet()
    s.from_list([10, 20, 30])
    collected = [x for x in s]
    assert set(collected) == {10, 20, 30}
    assert len(collected) == 3


def test_concat():
    s1 = HashSet()
    s1.from_list([1, 2])
    s2 = HashSet()
    s2.from_list([2, 3, None])
    s1.concat(s2)
    assert set(s1.to_list()) == {1, 2, 3, None}
    assert s1.size() == 4


def test_empty_monoid():
    empty = HashSet.empty()
    assert empty.size() == 0
    assert empty.to_list() == []

    s = HashSet()
    s.from_list([7, 8])
    s.concat(empty)
    assert set(s.to_list()) == {7, 8}

    empty.concat(s)
    assert set(empty.to_list()) == {7, 8}  # empty 被修改了，注意 concat 是原地修改


def test_growth_factor():
    # 测试扩容机制（growth factor=2）
    s = HashSet(growth_factor=2.0, initial_capacity=4)
    for i in range(20):
        s.add(i)
    assert s.size() == 20
    # 检查没有丢失元素
    for i in range(20):
        assert s.member(i)


# ========== 2. 属性测试 (Property-Based Tests) ==========


@given(st.lists(st.integers()))
def test_from_list_to_list_roundtrip(lst):
    """from_list + to_list 应该保持元素集合不变（顺序无关）"""
    s = HashSet()
    s.from_list(lst)
    result = s.to_list()
    assert set(result) == set(lst)
    assert len(result) == len(set(lst))  # 去重后的大小


@given(st.lists(st.integers()))
def test_add_all_and_member(lst):
    """添加所有元素后，每个元素都应该 member 为 True"""
    s = HashSet()
    for v in lst:
        s.add(v)
    for v in set(lst):
        assert s.member(v)


@given(st.lists(st.integers()))
def test_remove_all(lst):
    """添加再删除所有元素，set 应该为空"""
    s = HashSet()
    s.from_list(lst)
    for v in set(lst):
        s.remove(v)
    assert s.size() == 0
    assert s.to_list() == []


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_monoid_concat_associative(a, b):
    """concat 的结合律： (s1+s2)+s3 == s1+(s2+s3)"""
    s1 = HashSet()
    s1.from_list(a)
    s2 = HashSet()
    s2.from_list(b)
    s3 = HashSet()
    s3.from_list(a)  # 任意第三个集合，这里简单重复 a

    # (s1+s2)+s3
    left = HashSet()
    left.from_list(a)
    left.concat(s2)
    left.concat(s3)

    # s1+(s2+s3)
    right = HashSet()
    right.from_list(a)
    s2_copy = HashSet()
    s2_copy.from_list(b)
    s2_copy.concat(s3)
    right.concat(s2_copy)

    assert set(left.to_list()) == set(right.to_list())


@given(st.lists(st.integers()))
def test_monoid_identity(lst):
    """empty 是 concat 的单位元"""
    s = HashSet()
    s.from_list(lst)
    empty = HashSet.empty()

    # s + empty == s
    s_copy = HashSet()
    s_copy.from_list(lst)
    s_copy.concat(empty)
    assert set(s_copy.to_list()) == set(lst)

    # empty + s == s
    empty.concat(s)
    assert set(empty.to_list()) == set(lst)


@given(st.lists(st.integers()), st.lists(st.integers()))
def test_filter_property(a, b):
    """filter 之后，所有剩余元素都应满足 predicate"""
    s = HashSet()
    s.from_list(a + b)
    # 保留偶数
    s.filter(lambda x: x % 2 == 0)
    for v in s.to_list():
        assert v % 2 == 0


@given(st.lists(st.integers()), st.integers())
def test_map_preserves_size_if_injective(lst, offset):
    """如果映射是单射（如 +offset），大小不变"""
    s = HashSet()
    s.from_list(lst)
    original_size = s.size()
    s.map(lambda x: x + offset)
    assert s.size() == original_size


@given(st.lists(st.integers()))
def test_reduce_sum_equals_sum_of_set(lst):
    """reduce 求和应等于集合中所有元素的和（重复元素只算一次）"""
    s = HashSet()
    s.from_list(lst)
    total = s.reduce(lambda acc, val: acc + val, 0)
    expected = sum(set(lst))
    assert total == expected


@given(st.lists(st.integers()))
def test_iteration_matches_to_list(lst):
    """迭代器应该产生 to_list() 的所有元素（顺序无关）"""
    s = HashSet()
    s.from_list(lst)
    iter_elements = [x for x in s]
    assert set(iter_elements) == set(s.to_list())
    assert len(iter_elements) == s.size()


@given(st.lists(st.integers()))
def test_member_after_remove(lst):
    """删除后 member 返回 False，未删除的仍然 True"""
    if not lst:
        return
    s = HashSet()
    s.from_list(lst)
    v = lst[0]
    if v in s:
        s.remove(v)
        assert not s.member(v)
        # 其他元素依然存在
        for w in set(lst[1:]):
            if w != v:
                assert s.member(w)


@given(st.lists(st.integers()))
def test_none_handling(lst):
    """测试 None 值能正确处理"""
    s = HashSet()
    s.add(None)
    s.from_list(lst + [None, None])
    assert s.member(None)
    s.remove(None)
    assert not s.member(None)
    # None 不应出现在普通元素中
    for v in s.to_list():
        assert v is not None


# ========== 3. 可选：与 Python 内置 set 行为一致性测试 ==========


@given(st.lists(st.integers()))
def test_consistency_with_builtin_set(lst):
    """HashSet 的行为应与 Python set 在基本操作上一致"""
    py_set = set()
    my_set = HashSet()

    # 逐个添加
    for v in lst:
        py_set.add(v)
        my_set.add(v)

    # 成员检查
    for v in set(lst):
        assert (v in py_set) == my_set.member(v)

    # 大小
    assert len(py_set) == my_set.size()

    # 删除一个元素
    if lst:
        v = lst[0]
        if v in py_set:
            py_set.discard(v)
            if v in my_set:
                my_set.remove(v)
            assert (v in py_set) == my_set.member(v)

    # to_list 的集合相等
    assert set(my_set.to_list()) == py_set


# ========== 运行说明 ==========
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
