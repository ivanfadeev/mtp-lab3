"""Тесты сериализатора JSON."""

import json
from decimal import Decimal

import pytest

from bank.account import BankAccount, SavingsAccount
from bank.money import Money
from bank.serializer import JsonSerializer


@pytest.fixture
def serializer():
    instance = JsonSerializer()
    for cls in (Money, BankAccount, SavingsAccount):
        instance.register(cls)
    return instance


def test_money_round_trip(serializer):
    text = serializer.dumps(Money(12_345, "EUR"))
    assert json.loads(text)["__type__"] == "Money"
    assert serializer.loads(text) == Money(12_345, "EUR")


def test_account_with_history_round_trip(serializer):
    account = SavingsAccount("Иванов", "42301", Money(100), "2.5")
    account.deposit(Money(1_000))
    account.withdraw(Money(300))
    restored = serializer.loads(serializer.dumps(account))
    assert isinstance(restored, SavingsAccount)
    assert restored.balance == Money(700)
    assert restored.history == account.history
    assert restored.rate_percent == Decimal("2.5")
    restored.deposit(Money(50))
    assert restored.balance == Money(750)


def test_containers_keep_their_types(serializer):
    value = {"tuple": (1, 2), 3: "int key", "list": [Decimal("0.1")]}
    assert serializer.loads(serializer.dumps(value)) == value


def test_dict_with_service_key_survives(serializer):
    value = {"__type__": "просто строка"}
    assert serializer.loads(serializer.dumps(value)) == value


def test_unregistered_class_is_rejected(serializer):
    class Secret:
        pass

    with pytest.raises(TypeError):
        serializer.dumps(Secret())


def test_unknown_type_in_json_is_rejected(serializer):
    with pytest.raises(TypeError):
        serializer.loads('{"__type__": "os.system", "state": {}}')


def test_register_conflicting_name_fails(serializer):
    impostor = type("Money", (), {})
    with pytest.raises(ValueError):
        serializer.register(impostor)
