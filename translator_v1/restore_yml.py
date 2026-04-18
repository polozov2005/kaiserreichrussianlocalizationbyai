from pathlib import Path

def main():
    input_file = Path('yml_structure_input.txt')
    if not input_file.exists():
        print(f"❌ Файл {input_file} не найден. Положите его в корень проекта.")
        return

    # newline='' отключает автоматическую конвертацию \n <-> \r\n
    # utf-8-sig корректно читает/записывает BOM, который требует HOI4
    with open(input_file, 'r', encoding='utf-8-sig', newline='') as f:
        raw_text = f.read()

    lines = raw_text.splitlines(keepends=True)

    files_data = []
    current_path = None
    content_lines = []

    for line in lines:
        stripped = line.strip()
        # Путь к файлу: без отступов, заканчивается на .yml/.yaml
        if not line.startswith((' ', '\t')) and stripped.endswith(('.yml', '.yaml')):
            if current_path:
                files_data.append((current_path, ''.join(content_lines)))
            current_path = stripped
            content_lines = []
            continue

        # Пропускаем первую пустую строку после пути (это разделитель)
        if current_path is not None and stripped == '' and not content_lines:
            continue

        if current_path is not None:
            content_lines.append(line)

    if current_path:
        files_data.append((current_path, ''.join(content_lines)))

    success, errors, skipped = 0, 0, 0
    for path, content in files_data:
        target = Path(path)
        if not target.exists():
            print(f"⚠️  Пропущен (файл не найден): {path}")
            skipped += 1
            continue

        try:
            # HOI4 требует перенос строки в конце файла. Добавляем \r\n, если его нет.
            if content and not content.endswith(('\n', '\r\n')):
                content += '\r\n'

            # Записываем БЕЗ конвертации переносов и с BOM
            with open(target, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(content)
            print(f"✅ Обновлён: {path}")
            success += 1
        except Exception as e:
            print(f"❌ Ошибка записи {path}: {e}")
            errors += 1

    print(f"\n📊 Итог: обновлено {success}, пропущено {skipped}, ошибок {errors}")

if __name__ == '__main__':
    main()