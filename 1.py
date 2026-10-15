"""Модуль для парсинга строковых описаний объектов файловой системы."""

import shlex
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple


class ParseError(Exception):
    """Базовое исключение для ошибок разбора входной строки."""


class UnknownObjectTypeError(ParseError):
    """Исключение при передаче неизвестного типа объекта."""


class InvalidPropertyError(ParseError):
    """Исключение при некорректном значении или отсутствии свойства объекта."""


@dataclass
class FileObject:
    """Базовый класс, представляющий файл."""

    name: str
    creation_date: date
    size: int

    def __str__(self) -> str:
        """Возвращает строковое представление файла."""
        date_str = self.creation_date.strftime("%Y.%m.%d")
        return f"Файл: '{self.name}', Дата создания: {date_str}, Размер: {self.size} байт"


@dataclass
class AudioFile(FileObject):
    """Класс, представляющий аудиофайл с длительностью."""

    duration: time

    def __str__(self) -> str:
        """Возвращает строковое представление аудиофайла."""
        base_str = super().__str__()
        time_str = self.duration.strftime("%H:%M")
        return f"Аудиофайл -> {base_str}, Длительность: {time_str}"


@dataclass
class ArchiveFile(FileObject):
    """Класс, представляющий архив со степенью и алгоритмом сжатия."""

    compression_ratio: float
    algorithm: str

    def __str__(self) -> str:
        """Возвращает строковое представление архива."""
        base_str = super().__str__()
        return (
            f"Архив -> {base_str}, Сжатие: {self.compression_ratio}, "
            f"Алгоритм: '{self.algorithm}'"
        )


class TokenRecognizer:
    """Вспомогательный класс для распознавания и парсинга токенов."""

    @staticmethod
    def is_int(token: str) -> bool:
        """Проверяет, является ли токен целым числом (включая отрицательные)."""
        if token.startswith("-"):
            return token[1:].isdigit()
        return token.isdigit()

    @staticmethod
    def is_date(token: str) -> bool:
        """Проверяет формат даты гггг.мм.дд."""
        return len(token) == 10 and token[4] == "." and token[7] == "."

    @staticmethod
    def is_time(token: str) -> bool:
        """Проверяет формат времени чч:мм."""
        return len(token) == 5 and token[2] == ":"

    @staticmethod
    def is_float(token: str) -> bool:
        """Проверяет, является ли токен дробным числом."""
        clean = token[1:] if token.startswith("-") else token
        return "." in clean and clean.replace(".", "", 1).isdigit()

    @staticmethod
    def parse_date(token: str) -> date:
        """Преобразует строку в объект даты без накладных расходов strptime."""
        try:
            year, month, day = int(token[0:4]), int(token[5:7]), int(token[8:10])
            return date(year, month, day)
        except ValueError as err:
            raise InvalidPropertyError(f"Некорректная дата: {token}") from err

    @staticmethod
    def parse_time(token: str) -> time:
        """Преобразует строку в объект времени без накладных расходов strptime."""
        try:
            hour, minute = int(token[0:2]), int(token[3:5])
            return time(hour, minute)
        except ValueError as err:
            raise InvalidPropertyError(f"Некорректное время: {token}") from err


class PropertyExtractor:
    """Класс для извлечения типизированных свойств из списка токенов."""

    def __init__(self, recognizer: Optional[TokenRecognizer] = None) -> None:
        """Инициализирует экстрактор свойств."""
        self.recognizer = recognizer or TokenRecognizer()

    def extract(self, tokens: List[str]) -> Dict[str, Any]:
        """Извлекает свойства из списка строковых токенов."""
        data: Dict[str, Any] = {
            "size": None,
            "date": None,
            "time": None,
            "float": None,
            "strings": [],
        }
        for token in tokens:
            self._assign_token(token, data)
        return data

    def _assign_token(self, token: str, data: Dict[str, Any]) -> None:
        """Определяет тип токена и сохраняет его в словарь свойств."""
        if self.recognizer.is_int(token):
            size_val = int(token)
            if size_val < 0:
                raise InvalidPropertyError("Размер файла не может быть отрицательным")
            data["size"] = size_val
        elif self.recognizer.is_date(token):
            data["date"] = self.recognizer.parse_date(token)
        elif self.recognizer.is_time(token):
            data["time"] = self.recognizer.parse_time(token)
        elif self.recognizer.is_float(token):
            ratio_val = float(token)
            if not 0.0 <= ratio_val <= 1.0:
                raise InvalidPropertyError("Коэффициент сжатия должен быть от 0.0 до 1.0")
            data["float"] = ratio_val
        else:
            data["strings"].append(token)


