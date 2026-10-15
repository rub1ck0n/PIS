"""Скрипт для профилирования, динамического анализа памяти и генерации документации."""

import cProfile
import importlib
import io
import pstats
import pydoc
import tracemalloc

main_mod = importlib.import_module("1")
ObjectParser = main_mod.ObjectParser


def run_workload(iterations: int = 5000) -> None:
    """Нагрузочная функция для профилирования и анализа памяти."""
    parser = ObjectParser()
    batch = (
        'Файл "report.docx" 2024.05.12 1048576\n'
        'Аудиофайл "track.flac" 2024.06.01 35000000 04:15\n'
        'Архив "backup.zip" 2024.07.20 5000000 0.65 "DEFLATE"\n'
    )
    for _ in range(iterations):
        parser.parse_multiline(batch)


def run_profiler() -> None:
    """Запускает профилировщик cProfile и выводит топ-10 вызовов по времени."""
    print("=== 1. ПРОФИЛИРОВАНИЕ (cProfile) ===")
    profiler = cProfile.Profile()
    profiler.enable()
    run_workload(5000)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(10)
    print(stream.getvalue())


def run_memory_analysis() -> None:
    """Запускает динамический анализ потребления памяти с помощью tracemalloc."""
    print("=== 2. ДИНАМИЧЕСКИЙ АНАЛИЗ ПАМЯТИ (tracemalloc) ===")
    tracemalloc.start()
    run_workload(2000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Текущее использование памяти: {current / 1024:.2f} КБ")
    print(f"Пиковое использование памяти: {peak / 1024:.2f} КБ\n")


def generate_docs() -> None:
    """Генерирует HTML-документацию по исходному коду с помощью pydoc."""
    print("=== 3. АВТОГЕНЕРАЦИЯ ДОКУМЕНТАЦИИ (pydoc) ===")
    pydoc.writedoc("1")
    print("Документация успешно сгенерирована в файл 1.html")


if __name__ == "__main__":
    run_profiler()
    run_memory_analysis()
    generate_docs()