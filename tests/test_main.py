"""Проверка демонстрационного сценария."""

import main


def test_demo_runs_and_saves_state(tmp_path, capsys):
    target = tmp_path / "state.json"
    main.main(["--data", str(target)])
    output = capsys.readouterr().out
    assert target.exists()
    assert "1250.50 RUB + 99.50 RUB = 1350.00 RUB" in output
    assert "история вклада совпадает: True" in output
    assert "строки таблицы совпадают: True" in output
