"""Сериализация объектов в JSON и обратно."""

import json
from decimal import Decimal


class JsonSerializer:
    """Сохраняет объекты зарегистрированных классов в JSON и обратно.

    Объект записывается как словарь его атрибутов с полем "__type__".
    При чтении он создаётся без вызова __init__ и получает
    сохранённые атрибуты. Восстанавливаются только классы,
    зарегистрированные через register, поэтому из чужого JSON нельзя
    создать произвольный объект. Кроме объектов поддерживаются None,
    bool, int, float, str, list, tuple, Decimal и словари с ключами
    этих простых типов. Объекты с __slots__ не поддерживаются.
    """

    TYPE_KEY = "__type__"
    TUPLE_KEY = "__tuple__"
    DECIMAL_KEY = "__decimal__"
    MAPPING_KEY = "__mapping__"
    SERVICE_KEYS = frozenset({TYPE_KEY, TUPLE_KEY, DECIMAL_KEY, MAPPING_KEY})

    def __init__(self) -> None:
        self._registry: dict[str, type] = {}

    def register(self, cls: type) -> type:
        """Разрешить сериализацию класса и вернуть его же."""
        name = cls.__qualname__
        known = self._registry.get(name)
        if known is not None and known is not cls:
            raise ValueError(f"класс с именем {name} уже зарегистрирован")
        self._registry[name] = cls
        return cls

    def dumps(self, value: object, indent: int | None = 2) -> str:
        """Преобразовать значение в строку JSON."""
        return json.dumps(
            self._encode(value), ensure_ascii=False, indent=indent
        )

    def loads(self, text: str) -> object:
        """Восстановить значение из строки JSON."""
        return self._decode(json.loads(text))

    def _encode(self, value: object) -> object:
        """Преобразовать значение в структуру, пригодную для json."""
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, Decimal):
            return {self.DECIMAL_KEY: str(value)}
        if isinstance(value, list):
            return [self._encode(item) for item in value]
        if isinstance(value, tuple):
            return {self.TUPLE_KEY: [self._encode(item) for item in value]}
        if isinstance(value, dict):
            return self._encode_dict(value)
        return self._encode_object(value)

    def _encode_dict(self, value: dict) -> dict:
        """Закодировать словарь; особые ключи сохраняются списком пар."""
        plain = all(isinstance(key, str) for key in value)
        if plain and not self.SERVICE_KEYS.intersection(value):
            return {key: self._encode(item) for key, item in value.items()}
        pairs = [[self._encode(k), self._encode(v)] for k, v in value.items()]
        return {self.MAPPING_KEY: pairs}

    def _encode_object(self, value: object) -> dict:
        """Закодировать объект зарегистрированного класса."""
        cls = type(value)
        name = cls.__qualname__
        if self._registry.get(name) is not cls:
            raise TypeError(f"класс {name} не зарегистрирован")
        return {self.TYPE_KEY: name, "state": self._encode(vars(value))}

    def _decode(self, value: object) -> object:
        """Восстановить значение из структуры, прочитанной из JSON."""
        if isinstance(value, list):
            return [self._decode(item) for item in value]
        if not isinstance(value, dict):
            return value
        if self.TYPE_KEY in value:
            return self._decode_object(value)
        if self.TUPLE_KEY in value:
            return tuple(self._decode(item) for item in value[self.TUPLE_KEY])
        if self.DECIMAL_KEY in value:
            return Decimal(value[self.DECIMAL_KEY])
        if self.MAPPING_KEY in value:
            return {
                self._decode(key): self._decode(item)
                for key, item in value[self.MAPPING_KEY]
            }
        return {key: self._decode(item) for key, item in value.items()}

    def _decode_object(self, value: dict) -> object:
        """Создать объект зарегистрированного класса без вызова __init__."""
        name = value[self.TYPE_KEY]
        cls = self._registry.get(name)
        if cls is None:
            raise TypeError(f"неизвестный класс в JSON: {name}")
        obj = cls.__new__(cls)
        obj.__dict__.update(self._decode(value["state"]))
        return obj
