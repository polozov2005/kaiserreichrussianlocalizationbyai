import os
import re

def check_localisation_cyrillic(folder='localisation', output_file='missing_cyrillic3.log'):
    if not os.path.isdir(folder):
        print(f"Директория '{folder}' не найдена.")
        return

    # Паттерн для извлечения текста внутри кавычек
    quote_pattern = re.compile(r'["\']([^"\']*?)["\']')
    cyrillic_pattern = re.compile(r'[А-Яа-яЁё]')
    files_to_log = []

    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for filename in sorted(files):
            if not filename.endswith('.yml') or 'l_russian' not in filename:
                continue

            filepath = os.path.join(root, filename)
            has_missing_cyrillic = False

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Пропускаем комментарии
                        if line.lstrip().startswith('#'):
                            continue
                        # Строка должна содержать двоеточие
                        if ':' not in line:
                            continue

                        quoted_contents = quote_pattern.findall(line)
                        line_flagged = False

                        for content in quoted_contents:
                            stripped = content.strip()
                            if not stripped:
                                continue

                            # Удаляем стандартные маркеры локализации HOI4
                            temp = stripped
                            temp = re.sub(r'\$[^$]*\$', '', temp)
                            temp = re.sub(r'\[[^\]]*\]', '', temp)
                            temp = re.sub(r'£[A-Za-z_]+£?', '', temp)
                            temp = re.sub(r'§[^§]*§!?', '', temp)
                            # Оставляем только буквы
                            temp = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', temp)

                            # Если после очистки не осталось букв, строка пропускается
                            if not temp:
                                continue

                            # Проверяем наличие кириллицы в оригинальном содержимом кавычек
                            if not cyrillic_pattern.search(stripped):
                                line_flagged = True
                                break

                        if line_flagged:
                            has_missing_cyrillic = True
                            break # Найден проблемный участок, дальнейшее чтение файла не требуется
            except Exception as e:
                print(f"Ошибка чтения файла {filepath}: {e}")
                continue

            if has_missing_cyrillic:
                files_to_log.append(filepath)

    # Запись в файл UTF-8 без BOM
    with open(output_file, 'w', encoding='utf-8') as out:
        if files_to_log:
            out.write('\n'.join(files_to_log) + '\n')

    if files_to_log:
        print(f"Проверка завершена. Результаты сохранены в '{output_file}'")
    else:
        print("Проверка завершена. Файлов без кириллицы не найдено.")

if __name__ == '__main__':
    check_localisation_cyrillic()