class ObjectBuilder:
    """Класс для сборки объектов предметной области из словаря свойств."""

    VALID_TYPES: Tuple[str, ...] = ("Файл", "Аудиофайл", "Архив")

    @staticmethod
    def validate_base(data: Dict[str, Any]) -> None:
        """Проверяет наличие базовых свойств файла."""
        if not data["strings"] or data["date"] is None or data["size"] is None:
            raise InvalidPropertyError("Отсутствуют обязательные свойства базового файла")

    def build(self, obj_type: str, data: Dict[str, Any]) -> FileObject:
        """Создает экземпляр нужного класса на основе типа объекта."""
        if obj_type not in self.VALID_TYPES:
            raise UnknownObjectTypeError(f"Неизвестный тип объекта: {obj_type}")
        self.validate_base(data)
        name = data["strings"][0]
        if obj_type == "Файл":
            return FileObject(name, data["date"], data["size"])
        if obj_type == "Аудиофайл":
            return self._build_audio(name, data)
        return self._build_archive(name, data)

    @staticmethod
    def _build_audio(name: str, data: Dict[str, Any]) -> AudioFile:
        """Создает объект AudioFile."""
        if data["time"] is None:
            raise InvalidPropertyError("Для Аудиофайла не указана длительность")
        return AudioFile(name, data["date"], data["size"], data["time"])

    @staticmethod
    def _build_archive(name: str, data: Dict[str, Any]) -> ArchiveFile:
        """Создает объект ArchiveFile."""
        if data["float"] is None or len(data["strings"]) < 2:
            raise InvalidPropertyError("Для Архива не указаны сжатие или алгоритм")
        return ArchiveFile(
            name, data["date"], data["size"], data["float"], data["strings"][1]
        )


class ObjectParser:
    """Фасад для парсинга объектов из строк и файлов."""

    def __init__(
        self,
        extractor: Optional[PropertyExtractor] = None,
        builder: Optional[ObjectBuilder] = None,
    ) -> None:
        """Инициализирует парсер объектов."""
        self.extractor = extractor or PropertyExtractor()
        self.builder = builder or ObjectBuilder()

    def parse_line(self, line: str) -> FileObject:
        """Разбирает одну строку и возвращает созданный объект."""
        if not line or not line.strip():
            raise ParseError("Пустая строка")
        try:
            parts = shlex.split(line)
        except ValueError as err:
            raise ParseError("Незакрытая кавычка в строке") from err
        data = self.extractor.extract(parts[1:])
        return self.builder.build(parts[0], data)

    def parse_multiline(self, text: str) -> List[FileObject]:
        """Разбирает многострочный текст и возвращает список объектов."""
        results: List[FileObject] = []
        for line in text.splitlines():
            if line.strip():
                results.append(self.parse_line(line))
        return results

    def parse_file(self, file_path: str) -> List[FileObject]:
        """Считывает файл и возвращает список распознанных объектов."""
        with open(file_path, "r", encoding="utf-8") as file:
            return self.parse_multiline(file.read())


if __name__ == "__main__":
    parser = ObjectParser()
    sample_lines = [
        'Файл "report.docx" 2024.05.12 1048576',
        'Аудиофайл "track.flac" 2024.06.01 35000000 04:15',
        'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"',
    ]
    for raw_line in sample_lines:
        print(parser.parse_line(raw_line))