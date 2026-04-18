import os
import re

INPUT_DIR = "split_output"
OUTPUT_DIR = "useful_text"

line_pattern = re.compile(r'^\s*[\w\d_]+\s*:\s*["\']')

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in sorted(os.listdir(INPUT_DIR)):
        if not filename.endswith('.txt'):
            continue

        src_path = os.path.join(INPUT_DIR, filename)
        dst_path = os.path.join(OUTPUT_DIR, filename)
        extracted = []

        with open(src_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n\r')
                if line_pattern.match(line):
                    colon_pos = line.find(':')
                    if colon_pos == -1:
                        continue

                    rest = line[colon_pos+1:]
                    stripped_rest = rest.lstrip()
                    if not stripped_rest or stripped_rest[0] not in ('"', "'"):
                        continue

                    quote_char = stripped_rest[0]
                    start_idx = line.find(quote_char, colon_pos) + 1
                    end_idx = line.find(quote_char, start_idx)

                    if end_idx != -1 and end_idx > start_idx:
                        text = line[start_idx:end_idx]
                        # 🔑 Замена одиночного пробела на заглушку
                        if text == " ":
                            text = "*"
                        extracted.append(text)

        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(extracted) + '\n')
        print(f"[OK] Из {filename} извлечено {len(extracted)} текстов.")

if __name__ == "__main__":
    main()