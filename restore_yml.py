from pathlib import Path

def main():
    input_file = Path('yml_structure_input.txt')
    if not input_file.exists():
        print(f"❌ Файл {input_file} не найден. Убедитесь, что он лежит в корне проекта.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    files_data = []
    current_path = None
    content_lines = []
    state = 'expect_path'  # Состояния: expect_path, skip_separator, reading_content

    for line in lines:
        if state == 'expect_path':
            # Ищем строку с путем (без отступа, заканчивается на .yml/.yaml)
            if not line.startswith((' ', '\t', '#')) and line.strip().endswith(('.yml', '.yaml')):
                current_path = line.strip()
                state = 'skip_separator'
            continue

        if state == 'skip_separator':
            # Пропускаем одну пустую строку-разделитель после пути
            state = 'reading_content'
            content_lines = []
            continue

        if state == 'reading_content':
            # Проверяем, не началась ли новая запись файла
            if not line.startswith((' ', '\t', '#')) and line.strip().endswith(('.yml', '.yaml')):
                # Сохраняем предыдущий файл (убираем лишний пустой разделитель в конце контента)
                while content_lines and content_lines[-1] == '':
                    content_lines.pop()
                files_data.append((current_path, '\n'.join(content_lines)))

                # Начинаем парсинг нового файла
                current_path = line.strip()
                state = 'skip_separator'
            else:
                content_lines.append(line)

    # Не забываем сохранить последний файл из списка
    if current_path is not None:
        while content_lines and content_lines[-1] == '':
            content_lines.pop()
        files_data.append((current_path, '\n'.join(content_lines)))

    # Перезаписываем файлы
    success_count = 0
    error_count = 0
    not_found_count = 0

    for path, content in files_data:
        target = Path(path)
        if not target.exists():
            print(f"⚠️  Файл не найден: {path}")
            not_found_count += 1
            continue
        try:
            target.write_text(content, encoding='utf-8')
            print(f"✅ Обновлён: {path}")
            success_count += 1
        except Exception as e:
            print(f"❌ Ошибка записи {path}: {e}")
            error_count += 1

    print(f"\n📊 Итог: обновлено {success_count}, не найдено {not_found_count}, ошибок {error_count}")

if __name__ == '__main__':
    main()