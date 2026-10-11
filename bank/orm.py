"""Мини-ORM: таблица в памяти с методами insert и select."""

from collections.abc import Callable

TYPES: dict[str, type] = {"int": int, "float": float, "str": str, "bool": bool}
RESERVED = frozenset({"id", "where", "order_by", "descending", "limit"})

Row = dict[str, object]


class Column:
    """Столбец таблицы: имя, тип, обязательность и значение по умолчанию.

    Тип задаётся строкой из TYPES ("int", "float", "str", "bool"),
    чтобы описание таблицы можно было сохранить в JSON.
    """

    def __init__(
        self,
        name: str,
        type_name: str,
        required: bool = True,
        default: object = None,
    ) -> None:
        if not name.isidentifier() or name in RESERVED:
            raise ValueError(f"недопустимое имя столбца: {name!r}")
        if type_name not in TYPES:
            raise ValueError(f"неизвестный тип столбца: {type_name!r}")
        self.name = name
        self.type_name = type_name
        self.required = required
        self.default = None if default is None else self.convert(default)

    @property
    def python_type(self) -> type:
        """Тип Python, соответствующий столбцу."""
        return TYPES[self.type_name]

    def convert(self, value: object) -> object:
        """Проверить значение и привести его к типу столбца.

        None допустим только в необязательном столбце. Целое число
        в столбце float превращается в float; bool не считается
        числом.
        """
        if value is None:
            if self.required:
                raise ValueError(f"столбец {self.name} обязателен")
            return None
        expected = self.python_type
        if isinstance(value, bool) != (expected is bool):
            raise TypeError(self._type_error(value))
        if expected is float and isinstance(value, int):
            return float(value)
        if not isinstance(value, expected):
            raise TypeError(self._type_error(value))
        return value

    def _type_error(self, value: object) -> str:
        """Сформировать текст ошибки о несовпадении типа."""
        return (
            f"столбец {self.name} ожидает {self.type_name}, "
            f"получено {type(value).__name__}"
        )

    def __repr__(self) -> str:
        return f"Column({self.name!r}, {self.type_name!r})"


class Table:
    """Таблица в памяти с автоматическим первичным ключом id.

    insert проверяет значения по описанию столбцов, select отбирает
    строки по равенству столбцов и необязательному условию. Обе
    операции возвращают копии данных, поэтому изменить таблицу в
    обход insert нельзя.
    """

    def __init__(self, name: str, columns: list[Column]) -> None:
        names = [column.name for column in columns]
        if not names:
            raise ValueError("у таблицы должен быть хотя бы один столбец")
        if len(set(names)) != len(names):
            raise ValueError("имена столбцов повторяются")
        self._name = name
        self._columns = {column.name: column for column in columns}
        self._rows: dict[int, Row] = {}
        self._next_id = 1

    @property
    def name(self) -> str:
        """Имя таблицы."""
        return self._name

    @property
    def columns(self) -> tuple[Column, ...]:
        """Столбцы таблицы в порядке объявления."""
        return tuple(self._columns.values())

    def insert(self, **values: object) -> int:
        """Добавить строку и вернуть её id.

        Пропущенные столбцы получают значение по умолчанию; лишние
        столбцы, неверные типы и пустые обязательные поля вызывают
        ошибку, и строка не добавляется.
        """
        unknown = set(values) - set(self._columns)
        if unknown:
            raise ValueError(f"нет столбцов: {', '.join(sorted(unknown))}")
        row: Row = {"id": self._next_id}
        for name, column in self._columns.items():
            row[name] = column.convert(values.get(name, column.default))
        self._rows[self._next_id] = row
        self._next_id += 1
        return row["id"]

    def select(
        self,
        where: Callable[[Row], bool] | None = None,
        *,
        order_by: str | None = None,
        descending: bool = False,
        limit: int | None = None,
        **equals: object,
    ) -> list[Row]:
        """Вернуть копии строк, подходящих под условия.

        equals — точное совпадение значений столбцов (в том числе id),
        where — дополнительная функция-условие над строкой. Строки
        можно отсортировать по столбцу (пустые значения идут после
        заполненных) и ограничить их число.
        """
        known = {"id", *self._columns}
        unknown = set(equals) - known
        if unknown:
            raise ValueError(f"нет столбцов: {', '.join(sorted(unknown))}")
        if order_by is not None and order_by not in known:
            raise ValueError(f"нет столбца для сортировки: {order_by}")
        if limit is not None and limit < 0:
            raise ValueError("limit не может быть отрицательным")

        result = []
        for row in self._rows.values():
            if all(row[name] == value for name, value in equals.items()):
                if where is None or where(dict(row)):
                    result.append(dict(row))
        if order_by is not None:
            filled = [row for row in result if row[order_by] is not None]
            empty = [row for row in result if row[order_by] is None]
            filled.sort(key=lambda row: row[order_by], reverse=descending)
            result = filled + empty
        return result if limit is None else result[:limit]

    def get(self, row_id: int) -> Row | None:
        """Вернуть копию строки по id или None, если её нет."""
        row = self._rows.get(row_id)
        return None if row is None else dict(row)

    def __len__(self) -> int:
        return len(self._rows)

    def __repr__(self) -> str:
        return f"Table({self._name!r}, rows={len(self)})"
