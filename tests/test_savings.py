"""Тесты сберегательного счёта и полиморфизма проверки снятия."""

from decimal import Decimal

import pytest

from bank.account import BankAccount, InsufficientFundsError, SavingsAccount
from bank.money import Money


def test_savings_keeps_min_balance():
    savings = SavingsAccount("Иванов", "42301", Money(1_000))
    savings.deposit(Money(3_000))
    savings.withdraw(Money(2_000))
    with pytest.raises(InsufficientFundsError):
        savings.withdraw(Money(1))
    assert savings.balance == Money(1_000)


def test_savings_interest_is_rounded_half_up():
    savings = SavingsAccount("Иванов", "42301", Money(0), rate_percent="1.5")
    savings.deposit(Money(10_033))
    assert savings.add_interest() == Money(150)
    assert savings.balance == Money(10_183)
    assert savings.history[-1][0] == "проценты"
    assert savings.rate_percent == Decimal("1.5")


def test_zero_interest_not_recorded():
    savings = SavingsAccount("Иванов", "42301", Money(0))
    savings.deposit(Money(500))
    assert savings.add_interest() == Money(0)
    assert len(savings.history) == 1


def test_negative_rate_rejected():
    with pytest.raises(ValueError):
        SavingsAccount("Иванов", "42301", Money(0), rate_percent="-1")


def test_polymorphic_withdraw_check():
    accounts = [
        BankAccount("А", "1"),
        SavingsAccount("Б", "2", Money(500)),
    ]
    allowed = []
    for item in accounts:
        item.deposit(Money(1_000))
        try:
            item.withdraw(Money(800))
            allowed.append(True)
        except InsufficientFundsError:
            allowed.append(False)
    assert allowed == [True, False]
