"""Тесты банковских счетов."""

import pytest

from bank.account import BankAccount, InsufficientFundsError
from bank.money import Money


@pytest.fixture
def account():
    return BankAccount("Иванов И. И.", "40817-0001")


def test_new_account_is_empty(account):
    assert account.balance == Money(0)
    assert account.history == ()


def test_deposit_and_withdraw(account):
    assert account.deposit(Money(10_000)) == Money(10_000)
    assert account.withdraw(Money(2_500)) == Money(7_500)
    assert [op for op, _ in account.history] == ["пополнение", "снятие"]


def test_withdraw_more_than_balance_keeps_balance(account):
    account.deposit(Money(1_000))
    with pytest.raises(InsufficientFundsError):
        account.withdraw(Money(1_001))
    assert account.balance == Money(1_000)
    assert len(account.history) == 1


@pytest.mark.parametrize("amount", [Money(0), Money(-100)])
def test_amount_must_be_positive(account, amount):
    with pytest.raises(ValueError):
        account.deposit(amount)


def test_wrong_currency_rejected(account):
    with pytest.raises(ValueError):
        account.deposit(Money(100, "USD"))


def test_amount_must_be_money(account):
    with pytest.raises(TypeError):
        account.deposit(100)


def test_balance_is_read_only(account):
    with pytest.raises(AttributeError):
        account.balance = Money(1_000_000)


def test_transfer_moves_money(account):
    target = BankAccount("Петров П. П.", "40817-0002")
    account.deposit(Money(5_000))
    account.transfer(target, Money(2_000))
    assert account.balance == Money(3_000)
    assert target.balance == Money(2_000)


def test_failed_transfer_keeps_money(account):
    target = BankAccount("Smith", "001", currency="USD")
    account.deposit(Money(5_000))
    with pytest.raises(ValueError):
        account.transfer(target, Money(2_000))
    assert account.balance == Money(5_000)
