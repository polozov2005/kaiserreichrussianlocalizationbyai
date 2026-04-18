import os
from pathlib import Path

# Пути к папке и итоговому файлу
INPUT_DIR = Path("split_input")
OUTPUT_FILE = Path("yml_structure_input.txt")

# 1. Находим все файлы part_*.txt и сортируем их
files = sorted(INPUT_DIR.glob("part_*.txt"))

if not files:
    print("⚠️ Файлы не найдены в папке split_input")
    exit()

parts = []
for file_path in files:
    # Читаем содержимое
    content = file_path.read_text(encoding="utf-8")
    
    # Убираем только завершающие пустые строки (переносы), сохраняя структуру текста
    stripped = content.rstrip()
    
    # Добавляем только если в файле есть полезный текст
    if stripped:
        parts.append(stripped)

# 2. Объединяем блоки одним отступом (пустой строкой)
merged_text = "\n\n".join(parts)

# 3. Записываем результат. Добавляем один \n в конец для корректного формата текстового файла
OUTPUT_FILE.write_text(merged_text + "\n", encoding="utf-8")

print(f"✅ Готово! Объединено {len(parts)} файлов в {OUTPUT_FILE}")