"""Тесты класса TextFile."""

import pytest

from bank.files import TextFile


def test_write_and_read(tmp_path):
    file = TextFile(tmp_path / "data" / "note.txt")
    assert not file.exists()
    assert file.write("Привет") == 6
    assert file.exists()
    assert file.read() == "Привет"


def test_write_replaces_content_without_temp_files(tmp_path):
    file = TextFile(tmp_path / "note.txt")
    file.write("старое")
    file.write("новое")
    assert file.read() == "новое"
    assert [p.name for p in tmp_path.iterdir()] == ["note.txt"]


def test_append_lines(tmp_path):
    file = TextFile(tmp_path / "log.txt")
    file.append_line("первая")
    file.append_line("вторая")
    assert file.read_lines() == ["первая", "вторая"]


def test_size_counts_bytes(tmp_path):
    file = TextFile(tmp_path / "ru.txt")
    file.write("ёж")
    assert file.size() == 4


def test_delete(tmp_path):
    file = TextFile(tmp_path / "temp.txt")
    file.write("x")
    assert file.delete() is True
    assert file.delete() is False


def test_read_missing_file_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        TextFile(tmp_path / "missing.txt").read()


def test_custom_encoding(tmp_path):
    file = TextFile(tmp_path / "cp.txt", encoding="cp1251")
    file.write("Тест")
    assert file.size() == 4
    assert file.read() == "Тест"
