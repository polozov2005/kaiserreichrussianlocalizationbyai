import os
import re

def check_localisation_cyrillic(folder='localisation', output_file='missing_cyrillic.log'):
    if not os.path.isdir(folder):
        print(f"Директория '{folder}' не найдена.")
        return

    # Стандарт для PDX: текст всегда в двойных кавычках. Игнорируем апострофы внутри.
    quote_pattern = re.compile(r'"([^"]*)"')
    file_log = {}

    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for filename in sorted(files):
            if not filename.endswith('.yml') or 'l_russian' not in filename:
                continue

            filepath = os.path.join(root, filename)
            lines_to_log = []

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, start=1):
                        # Пропускаем комментарии
                        if line.lstrip().startswith('#'):
                            continue
                        # Строка должна содержать двоеточие
                        if ':' not in line:
                            continue

                        original_line = line.rstrip('\n\r')
                        quoted_contents = quote_pattern.findall(line)
                        valid_contents = []

                        for content in quoted_contents:
                            stripped = content.strip()
                            if not stripped:
                                continue

                            # 1. Убираем литеральные переносы
                            temp = stripped.replace('\\n', '').replace('\\r', '')
                            # 2. Убираем переменные, скобки, иконки
                            temp = re.sub(r'\$[^$]*\$', '', temp)          # $VAR$
                            temp = re.sub(r'\[[^\]]*\]', '', temp)         # [KEY]
                            temp = re.sub(r'£[A-Za-z_]+£?', '', temp)      # £icon£
                            # 3. Убираем ВСЕ маркеры цвета § (самый надёжный способ для PDX)
                            temp = temp.replace('§', '')

                            # Оставляем только буквы (латиница + кириллица)
                            letters_only = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', temp)

                            # Если после очистки не осталось букв → пропускаем
                            if not letters_only:
                                continue

                            valid_contents.append(stripped)

                        if not valid_contents:
                            continue

                        # Проверяем наличие кириллицы в отфильтрованном содержимом
                        has_cyrillic = any('\u0400' <= char <= '\u04FF' for content in valid_contents for char in content)

                        # Явное условие: строки С кириллицей пропускаем, в лог попадают ТОЛЬКО строки БЕЗ кириллицы
                        if has_cyrillic:
                            continue

                        lines_to_log.append((line_num, original_line))
                        
            except Exception as e:
                print(f"Ошибка чтения файла {filepath}: {e}")
                continue

            if lines_to_log:
                file_log[filepath] = lines_to_log

    # Запись в UTF-8 без BOM
    with open(output_file, 'w', encoding='utf-8') as out:
        first_block = True
        for filepath, line_data in file_log.items():
            if not first_block:
                out.write('\n')
            out.write(f"{filepath}\n")
            for line_num, original_line in line_data:
                out.write(f"{line_num}\n")
                out.write(f"{original_line}\n")
            first_block = False

    if file_log:
        print(f"Проверка завершена. Результаты сохранены в '{output_file}'")
    else:
        print("Проверка завершена. Строк без кириллицы не найдено.")

if __name__ == '__main__':
    check_localisation_cyrillic()