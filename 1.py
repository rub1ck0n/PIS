import shlex
from dataclasses import dataclass
from datetime import date, datetime, time


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


def create_object_from_string(input_string):
    parts = shlex.split(input_string)
    obj_type = parts[0]

    name = ""
    creation_date = None
    size = 0
    duration = None
    compression_ratio = 0.0
    algorithm = ""

    for part in parts[1:]:
        if part.isdigit():
            size = int(part)
        elif len(part) == 10 and part[4] == "." and part[7] == ".":
            creation_date = datetime.strptime(part, "%Y.%m.%d").date()
        elif len(part) == 5 and part[2] == ":":
            duration = datetime.strptime(part, "%H:%M").time()
        elif "." in part and part.replace(".", "", 1).isdigit():
            compression_ratio = float(part)
        else:
            if not name:
                name = part
            else:
                algorithm = part

    if obj_type == "Файл":
        return FileObject(name, creation_date, size)
    elif obj_type == "Аудиофайл":
        return AudioFile(name, creation_date, size, duration)
    elif obj_type == "Архив":
        return ArchiveFile(name, creation_date, size, compression_ratio, algorithm)
    return None


if __name__ == "__main__":
    test_strings = [
        'Файл "report.docx" 2024.05.12 1048576',
        'Аудиофайл "track.flac" 2024.06.01 35000000 04:15',
        'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"',
    ]

    for line in test_strings:
        obj = create_object_from_string(line)
        print(obj)