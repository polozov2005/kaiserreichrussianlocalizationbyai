import os
import re

# === НАСТРОЙКИ ===
INPUT_FILE = 'yml_structure_input.txt'
MAX_CHARS = 131072
OUTPUT_DIR = 'split_output'  # Папка, куда будут сохранены результаты
# =================

def parse_blocks(text):
    """Разбивает исходный текст на атомарные блоки по строкам-путям к .yml файлам."""
    blocks = []
    current_block = []
    # Строка считается началом нового блока, если:
    # 1. Начинается без отступа (первый символ не пробел/таб)
    # 2. Заканчивается на .yml (игнорируя возможные пробелы в конце строки)
    path_pattern = re.compile(r'^[^\s].*\.yml\s*$')

    for line in text.splitlines(keepends=True):
        if path_pattern.match(line) and current_block:
            blocks.append(''.join(current_block))
            current_block = [line]
        else:
            current_block.append(line)

    if current_block:
        blocks.append(''.join(current_block))
    return blocks

def pack_blocks_into_files(blocks):
    """Жадно упаковывает блоки в части, строго соблюдая лимит символов."""
    parts = []
    current_part = ""

    for block in blocks:
        block_len = len(block)
        
        # Если один блок сам по себе больше лимита
        if block_len > MAX_CHARS:
            print(f"⚠️ Внимание: Блок начинается с '{block.splitlines()[0][:30]}...' "
                  f"и имеет {block_len} симв. (превышает лимит). "
                  f"Будет сохранён в отдельный файл.")
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(block)
            continue

        # Проверяем, влезет ли блок в текущую часть
        if len(current_part) + block_len <= MAX_CHARS:
            current_part += block
        else:
            # Лимит достигнут: сохраняем текущую часть и начинаем новую
            parts.append(current_part)
            current_part = block

    if current_part:
        parts.append(current_part)

    return parts

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Ошибка: файл '{INPUT_FILE}' не найден в текущей директории.")
        return

    print(f"📖 Чтение {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = parse_blocks(content)
    print(f"📦 Найдено блоков: {len(blocks)}")

    parts = pack_blocks_into_files(blocks)

    # Создаём папку для результатов
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Создана/используется папка: ./{OUTPUT_DIR}/")

    print(f"📝 Запись частей (лимит: {MAX_CHARS} симв.)...")
    for i, part in enumerate(parts, 1):
        out_name = f"part_{i:03d}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(part)
            
        # Подсчёт блоков внутри части (примерный, по количеству заголовков .yml)
        block_count = sum(1 for line in part.splitlines() if re.match(r'^[^\s].*\.yml\s*$', line))
        print(f"✅ {out_name} | Символов: {len(part):>6} | Блоков: {block_count}")

    total_chars = sum(len(p) for p in parts)
    print(f"\n✨ Готово! Всего частей: {len(parts)} | Общий объём: {total_chars} симв.")

if __name__ == "__main__":
    main()