import os
import re

def check_localisation_cyrillic(folder='localisation', output_dir='translator_v2\missing_cyrillic'):
    if not os.path.isdir(folder):
        print(f"Директория '{folder}' не найдена.")
        return

    # Создаём папку для логов, если её нет
    os.makedirs(output_dir, exist_ok=True)

    quote_pattern = re.compile(r'"([^"]*)"')
    file_data = {}

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
                            # 3. Убираем маркеры цвета/форматирования
                            temp = re.sub(r'§[A-Za-z0-9=+!-]*', '', temp)

                            # Оставляем только буквы
                            letters_only = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', temp)
                            if not letters_only:
                                continue

                            valid_contents.append(stripped)

                        if not valid_contents:
                            continue

                        # Пропускаем строки с одиночными заглавными латинскими буквами
                        if all(len(c) == 1 and 'A' <= c <= 'Z' for c in valid_contents):
                            continue

                        # Проверяем наличие кириллицы
                        has_cyrillic = any('\u0400' <= char <= '\u04FF' for content in valid_contents for char in content)
                        if has_cyrillic:
                            continue

                        # Сохраняем: номер строки, оригинал, отфильтрованное содержимое кавычек
                        lines_to_log.append((line_num, original_line, valid_contents))

            except Exception as e:
                print(f"Ошибка чтения файла {filepath}: {e}")
                continue

            if lines_to_log:
                file_data[filepath] = lines_to_log

    # Пути к трём логам
    log1_path = os.path.join(output_dir, 'missing_cyrillic_full.log')
    log2_path = os.path.join(output_dir, 'missing_cyrillic_paths.log')
    log3_path = os.path.join(output_dir, 'missing_cyrillic_contents.log')

    with open(log1_path, 'w', encoding='utf-8') as f1, \
         open(log2_path, 'w', encoding='utf-8') as f2, \
         open(log3_path, 'w', encoding='utf-8') as f3:

        first_block = True
        for filepath, line_data in file_data.items():
            if not first_block:
                f1.write('\n')
                f2.write('\n')
                # Для 3-го лога разделитель не нужен, будет сплошной список
            first_block = False

            # Заголовки только для 1 и 2 логов
            f1.write(f"{filepath}\n")
            f2.write(f"{filepath}\n")

            for line_num, original_line, contents in line_data:
                f1.write(f"{line_num}\n{original_line}\n")
                f2.write(f"{line_num}\n")
                # 3 лог: только текст из кавычек, без путей и номеров
                f3.write(f"{' '.join(contents)}\n")

    print(f"Проверка завершена. Логи сохранены в папке '{output_dir}':")
    print(f" {log1_path} (полный контекст)")
    print(f" {log2_path} (пути и номера строк)")
    print(f" {log3_path} (содержимое в кавычках)")
    
    if not file_data:
        print("Строк без кириллицы не найдено.")

if __name__ == '__main__':
    check_localisation_cyrillic()