import os
from pathlib import Path

def process_directory(current_path, depth, lines):
    """Рекурсивный обход папок и сбор структуры."""
    # Сортируем: сначала папки, потом файлы, по алфавиту (без учёта регистра)
    items = sorted(
        current_path.iterdir(),
        key=lambda x: (not x.is_dir(), x.name.lower())
    )

    for item in items:
        # Пропускаем скрытые папки/файлы (начинаются с точки)
        if item.name.startswith('.'):
            continue

        if item.is_dir():
            lines.append('\t' * depth + item.name)
            process_directory(item, depth + 1, lines)
        elif item.suffix.lower() in ['.yml', '.yaml']:
            file_indent = '\t' * (depth + 1)
            lines.append(f"{file_indent}{item.name}")
            try:
                # Читаем содержимое, убираем лишние переводы строк в конце файла
                content = item.read_text(encoding='utf-8').rstrip('\n')
                lines.append(content)
            except Exception as e:
                lines.append(f"[Ошибка чтения: {e}]")
            # Пустая строка для визуального разделения между файлами
            lines.append("")

def main():
    # '.' означает текущую рабочую директорию (корень проекта)
    root_dir = Path('.')
    output_file = Path('yml_structure_output.txt')

    all_lines = []

    # Обрабатываем содержимое корневой папки
    root_items = sorted(
        root_dir.iterdir(),
        key=lambda x: (not x.is_dir(), x.name.lower())
    )

    for item in root_items:
        if item.name.startswith('.'):
            continue

        if item.is_dir():
            all_lines.append(item.name)
            process_directory(item, depth=1, lines=all_lines)
        elif item.suffix.lower() in ['.yml', '.yaml']:
            all_lines.append(item.name)
            try:
                content = item.read_text(encoding='utf-8').rstrip('\n')
                all_lines.append(content)
            except Exception as e:
                all_lines.append(f"[Ошибка чтения: {e}]")
            all_lines.append("")

    # Записываем результат в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines))

    print(f"✅ Готово! Файл {output_file} создан в корне проекта.")

if __name__ == '__main__':
    main()