import shlex
from dataclasses import dataclass
from datetime import date, datetime, time


class ParseError(Exception):
    pass


class UnknownObjectTypeError(ParseError):
    pass


class InvalidPropertyError(ParseError):
    pass


@dataclass
class FileObject:
    name: str
    creation_date: date
    size: int

    def __str__(self):
        date_str = self.creation_date.strftime("%Y.%m.%d")
        return f"Файл: '{self.name}', Дата создания: {date_str}, Размер: {self.size} байт"


@dataclass
class AudioFile(FileObject):
    duration: time

    def __str__(self):
        base_str = super().__str__()
        time_str = self.duration.strftime("%H:%M")
        return f"Аудиофайл -> {base_str}, Длительность: {time_str}"


@dataclass
class ArchiveFile(FileObject):
    compression_ratio: float
    algorithm: str

    def __str__(self):
        base_str = super().__str__()
        return f"Архив -> {base_str}, Сжатие: {self.compression_ratio}, Алгоритм: '{self.algorithm}'"


class TokenRecognizer:
    @staticmethod
    def is_date(token):
        return len(token) == 10 and token[4] == "." and token[7] == "."

    @staticmethod
    def is_time(token):
        return len(token) == 5 and token[2] == ":"

    @staticmethod
    def is_float(token):
        return "." in token and token.replace(".", "", 1).isdigit()

    @staticmethod
    def parse_date(token):
        try:
            return datetime.strptime(token, "%Y.%m.%d").date()
        except ValueError as err:
            raise InvalidPropertyError(f"Некорректная дата: {token}") from err

    @staticmethod
    def parse_time(token):
        try:
            return datetime.strptime(token, "%H:%M").time()
        except ValueError as err:
            raise InvalidPropertyError(f"Некорректное время: {token}") from err


class PropertyExtractor:
    def __init__(self, recognizer=None):
        self.recognizer = recognizer or TokenRecognizer()

    def extract(self, tokens):
        data = {"size": None, "date": None, "time": None, "float": None, "strings": []}
        for token in tokens:
            self._assign_token(token, data)
        return data

    def _assign_token(self, token, data):
        if token.isdigit():
            data["size"] = int(token)
        elif self.recognizer.is_date(token):
            data["date"] = self.recognizer.parse_date(token)
        elif self.recognizer.is_time(token):
            data["time"] = self.recognizer.parse_time(token)
        elif self.recognizer.is_float(token):
            data["float"] = float(token)
        else:
            data["strings"].append(token)


class ObjectBuilder:
    @staticmethod
    def validate_base(data):
        if not data["strings"] or data["date"] is None or data["size"] is None:
            raise InvalidPropertyError("Отсутствуют обязательные свойства базового файла")

    def build(self, obj_type, data):
        if obj_type not in ("Файл", "Аудиофайл", "Архив"):
            raise UnknownObjectTypeError(f"Неизвестный тип объекта: {obj_type}")
        self.validate_base(data)
        name = data["strings"][0]
        if obj_type == "Файл":
            return FileObject(name, data["date"], data["size"])
        if obj_type == "Аудиофайл":
            return self._build_audio(name, data)
        return self._build_archive(name, data)

    @staticmethod
    def _build_audio(name, data):
        if data["time"] is None:
            raise InvalidPropertyError("Для Аудиофайла не указана длительность")
        return AudioFile(name, data["date"], data["size"], data["time"])

    @staticmethod
    def _build_archive(name, data):
        if data["float"] is None or len(data["strings"]) < 2:
            raise InvalidPropertyError("Для Архива не указаны сжатие или алгоритм")
        return ArchiveFile(name, data["date"], data["size"], data["float"], data["strings"][1])


class ObjectParser:
    def __init__(self, extractor=None, builder=None):
        self.extractor = extractor or PropertyExtractor()
        self.builder = builder or ObjectBuilder()

    def parse_line(self, line):
        if not line or not line.strip():
            raise ParseError("Пустая строка")
        try:
            parts = shlex.split(line)
        except ValueError as err:
            raise ParseError("Незакрытая кавычка в строке") from err
        data = self.extractor.extract(parts[1:])
        return self.builder.build(parts[0], data)

    def parse_multiline(self, text):
        results = []
        for line in text.splitlines():
            if line.strip():
                results.append(self.parse_line(line))
        return results

    def parse_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return self.parse_multiline(file.read())


if __name__ == "__main__":
    parser = ObjectParser()
    sample_lines = [
        'Файл "report.docx" 2024.05.12 1048576',
        'Аудиофайл "track.flac" 2024.06.01 35000000 04:15',
        'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"',
        'НеизвестныйТип "test.txt" 2024.05.12 100',
        'Файл "broken_date.txt" 2024.99.99 100',
        'Файл "unclosed_quote.txt 2024.05.12 100',
    ]

    for raw_line in sample_lines:
        try:
            obj = parser.parse_line(raw_line)
            print(f"[OK] {obj}")
        except ParseError as error:
            print(f"[ОШИБКА] Строка '{raw_line}' -> {error}")