from pathlib import Path

def main():
    root_dir = Path('.')
    output_file = Path('yml_structure_output.txt')
    all_lines = []

    # 1. Собираем все yml и yaml файлы рекурсивно
    yml_files = list(root_dir.rglob('*.yml')) + list(root_dir.rglob('*.yaml'))

    # 2. Игнорируем скрытые папки и файлы (начинаются с точки)
    yml_files = [f for f in yml_files if not any(part.startswith('.') for part in f.parts)]

    # 3. Сортируем по пути для предсказуемого порядка вывода
    yml_files.sort(key=lambda x: str(x.relative_to(root_dir)).lower())

    for file_path in yml_files:
        # Получаем путь от корня проекта и меняем / на \
        rel_path = str(file_path.relative_to(root_dir)).replace('/', '\\')
        all_lines.append(rel_path)
        all_lines.append('')  # [отступ]

        try:
            # utf-8-sig автоматически убирает BOM, если он есть
            content = file_path.read_text(encoding='utf-8-sig').rstrip('\n')
            all_lines.append(content)
        except Exception as e:
            all_lines.append(f"[Ошибка чтения: {e}]")

        all_lines.append('')  # [отступ]

    # Убираем пустые строки в самом конце файла
    while all_lines and all_lines[-1].strip() == '':
        all_lines.pop()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines))

    print(f"✅ Готово! Файл {output_file} создан в корне проекта.")

if __name__ == '__main__':
    main()