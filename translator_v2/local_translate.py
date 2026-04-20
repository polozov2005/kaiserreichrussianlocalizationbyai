import requests
import sys
import time

# ================= НАСТРОЙКИ =================
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL = "Qwen3.5:9b"          # Ваша модель в Ollama
SOURCE_LANG = "English"     # Исходный язык
TARGET_LANG = "Russian"     # Целевой язык
TIMEOUT_SEC = 120           # Таймаут на строку (локальные LLM могут думать долго)
DELAY_SEC = 0.0             # Задержка между запросами (0 = без задержки)
# =============================================

def translate_line(line: str) -> str:
    """Отправляет строку в Ollama и возвращает только перевод."""
    if not line.strip():
        return line  # Сохраняем пустые строки без изменений

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a precise translator. Translate the following text "
                    f"from {SOURCE_LANG} to {TARGET_LANG}. "
                    f"Return ONLY the translated text. Do not add explanations, "
                    f"quotes, markdown, or any extra formatting."
                )
            },
            {"role": "user", "content": line.strip()}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,  # Низкая температура для стабильных переводов
            "num_predict": 1024  # Макс. длина ответа
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=TIMEOUT_SEC)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ Ошибка запроса к Ollama: {e}", file=sys.stderr)
        return f"[TRANSLATION_ERROR: {line.strip()}]"

def main():
    input_file = "source.txt"
    output_file = "translated.txt"

    print(f"📖 Чтение {input_file}...")
    try:
        with open(input_file, "r", encoding="utf-8") as f_in, \
             open(output_file, "w", encoding="utf-8") as f_out:

            lines = f_in.readlines()
            total = len(lines)

            for i, line in enumerate(lines, 1):
                print(f"🔄 Обработка строки {i}/{total}...", end="\r")
                translated = translate_line(line)
                f_out.write(translated + "\n")
                if DELAY_SEC > 0:
                    time.sleep(DELAY_SEC)

            print(f"\n✅ Готово! Перевод сохранён в {output_file}")

    except FileNotFoundError:
        print(f"❌ Файл {input_file} не найден в текущей директории.")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()