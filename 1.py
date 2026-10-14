import shlex
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class FileObject:
    name: str
    creation_date: date
    size: int

    def __str__(self):
        date_str = self.creation_date.strftime("%Y.%m.%d")
        return f"Файл: '{self.name}', Дата создания: {date_str}, Размер: {self.size} байт"


def create_file_from_string(input_string):
    parts = shlex.split(input_string)
    obj_type = parts[0]

    if obj_type != "Файл":
        return None

    name = ""
    creation_date = None
    size = 0

    for part in parts[1:]:
        if part.isdigit():
            size = int(part)
        elif len(part) == 10 and part[4] == "." and part[7] == ".":
            creation_date = datetime.strptime(part, "%Y.%m.%d").date()
        else:
            name = part

    return FileObject(name, creation_date, size)


if __name__ == "__main__":
    test_strings = [
        'Файл "report.docx" 2024.05.12 1048576',
        'Файл    "моя курсовая работа.pdf"    2023.11.01     524288',
        'Файл 2022.01.15 "archive.zip" 999999',
        'Файл 4096 2024.10.10 "script.py"',
    ]

    for line in test_strings:
        file_obj = create_file_from_string(line)
        print(file_obj)