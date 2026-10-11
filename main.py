"""Лабораторная работа №3: объектно-ориентированное программирование.

Демонстрация классов варианта 7: сумма денег с оператором «+»,
банковские счета, работа с файлами, сериализация в JSON и мини-ORM.
Автор: Фадеев Иван Александрович, группа 221141, вариант 7.
"""

import argparse
from pathlib import Path

from bank.account import BankAccount, InsufficientFundsError, SavingsAccount
from bank.files import TextFile
from bank.money import Money
from bank.orm import Column, Table
from bank.serializer import JsonSerializer

APP_NAME = "lab3"
APP_VERSION = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    """Собрать разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Демонстрация классов лабораторной №3 (вариант 7)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("bank_state.json"),
        help="файл для сохранения состояния (по умолчанию bank_state.json)",
    )
    return parser


def build_serializer() -> JsonSerializer:
    """Создать сериализатор и зарегистрировать в нём классы проекта."""
    serializer = JsonSerializer()
    for cls in (Money, BankAccount, SavingsAccount, Column, Table):
        serializer.register(cls)
    return serializer


def show_money() -> None:
    """Показать перегрузку оператора «+» у Money."""
    print("== Перегрузка оператора + ==")
    price = Money.from_string("1250.50")
    delivery = Money.from_string("99.50")
    print(f"{price} + {delivery} = {price + delivery}")
    parts = [Money(10_000), Money(2_550), Money(45)]
    print(f"sum({[str(part) for part in parts]}) = {sum(parts)}")
    try:
        Money(100, "RUB") + Money(100, "USD")
    except ValueError as error:
        print(f"RUB + USD -> ValueError: {error}")


def show_accounts() -> list[BankAccount]:
    """Показать пополнение, снятие и перевод между счетами."""
    print("\n== Банковский счёт ==")
    card = BankAccount("Фадеев И. А.", "40817-0001")
    card.deposit(Money.from_string("15000"))
    card.withdraw(Money.from_string("3200.75"))
    print(f"после пополнения и снятия: {card.balance}")
    try:
        card.withdraw(Money.from_string("50000"))
    except InsufficientFundsError as error:
        print(f"снятие 50000 -> InsufficientFundsError: {error}")

    savings = SavingsAccount(
        "Фадеев И. А.",
        "42301-0002",
        min_balance=Money.from_string("1000"),
        rate_percent="1.5",
    )
    card.transfer(savings, Money.from_string("8000"))
    print(f"перевод 8000: карта {card.balance}, вклад {savings.balance}")
    print(f"начислено процентов: {savings.add_interest()}")
    try:
        savings.withdraw(Money.from_string("7500"))
    except InsufficientFundsError as error:
        print(f"снятие 7500 со вклада -> отказ: {error}")
    for operation, amount in savings.history:
        print(f"  вклад: {operation:<11} {amount}")
    return [card, savings]


def show_table() -> Table:
    """Показать работу мини-ORM: insert и select."""
    print("\n== Мини-ORM ==")
    clients = Table(
        "clients",
        [
            Column("name", "str"),
            Column("city", "str"),
            Column("age", "int"),
            Column("vip", "bool", default=False),
        ],
    )
    clients.insert(name="Иван", city="Москва", age=21, vip=True)
    clients.insert(name="Мария", city="Казань", age=34)
    clients.insert(name="Олег", city="Москва", age=45)
    clients.insert(name="Анна", city="Москва", age=19)
    print(f"{clients!r}")
    moscow = clients.select(city="Москва", order_by="age")
    print("клиенты из Москвы по возрасту:")
    for row in moscow:
        print(f"  {row}")
    adults = clients.select(lambda row: row["age"] >= 30, order_by="name")
    print(f"старше 30: {[row['name'] for row in adults]}")
    try:
        clients.insert(name="Пётр", city="Тула", age="сорок")
    except TypeError as error:
        print(f"insert с age='сорок' -> TypeError: {error}")
    return clients


def show_saving(
    path: Path, accounts: list[BankAccount], clients: Table
) -> None:
    """Сохранить объекты в JSON-файл и прочитать их обратно."""
    print("\n== Сериализация в JSON и работа с файлом ==")
    serializer = build_serializer()
    state_file = TextFile(path)
    state = {"accounts": accounts, "clients": clients}
    written = state_file.write(serializer.dumps(state))
    print(f"записано символов: {written}, файл {state_file.path}")

    restored = serializer.loads(state_file.read())
    card, savings = restored["accounts"]
    print(f"восстановлено: {card!r}")
    print(f"восстановлено: {savings!r}")
    same_history = savings.history == accounts[1].history
    print(f"история вклада совпадает: {same_history}")
    same_rows = restored["clients"].select() == clients.select()
    print(f"строки таблицы совпадают: {same_rows}")


def main(argv: list[str] | None = None) -> None:
    """Выполнить демонстрацию всех заданий."""
    args = build_parser().parse_args(argv)
    show_money()
    accounts = show_accounts()
    clients = show_table()
    show_saving(args.data, accounts, clients)


if __name__ == "__main__":
    main()
