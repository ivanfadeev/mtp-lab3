"""Тесты мини-ORM."""

import pytest

from bank.orm import Column, Table
from bank.serializer import JsonSerializer


@pytest.fixture
def table():
    users = Table(
        "users",
        [
            Column("name", "str"),
            Column("age", "int"),
            Column("score", "float", required=False),
            Column("active", "bool", default=True),
        ],
    )
    users.insert(name="Аня", age=19, score=4.5)
    users.insert(name="Борис", age=31)
    users.insert(name="Вера", age=25, score=3, active=False)
    return users


def test_insert_returns_sequential_ids(table):
    assert table.insert(name="Глеб", age=40) == 4
    assert len(table) == 4


def test_insert_fills_defaults_and_converts(table):
    assert table.get(2) == {
        "id": 2, "name": "Борис", "age": 31, "score": None, "active": True,
    }
    assert table.get(3)["score"] == 3.0


@pytest.mark.parametrize(
    "values, error",
    [
        ({"name": "X"}, ValueError),
        ({"name": "X", "age": "20"}, TypeError),
        ({"name": "X", "age": True}, TypeError),
        ({"name": "X", "age": 20, "city": "Тула"}, ValueError),
    ],
)
def test_insert_validates(table, values, error):
    with pytest.raises(error):
        table.insert(**values)
    assert len(table) == 3


def test_select_all(table):
    assert [row["name"] for row in table.select()] == ["Аня", "Борис", "Вера"]


def test_select_by_equality(table):
    assert [row["id"] for row in table.select(active=True)] == [1, 2]
    assert table.select(id=3)[0]["name"] == "Вера"


def test_select_with_condition_order_and_limit(table):
    rows = table.select(
        lambda row: row["age"] > 18, order_by="age", descending=True, limit=2
    )
    assert [row["name"] for row in rows] == ["Борис", "Вера"]


def test_order_puts_empty_values_last(table):
    assert [r["id"] for r in table.select(order_by="score")] == [3, 1, 2]


def test_select_returns_copies(table):
    table.select()[0]["name"] = "Изменено"
    assert table.get(1)["name"] == "Аня"


@pytest.mark.parametrize(
    "kwargs",
    [{"city": "Тула"}, {"order_by": "city"}, {"limit": -1}],
)
def test_select_validates(table, kwargs):
    with pytest.raises(ValueError):
        table.select(**kwargs)


@pytest.mark.parametrize("name", ["id", "limit", "1st", "has space"])
def test_column_name_validation(name):
    with pytest.raises(ValueError):
        Column(name, "str")


def test_table_validation():
    with pytest.raises(ValueError):
        Table("empty", [])
    with pytest.raises(ValueError):
        Table("dup", [Column("a", "int"), Column("a", "str")])
    with pytest.raises(ValueError):
        Column("a", "list")


def test_table_survives_json_round_trip(table):
    serializer = JsonSerializer()
    serializer.register(Table)
    serializer.register(Column)
    restored = serializer.loads(serializer.dumps(table))
    assert restored.select() == table.select()
    assert restored.insert(name="Глеб", age=40) == 4
