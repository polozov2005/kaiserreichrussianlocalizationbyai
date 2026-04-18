import os
import re

INPUT_DIR = "split_output"
USEFUL_DIR = "useful_text"
OUTPUT_DIR = "split_input"

line_pattern = re.compile(r'^\s*[\w\d_]+\s*:\s*["\']')

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in sorted(os.listdir(INPUT_DIR)):
        if not filename.endswith('.txt'):
            continue

        src_path = os.path.join(INPUT_DIR, filename)
        useful_path = os.path.join(USEFUL_DIR, filename)
        dst_path = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(useful_path):
            print(f"[WARN] Файл {useful_path} не найден. Пропуск.")
            continue

        # Читаем строки, удаляя только переносы. 
        # Фильтруем полностью пустые строки (length 0), чтобы избежать сдвига из-за лишних Enter в редакторе.
        with open(useful_path, 'r', encoding='utf-8') as f:
            useful_texts = [line.rstrip('\n\r') for line in f if line.rstrip('\n\r') != ""]
        useful_iter = iter(useful_texts)

        with open(src_path, 'r', encoding='utf-8') as f_in, \
             open(dst_path, 'w', encoding='utf-8') as f_out:
            count = 0
            for line in f_in:
                line_stripped = line.rstrip('\n\r')
                if line_pattern.match(line_stripped):
                    colon_pos = line_stripped.find(':')
                    if colon_pos == -1:
                        f_out.write(line_stripped + '\n')
                        continue

                    rest = line_stripped[colon_pos+1:]
                    stripped_rest = rest.lstrip()
                    if stripped_rest and stripped_rest[0] in ('"', "'"):
                        quote_char = stripped_rest[0]
                        start_idx = line_stripped.find(quote_char, colon_pos) + 1
                        end_idx = line_stripped.find(quote_char, start_idx)

                        if end_idx != -1:
                            current_value = line_stripped[start_idx:end_idx]

                            if current_value == "":
                                # Пропускаем пустые кавычки "", не расходуем строку из useful_text
                                pass
                            else:
                                try:
                                    placeholder_text = next(useful_iter)
                                    # 🔑 Восстановление пробела из заглушки
                                    new_text = " " if placeholder_text == "*" else placeholder_text
                                    line_stripped = line_stripped[:start_idx] + new_text + line_stripped[end_idx:]
                                    count += 1
                                except StopIteration:
                                    print(f"[WARN] В {filename} закончились строки в useful_text.")

                f_out.write(line_stripped + '\n')
        print(f"[OK] В {filename} восстановлено {count} текстов.")

if __name__ == "__main__":
    main()