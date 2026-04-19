import os
import re
import glob

# ==========================================================
# Конфигурация
# ==========================================================
TARGET_DIR = 'localisation'
REFERENCE_PATHS = ['ai_localisation', 'old_localisation1', 'old_localisation2']


def has_cyrillic(text: str) -> bool:
    """Проверяет наличие кириллических символов в строке."""
    return bool(re.search(r'[\u0400-\u04FF]', text))


def extract_quoted_text(line: str) -> str:
    """Извлекает текст внутри двойных кавычек."""
    match = re.search(r'"([^"]*)"', line)
    return match.group(1) if match else ""


def parse_key(line: str) -> str | None:
    """Извлекает ключ локализации (текст до первого двоеточия)."""
    if ':' not in line:
        return None
    key = line.split(':', 1)[0].strip()
    # Игнорируем комментарии и пустые ключи
    if not key or key.startswith('#'):
        return None
    return key


def load_references(paths: list[str]) -> dict[str, str]:
    """Загружает строки из справочных файлов в словарь {ключ: строка}.
    Приоритет отдаётся строкам, содержащим кириллицу."""
    ref_dict = {}
    for path in paths:
        if os.path.isfile(path):
            files = [path]
        elif os.path.isdir(path):
            files = glob.glob(os.path.join(path, '**/*.yml'), recursive=True)
        else:
            print(f"Путь не найден: {path}")
            continue

        if not files:
            print(f"Предупреждение: файлы .yml не найдены в {path}")
            continue

        print(f"Сканирование директории: {path} (найдено файлов: {len(files)})")
        
        for fpath in files:
            with open(fpath, 'r', encoding='utf-8', newline='') as f:
                for line in f:
                    key = parse_key(line)
                    if not key:
                        continue
                    
                    line_has_cyrillic = has_cyrillic(extract_quoted_text(line))
                    
                    # Логика приоритета:
                    # 1. Ключ отсутствует -> добавляем
                    # 2. Ключ есть, но новая строка содержит кириллицу -> перезаписываем (перевод важнее)
                    if key not in ref_dict or line_has_cyrillic:
                        ref_dict[key] = line

    print(f"Итог: загружено {len(ref_dict)} уникальных ключей для замены.\n")
    return ref_dict


def process_localisation(target_dir: str, ref_dict: dict[str, str]) -> None:
    """Обрабатывает файлы в целевой директории и выполняет замены."""
    if not os.path.isdir(target_dir):
        print(f"Директория локализации не найдена: {target_dir}")
        return

    files = glob.glob(os.path.join(target_dir, '**/*.yml'), recursive=True)
    if not files:
        print("Файлы .yml не найдены в директории локализации.")
        return

    modified_count = 0
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8', newline='') as f:
            lines = f.readlines()

        new_lines = []
        file_changed = False
        for line in lines:
            key = parse_key(line)
            if key and key in ref_dict:
                ref_line = ref_dict[key]
                # Замена только если в кавычках справочной строки есть кириллица
                if has_cyrillic(extract_quoted_text(ref_line)):
                    # Сохраняем оригинальный символ переноса строки
                    if line.endswith('\r\n'):
                        ending = '\r\n'
                    elif line.endswith('\n'):
                        ending = '\n'
                    else:
                        ending = ''
                    
                    new_line = ref_line.rstrip('\r\n') + ending
                    new_lines.append(new_line)
                    file_changed = True
                    continue
            new_lines.append(line)

        if file_changed:
            # encoding='utf-8' без BOM, newline='' сохраняет исходные окончания строк
            with open(fpath, 'w', encoding='utf-8', newline='') as f:
                f.writelines(new_lines)
            modified_count += 1

    print(f"Обработано файлов: {len(files)} | Изменено: {modified_count}")


if __name__ == '__main__':
    print("Начало обработки файлов локализации...")
    references = load_references(REFERENCE_PATHS)
    process_localisation(TARGET_DIR, references)
    print("Обработка завершена.")