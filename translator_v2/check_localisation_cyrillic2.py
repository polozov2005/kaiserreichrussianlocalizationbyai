import os
import re

def check_localisation_cyrillic(folder='localisation', output_file='missing_cyrillic.log'):
    if not os.path.isdir(folder):
        print(f"Директория '{folder}' не найдена.")
        return

    # Паттерн для извлечения текста внутри одинарных или двойных кавычек
    quote_pattern = re.compile(r'["\']([^"\']*?)["\']')
    file_log = {}

    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for filename in sorted(files):
            # Проверяем расширение и наличие l_russian в имени файла
            if not filename.endswith('.yml') or 'l_russian' not in filename:
                continue

            filepath = os.path.join(root, filename)
            entries = []

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, start=1):
                        quoted_contents = quote_pattern.findall(line)
                        valid_contents = []

                        for content in quoted_contents:
                            stripped = content.strip()
                            
                            # Пропускаем, если в кавычках нет символов
                            if not stripped:
                                continue
                            
                            # Пропускаем, если содержимое полностью окружено $ или []
                            if (stripped.startswith('$') and stripped.endswith('$')) or \
                               (stripped.startswith('[') and stripped.endswith(']')):
                                continue
                                
                            valid_contents.append(content)

                        # Если после фильтрации не осталось контента, строка игнорируется
                        if not valid_contents:
                            continue

                        # Проверяем наличие кириллицы только в отфильтрованном содержимом
                        has_cyrillic = any('\u0400' <= char <= '\u04FF' for content in valid_contents for char in content)

                        # Если кириллицы нет, запоминаем номер строки и оригинал
                        if not has_cyrillic:
                            entries.append((line_num, line.rstrip('\n\r')))
            except Exception as e:
                print(f"Ошибка чтения файла {filepath}: {e}")
                continue

            if entries:
                file_log[filepath] = entries

    # Запись результатов в файл UTF-8 без BOM
    with open(output_file, 'w', encoding='utf-8') as out:
        for filepath, entries in file_log.items():
            out.write(filepath + '\n')
            for line_num, original_line in entries:
                out.write(str(line_num) + '\n')
                out.write(original_line + '\n')

    if file_log:
        print(f"Проверка завершена. Результаты сохранены в '{output_file}'")
    else:
        print("Проверка завершена. Строк без кириллицы не найдено.")

if __name__ == '__main__':
    check_localisation_cyrillic()