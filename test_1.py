"""Модульные тесты для проверки парсера объектов."""

import importlib
import os
import unittest
from datetime import date, time

main_mod = importlib.import_module("1")
ObjectParser = main_mod.ObjectParser
FileObject = main_mod.FileObject
AudioFile = main_mod.AudioFile
ArchiveFile = main_mod.ArchiveFile
ParseError = main_mod.ParseError
UnknownObjectTypeError = main_mod.UnknownObjectTypeError
InvalidPropertyError = main_mod.InvalidPropertyError


class TestObjectParser(unittest.TestCase):
    """Набор модульных тестов для класса ObjectParser."""

    def setUp(self) -> None:
        """Инициализация парсера перед каждым тестом."""
        self.parser = ObjectParser()

    def test_valid_file_object(self) -> None:
        """Проверка создания базового объекта Файл."""
        line = 'Файл "report.docx" 2024.05.12 1048576'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, FileObject)
        self.assertEqual(obj.name, "report.docx")
        self.assertEqual(obj.creation_date, date(2024, 5, 12))
        self.assertEqual(obj.size, 1048576)
        self.assertIn("report.docx", str(obj))

    def test_valid_audio_file(self) -> None:
        """Проверка создания объекта Аудиофайл с произвольным порядком свойств."""
        line = 'Аудиофайл 35000000 04:15 "track.flac" 2024.06.01'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, AudioFile)
        self.assertEqual(obj.duration, time(4, 15))
        self.assertIn("04:15", str(obj))

    def test_valid_archive_file(self) -> None:
        """Проверка создания объекта Архив."""
        line = 'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, ArchiveFile)
        self.assertAlmostEqual(obj.compression_ratio, 0.65)
        self.assertEqual(obj.algorithm, "DEFLATE")
        self.assertIn("DEFLATE", str(obj))

    def test_empty_string_raises_error(self) -> None:
        """Проверка выброса исключения при пустой строке."""
        with self.assertRaises(ParseError):
            self.parser.parse_line("   ")

    def test_unclosed_quote_raises_error(self) -> None:
        """Проверка выброса исключения при незакрытой кавычке."""
        with self.assertRaises(ParseError):
            self.parser.parse_line('Файл "report.docx 2024.05.12 1024')

    def test_unknown_object_type_raises_error(self) -> None:
        """Проверка выброса исключения при неизвестном типе объекта."""
        with self.assertRaises(UnknownObjectTypeError):
            self.parser.parse_line('Папка "docs" 2024.05.12 1024')

    def test_invalid_date_raises_error(self) -> None:
        """Проверка выброса исключения при некорректной дате."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Файл "report.docx" 2024.15.99 1024')

    def test_invalid_time_raises_error(self) -> None:
        """Проверка выброса исключения при некорректном времени."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Аудиофайл "track.flac" 2024.06.01 1000 29:99')

    def test_negative_file_size_raises_error(self) -> None:
        """Проверка выброса исключения при отрицательном размере файла."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Файл "report.docx" 2024.05.12 -500')

    def test_invalid_compression_ratio_raises_error(self) -> None:
        """Проверка выброса исключения при коэффициенте сжатия вне диапазона [0, 1]."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Архив "backup.zip" 2024.07.20 5000 1.85 "DEFLATE"')

    def test_missing_base_properties_raises_error(self) -> None:
        """Проверка выброса исключения при отсутствии размера файла."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Файл "report.docx" 2024.05.12')

    def test_missing_audio_duration_raises_error(self) -> None:
        """Проверка выброса исключения при отсутствии длительности аудиофайла."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Аудиофайл "track.flac" 2024.06.01 35000000')

    def test_missing_archive_properties_raises_error(self) -> None:
        """Проверка выброса исключения при отсутствии алгоритма сжатия архива."""
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Архив "backup.zip" 2024.07.20 5000000 0.65')

    def test_parse_multiline_and_file(self) -> None:
        """Проверка чтения нескольких объектов из текстового файла."""
        text = (
            'Файл "a.txt" 2024.01.01 100\n'
            'Аудиофайл "b.mp3" 2024.01.02 200 03:30\n'
        )
        temp_file = "temp_test.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text)
        try:
            objects = self.parser.parse_file(temp_file)
            self.assertEqual(len(objects), 2)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    unittest.main()