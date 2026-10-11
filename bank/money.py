"""Денежная сумма с перегрузкой арифметических операторов."""

from decimal import Decimal, InvalidOperation
from functools import total_ordering


@total_ordering
class Money:
    """Неизменяемая денежная сумма в копейках с указанием валюты.

    Сумма хранится целым числом копеек, поэтому сложение не даёт
    ошибок округления, как у float. Складывать, вычитать и
    сравнивать можно только суммы в одной валюте.
    """

    def __init__(self, kopecks: int = 0, currency: str = "RUB") -> None:
        if isinstance(kopecks, bool) or not isinstance(kopecks, int):
            raise TypeError("сумма задаётся целым числом копеек")
        if not currency:
            raise ValueError("не указана валюта")
        self._kopecks = kopecks
        self._currency = currency.upper()

    @classmethod
    def from_string(cls, amount: str, currency: str = "RUB") -> "Money":
        """Создать сумму из строки в рублях, например "1250.50".

        Допускается не больше двух знаков после точки; иначе или при
        нечисловой строке возбуждается ValueError.
        """
        try:
            value = Decimal(amount.strip().replace(",", ".")) * 100
        except InvalidOperation:
            raise ValueError(f"не число: {amount!r}") from None
        if value != value.to_integral_value():
            raise ValueError("больше двух знаков после точки")
        return cls(int(value), currency)

    @property
    def kopecks(self) -> int:
        """Сумма в копейках."""
        return self._kopecks

    @property
    def currency(self) -> str:
        """Код валюты в верхнем регистре."""
        return self._currency

    def _same_currency(self, other: "Money") -> None:
        """Убедиться, что валюты совпадают, иначе возбудить ValueError."""
        if self._currency != other.currency:
            raise ValueError(
                f"разные валюты: {self._currency} и {other.currency}"
            )

    def __add__(self, other: object) -> "Money":
        """Сложить две суммы одной валюты и вернуть новую сумму."""
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self._kopecks + other.kopecks, self._currency)

    def __radd__(self, other: object) -> "Money":
        """Разрешить sum() по списку сумм: 0 + Money даёт Money."""
        if isinstance(other, int) and other == 0:
            return self
        return NotImplemented

    def __sub__(self, other: object) -> "Money":
        """Вычесть сумму той же валюты и вернуть новую сумму."""
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self._kopecks - other.kopecks, self._currency)

    def __neg__(self) -> "Money":
        """Вернуть сумму с противоположным знаком."""
        return Money(-self._kopecks, self._currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self._kopecks, self._currency) == (
            other.kopecks,
            other.currency,
        )

    def __lt__(self, other: object) -> bool:
        """Сравнить суммы одной валюты."""
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return self._kopecks < other.kopecks

    def __hash__(self) -> int:
        return hash((self._kopecks, self._currency))

    def __bool__(self) -> bool:
        return self._kopecks != 0

    def __repr__(self) -> str:
        return f"Money({self._kopecks}, {self._currency!r})"

    def __str__(self) -> str:
        sign = "-" if self._kopecks < 0 else ""
        rubles, kopecks = divmod(abs(self._kopecks), 100)
        return f"{sign}{rubles}.{kopecks:02d} {self._currency}"
