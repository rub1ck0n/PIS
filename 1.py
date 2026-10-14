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


def is_date_token(token):
    return len(token) == 10 and token[4] == "." and token[7] == "."


def is_time_token(token):
    return len(token) == 5 and token[2] == ":"


def is_float_token(token):
    return "." in token and token.replace(".", "", 1).isdigit()


def assign_token_value(token, data):
    if token.isdigit():
        data["size"] = int(token)
    elif is_date_token(token):
        data["date"] = datetime.strptime(token, "%Y.%m.%d").date()
    elif is_time_token(token):
        data["time"] = datetime.strptime(token, "%H:%M").time()
    elif is_float_token(token):
        data["float"] = float(token)
    else:
        data["strings"].append(token)


def extract_properties(tokens):
    data = {"size": 0, "date": None, "time": None, "float": 0.0, "strings": []}
    for token in tokens:
        assign_token_value(token, data)
    return data


def build_object(obj_type, data):
    name = data["strings"][0] if len(data["strings"]) > 0 else ""
    algo = data["strings"][1] if len(data["strings"]) > 1 else ""
    if obj_type == "Файл":
        return FileObject(name, data["date"], data["size"])
    if obj_type == "Аудиофайл":
        return AudioFile(name, data["date"], data["size"], data["time"])
    if obj_type == "Архив":
        return ArchiveFile(name, data["date"], data["size"], data["float"], algo)
    return None


def create_object_from_string(input_string):
    parts = shlex.split(input_string)
    data = extract_properties(parts[1:])
    return build_object(parts[0], data)


def create_objects_from_multiline_string(multiline_string):
    lines = [line.strip() for line in multiline_string.splitlines() if line.strip()]
    objects = [create_object_from_string(line) for line in lines]
    return [obj for obj in objects if obj is not None]


def create_objects_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return create_objects_from_multiline_string(file.read())


def run_demo():
    batch_text = (
        'Файл "report.docx" 2024.05.12 1048576\n'
        'Аудиофайл "track.flac" 2024.06.01 35000000 04:15\n'
        'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"'
    )
    with open("test_data.txt", "w", encoding="utf-8") as f:
        f.write(batch_text)
    for item in create_objects_from_file("test_data.txt"):
        print(item)


if __name__ == "__main__":
    run_demo()