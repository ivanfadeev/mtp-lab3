"""Тесты класса Money и перегрузки оператора «+»."""

import pytest

from bank.money import Money


def test_addition_returns_new_sum():
    first = Money(1050)
    second = Money(250)
    assert first + second == Money(1300)
    assert first == Money(1050)


def test_sum_of_list_uses_radd():
    assert sum([Money(100), Money(250), Money(5)]) == Money(355)


def test_add_different_currencies_fails():
    with pytest.raises(ValueError):
        Money(100, "RUB") + Money(100, "USD")


def test_add_non_money_is_not_supported():
    with pytest.raises(TypeError):
        Money(100) + 5


def test_subtraction_and_negation():
    assert Money(500) - Money(800) == Money(-300)
    assert -Money(300) == Money(-300)


def test_comparison_and_hash():
    assert Money(100) < Money(200)
    assert Money(300) >= Money(300)
    assert len({Money(100), Money(100), Money(100, "USD")}) == 2


@pytest.mark.parametrize(
    "text, kopecks",
    [("1250.50", 125050), ("0,99", 99), (" 7 ", 700), ("-3.5", -350)],
)
def test_from_string(text, kopecks):
    assert Money.from_string(text).kopecks == kopecks


@pytest.mark.parametrize("text", ["abc", "1.005", ""])
def test_from_string_rejects_bad_input(text):
    with pytest.raises(ValueError):
        Money.from_string(text)


def test_constructor_rejects_float_and_bool():
    with pytest.raises(TypeError):
        Money(10.5)
    with pytest.raises(TypeError):
        Money(True)


def test_str_formats_rubles_and_kopecks():
    assert str(Money(125005)) == "1250.05 RUB"
    assert str(Money(-7, "usd")) == "-0.07 USD"
