import os
import unittest
from datetime import date, time
import importlib

main_mod = importlib.import_module("1")
ObjectParser = main_mod.ObjectParser
FileObject = main_mod.FileObject
AudioFile = main_mod.AudioFile
ArchiveFile = main_mod.ArchiveFile
ParseError = main_mod.ParseError
UnknownObjectTypeError = main_mod.UnknownObjectTypeError
InvalidPropertyError = main_mod.InvalidPropertyError


class TestObjectParser(unittest.TestCase):
    def setUp(self):
        self.parser = ObjectParser()

    def test_valid_file_object(self):
        line = 'Файл "report.docx" 2024.05.12 1048576'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, FileObject)
        self.assertEqual(obj.name, "report.docx")
        self.assertEqual(obj.creation_date, date(2024, 5, 12))
        self.assertEqual(obj.size, 1048576)
        self.assertIn("report.docx", str(obj))

    def test_valid_audio_file(self):
        line = 'Аудиофайл 35000000 04:15 "track.flac" 2024.06.01'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, AudioFile)
        self.assertEqual(obj.duration, time(4, 15))
        self.assertIn("04:15", str(obj))

    def test_valid_archive_file(self):
        line = 'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"'
        obj = self.parser.parse_line(line)
        self.assertIsInstance(obj, ArchiveFile)
        self.assertAlmostEqual(obj.compression_ratio, 0.65)
        self.assertEqual(obj.algorithm, "DEFLATE")
        self.assertIn("DEFLATE", str(obj))

    def test_empty_string_raises_error(self):
        with self.assertRaises(ParseError):
            self.parser.parse_line("   ")

    def test_unclosed_quote_raises_error(self):
        with self.assertRaises(ParseError):
            self.parser.parse_line('Файл "report.docx 2024.05.12 1024')

    def test_unknown_object_type_raises_error(self):
        with self.assertRaises(UnknownObjectTypeError):
            self.parser.parse_line('Папка "docs" 2024.05.12 1024')

    def test_invalid_date_raises_error(self):
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Файл "report.docx" 2024.15.99 1024')

    def test_invalid_time_raises_error(self):
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Аудиофайл "track.flac" 2024.06.01 1000 29:99')

    def test_missing_base_properties_raises_error(self):
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Файл "report.docx" 2024.05.12')

    def test_missing_audio_duration_raises_error(self):
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Аудиофайл "track.flac" 2024.06.01 35000000')

    def test_missing_archive_properties_raises_error(self):
        with self.assertRaises(InvalidPropertyError):
            self.parser.parse_line('Архив "backup.zip" 2024.07.20 5000000 0.65')

    def test_parse_multiline_and_file(self):
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