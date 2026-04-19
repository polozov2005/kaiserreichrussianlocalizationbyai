import os
import re

def check_localisation_cyrillic(folder='localisation', output_file='missing_cyrillic.log'):
    if not os.path.isdir(folder):
        print(f"Директория '{folder}' не найдена.")
        return

    quote_pattern = re.compile(r'["\']([^"\']*?)["\']')
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
                        quoted_contents = quote_pattern.findall(line)
                        valid_contents = []

                        for content in quoted_contents:
                            stripped = content.strip()
                            if not stripped:
                                continue
                            if (stripped.startswith('$') and stripped.endswith('$')) or \
                               (stripped.startswith('[') and stripped.endswith(']')):
                                continue
                            valid_contents.append(content)

                        if not valid_contents:
                            continue

                        has_cyrillic = any('\u0400' <= char <= '\u04FF' for content in valid_contents for char in content)

                        if not has_cyrillic:
                            lines_to_log.append(line_num)
            except Exception as e:
                print(f"Ошибка чтения файла {filepath}: {e}")
                continue

            if lines_to_log:
                file_log[filepath] = lines_to_log

    with open(output_file, 'w', encoding='utf-8') as out:
        blocks = []
        for filepath, line_numbers in file_log.items():
            block_lines = [filepath] + [' ' + str(n) for n in line_numbers]
            blocks.append('\n'.join(block_lines))
        
        out.write('\n\n'.join(blocks))
        if blocks:
            out.write('\n')

    if file_log:
        print(f"Проверка завершена. Результаты сохранены в '{output_file}'")
    else:
        print("Проверка завершена. Строк без кириллицы не найдено.")

if __name__ == '__main__':
    check_localisation_cyrillic()