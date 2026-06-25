"""
Unit-тесты для algorithms.py.

Идея: каждый алгоритм сортировки должен после прогона всех шагов
дать массив, эквивалентный sorted(input), и не терять/не добавлять
элементы. Параметризуем по всем алгоритмам из ALGORITHMS, чтобы
один набор кейсов проверял все семь функций сразу.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from algorithms import get_steps, ALGORITHMS


ALL_ALGOS = list(ALGORITHMS.keys())


@pytest.mark.parametrize("algo", ALL_ALGOS)
class TestSortingCorrectness:
    """Базовая корректность: на выходе отсортированный массив."""

    def test_random_array(self, algo):
        arr = [5, 3, 8, 1, 9, 2, 7]
        steps = get_steps(arr, algo)
        assert steps[-1]["arr"] == sorted(arr)

    def test_already_sorted(self, algo):
        arr = [1, 2, 3, 4, 5]
        steps = get_steps(arr, algo)
        assert steps[-1]["arr"] == arr

    def test_reverse_sorted(self, algo):
        arr = [5, 4, 3, 2, 1]
        steps = get_steps(arr, algo)
        assert steps[-1]["arr"] == sorted(arr)

    def test_duplicates(self, algo):
        arr = [4, 2, 4, 1, 2, 4]
        steps = get_steps(arr, algo)
        assert steps[-1]["arr"] == sorted(arr)

    def test_single_element(self, algo):
        arr = [42]
        steps = get_steps(arr, algo)
        assert steps[-1]["arr"] == [42]

    def test_empty_array(self, algo):
        # Граничный случай: сортировка пустого массива не должна падать.
        steps = get_steps([], algo)
        assert steps[-1]["arr"] == []

    def test_two_elements(self, algo):
        for arr in ([1, 2], [2, 1]):
            steps = get_steps(arr, algo)
            assert steps[-1]["arr"] == sorted(arr)

    def test_no_elements_lost_or_duplicated(self, algo):
        # Сортировка - это перестановка: мультисеты совпадают.
        arr = [9, 1, 5, 1, 9, 3]
        steps = get_steps(arr, algo)
        assert sorted(steps[-1]["arr"]) == sorted(arr)
        assert len(steps[-1]["arr"]) == len(arr)

    def test_final_step_marks_everything_done(self, algo):
        arr = [3, 1, 2]
        steps = get_steps(arr, algo)
        assert sorted(steps[-1]["done"]) == list(range(len(arr)))

    def test_does_not_mutate_input(self, algo):
        # get_steps работает с копией, оригинальный список не должен меняться.
        arr = [3, 1, 2]
        original = list(arr)
        get_steps(arr, algo)
        assert arr == original

    def test_step_structure(self, algo):
        # Каждый шаг должен содержать все ожидаемые ключи нужного типа.
        steps = get_steps([3, 1, 2], algo)
        for step in steps:
            assert isinstance(step["arr"], list)
            assert isinstance(step["cmp"], list)
            assert isinstance(step["swap"], list)
            assert isinstance(step["done"], list)
            assert isinstance(step["cmps"], int)
            assert isinstance(step["swaps"], int)

    def test_cmps_and_swaps_are_monotonic(self, algo):
        # Счётчики только растут от шага к шагу.
        steps = get_steps([5, 3, 8, 1, 9, 2, 7], algo)
        for prev, cur in zip(steps, steps[1:]):
            assert cur["cmps"] >= prev["cmps"]
            assert cur["swaps"] >= prev["swaps"]


def test_unknown_algorithm_raises():
    with pytest.raises(ValueError):
        get_steps([1, 2, 3], "not_a_real_algorithm")


def test_registry_matches_readme_claims():
    # README заявляет 6 алгоритмов; в реальности зарегистрировано 7
    # (heap_sort добавлен, но не упомянут). Тест фиксирует факт.
    expected = {"bubble", "insertion", "selection", "quick", "merge", "shell", "heap"}
    assert set(ALGORITHMS.keys()) == expected
