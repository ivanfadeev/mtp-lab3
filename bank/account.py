"""Банковские счета: обычный и сберегательный."""

from bank.money import Money


class InsufficientFundsError(Exception):
    """На счёте не хватает средств для списания."""


class BankAccount:
    """Банковский счёт с пополнением, снятием и историей операций.

    Баланс закрыт от прямого изменения: он меняется только через
    deposit, withdraw и transfer, которые проверяют сумму и валюту.
    """

    def __init__(self, owner: str, number: str, currency: str = "RUB") -> None:
        if not owner.strip():
            raise ValueError("не указан владелец счёта")
        self._owner = owner
        self._number = number
        self._balance = Money(0, currency)
        self._history: list[tuple[str, Money]] = []

    @property
    def owner(self) -> str:
        """Владелец счёта."""
        return self._owner

    @property
    def number(self) -> str:
        """Номер счёта."""
        return self._number

    @property
    def currency(self) -> str:
        """Валюта счёта."""
        return self._balance.currency

    @property
    def balance(self) -> Money:
        """Текущий баланс; изменить его напрямую нельзя."""
        return self._balance

    @property
    def history(self) -> tuple[tuple[str, Money], ...]:
        """Операции по счёту в порядке выполнения (копия)."""
        return tuple(self._history)

    def deposit(self, amount: Money) -> Money:
        """Пополнить счёт и вернуть новый баланс."""
        self._check_amount(amount)
        self._apply("пополнение", amount)
        return self._balance

    def withdraw(self, amount: Money) -> Money:
        """Снять деньги со счёта и вернуть новый баланс.

        Если средств не хватает, возбуждается InsufficientFundsError,
        а баланс не меняется.
        """
        self._check_amount(amount)
        self._check_can_withdraw(amount)
        self._apply("снятие", -amount)
        return self._balance

    def transfer(self, target: "BankAccount", amount: Money) -> None:
        """Перевести сумму на другой счёт.

        Сумма проверяется для обоих счетов до списания, поэтому при
        ошибке деньги не пропадают ни с одного из них.
        """
        target._check_amount(amount)
        self.withdraw(amount)
        target.deposit(amount)

    def _apply(self, operation: str, amount: Money) -> None:
        """Изменить баланс и записать операцию в историю."""
        self._balance = self._balance + amount
        self._history.append((operation, amount))

    def _check_amount(self, amount: Money) -> None:
        """Проверить тип, валюту и знак суммы операции."""
        if not isinstance(amount, Money):
            raise TypeError("сумма должна быть объектом Money")
        if amount.currency != self.currency:
            raise ValueError(
                f"счёт в {self.currency}, а сумма в {amount.currency}"
            )
        if amount.kopecks <= 0:
            raise ValueError("сумма должна быть положительной")

    def _check_can_withdraw(self, amount: Money) -> None:
        """Убедиться, что средств хватает на списание."""
        if amount > self._balance:
            raise InsufficientFundsError(
                f"на счёте {self._balance}, а списать нужно {amount}"
            )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self._owner!r}, {self._number!r}, "
            f"balance={self._balance})"
        )
