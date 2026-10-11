"""Работа с текстовыми файлами."""

import os
from pathlib import Path


class TextFile:
    """Текстовый файл: чтение, запись, дозапись и работа со строками.

    Все операции выполняются в указанной кодировке (по умолчанию
    UTF-8). Запись выполняется через временный файл с последующей
    заменой, поэтому при сбое старое содержимое не портится.
    """

    def __init__(self, path: str | Path, encoding: str = "utf-8") -> None:
        self._path = Path(path)
        self._encoding = encoding

    @property
    def path(self) -> Path:
        """Путь к файлу."""
        return self._path

    @property
    def encoding(self) -> str:
        """Кодировка файла."""
        return self._encoding

    def exists(self) -> bool:
        """Проверить, существует ли файл."""
        return self._path.is_file()

    def size(self) -> int:
        """Размер файла в байтах."""
        return self._path.stat().st_size

    def read(self) -> str:
        """Прочитать файл целиком."""
        return self._path.read_text(encoding=self._encoding)

    def read_lines(self) -> list[str]:
        """Прочитать файл и вернуть список строк без символов перевода."""
        return self.read().splitlines()

    def write(self, text: str) -> int:
        """Заменить содержимое файла и вернуть число записанных символов.

        Недостающие каталоги создаются. Данные сначала пишутся во
        временный файл рядом, затем он атомарно заменяет исходный.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_name(self._path.name + ".tmp")
        with temporary.open("w", encoding=self._encoding) as stream:
            written = stream.write(text)
        os.replace(temporary, self._path)
        return written

    def append(self, text: str) -> int:
        """Дописать текст в конец файла и вернуть число символов."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding=self._encoding) as stream:
            return stream.write(text)

    def append_line(self, line: str) -> int:
        """Дописать строку и перевод строки в конец файла."""
        return self.append(line + "\n")

    def delete(self) -> bool:
        """Удалить файл; вернуть True, если он существовал."""
        if not self.exists():
            return False
        self._path.unlink()
        return True

    def __repr__(self) -> str:
        return f"TextFile({str(self._path)!r})"
