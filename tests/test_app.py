"""
Functional-тесты для app.py.

Используем Flask test_client — он гоняет WSGI-приложение в памяти,
без реального сетевого сервера. Это и есть functional-уровень:
проверяем поведение HTTP API "снаружи", а не внутренние функции.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app, generate_array


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── GET / ────────────────────────────────────────────────────────────────────

def test_index_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200


# ── GET /api/array ───────────────────────────────────────────────────────────

def test_get_array_default(client):
    resp = client.get("/api/array")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "array" in data
    assert len(data["array"]) == 40  # дефолтный size в app.py


def test_get_array_custom_size(client):
    resp = client.get("/api/array?size=15")
    data = resp.get_json()
    assert len(data["array"]) == 15


def test_get_array_size_clamped_to_max(client):
    # app.py клампит size в диапазон [5, 100]
    resp = client.get("/api/array?size=500")
    data = resp.get_json()
    assert len(data["array"]) == 100


def test_get_array_size_clamped_to_min(client):
    resp = client.get("/api/array?size=1")
    data = resp.get_json()
    assert len(data["array"]) == 5


def test_get_array_reversed_mode(client):
    resp = client.get("/api/array?size=10&mode=reversed")
    data = resp.get_json()
    arr = data["array"]
    assert arr == sorted(arr, reverse=True)


def test_get_array_nearly_mode_has_right_size(client):
    resp = client.get("/api/array?size=20&mode=nearly")
    data = resp.get_json()
    assert len(data["array"]) == 20


def test_get_array_invalid_size_param_returns_400(client):
    # request.args.get + int() на нечисловой строке -> ValueError,
    # Flask должен превратить это в 400, а не в 500/краш.
    resp = client.get("/api/array?size=abc")
    assert resp.status_code == 400


# ── POST /api/sort ───────────────────────────────────────────────────────────

def test_sort_endpoint_returns_sorted_result(client):
    resp = client.post("/api/sort", json={"array": [5, 3, 1, 4, 2], "algorithm": "bubble"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "steps" in data
    assert "total" in data
    assert data["total"] == len(data["steps"])
    assert data["steps"][-1]["arr"] == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("algo", ["bubble", "insertion", "selection", "quick", "merge", "shell", "heap"])
def test_sort_endpoint_works_for_every_algorithm(client, algo):
    resp = client.post("/api/sort", json={"array": [9, 4, 6, 1, 3], "algorithm": algo})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["steps"][-1]["arr"] == [1, 3, 4, 6, 9]


def test_sort_endpoint_unknown_algorithm(client):
    resp = client.post("/api/sort", json={"array": [1, 2, 3], "algorithm": "bogosort"})
    assert resp.status_code == 400


def test_sort_endpoint_missing_body(client):
    resp = client.post("/api/sort", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    # пустой array по умолчанию -> defaults к "bubble" на пустом списке
    assert data["steps"][-1]["arr"] == []


def test_sort_endpoint_empty_array(client):
    resp = client.post("/api/sort", json={"array": [], "algorithm": "merge"})
    assert resp.status_code == 200
    assert resp.get_json()["steps"][-1]["arr"] == []


# ── generate_array (вспомогательная функция, дёргается из роута) ───────────

def test_generate_array_random_size_and_range():
    arr = generate_array(30, "random")
    assert len(arr) == 30
    assert all(10 <= x <= 100 for x in arr)


def test_generate_array_reversed_is_strictly_descending():
    arr = generate_array(10, "reversed")
    assert arr == list(range(100, 90, -1))


def test_generate_array_nearly_preserves_multiset():
    # "nearly" должен быть почти отсортирован, но содержать те же числа,
    # что и base range, просто с парой свапов.
    arr = generate_array(20, "nearly")
    assert sorted(arr) == list(range(10, 30))


def test_generate_array_unknown_mode_falls_back_to_random():
    arr = generate_array(10, "totally_made_up_mode")
    assert len(arr) == 10
