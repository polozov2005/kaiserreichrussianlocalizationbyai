import requests
import sys
import time

# ================= НАСТРОЙКИ =================
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"          # Ваша модель в Ollama
SOURCE_LANG = "English"     # Исходный язык
TARGET_LANG = "Russian"     # Целевой язык
TIMEOUT_SEC = 120           # Таймаут на строку (локальные LLM могут думать долго)
DELAY_SEC = 0.0             # Задержка между запросами (0 = без задержки)
# =============================================

def translate_line(line: str) -> str:
    """Отправляет строку в Ollama и возвращает только перевод + логирование."""
    if not line.strip():
        return line

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
            "temperature": 0.1,
            "num_predict": 1024,
            "enable_thinking": False
        }
    }

    try:
        print(f"\n📤 Запрос: {line.strip()[:60]}...", file=sys.stderr)
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=TIMEOUT_SEC)
        
        # 🔥 Важно: проверяем статус ДО парсинга JSON
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text}", file=sys.stderr)
            return f"[HTTP_{response.status_code}]"
        
        result = response.json()
        print(f"📦 Сырой ответ Ollama: {result}", file=sys.stderr)  # 🔥 Ключевая строка!
        
        # 🔥 Проверяем наличие поля error (Ollama часто так сообщает об ошибках)
        if "error" in result:
            print(f"❌ Ошибка от Ollama: {result['error']}", file=sys.stderr)
            return f"[OLLAMA_ERROR: {result['error']}]"
        
        # 🔥 Безопасное извлечение контента
        content = result.get("message", {}).get("content", "").strip()
        if not content:
            print(f"⚠️ Пустой content в ответе!", file=sys.stderr)
            return f"[EMPTY_CONTENT]"
            
        print(f"✅ Перевод: {content[:60]}...", file=sys.stderr)
        return content
        
    except requests.exceptions.Timeout:
        print(f"\n⏱️ Таймаут запроса (> {TIMEOUT_SEC} сек)", file=sys.stderr)
        return f"[TIMEOUT]"
    except requests.exceptions.ConnectionError:
        print(f"\n🔌 Не удалось подключиться к Ollama. Запущен ли сервер?", file=sys.stderr)
        return f"[CONNECTION_ERROR]"
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️ Ошибка запроса: {type(e).__name__}: {e}", file=sys.stderr)
        return f"[REQUEST_ERROR]"
    except ValueError as e:  # json.JSONDecodeError наследуется от ValueError
        print(f"\n🧩 Не удалось распарсить JSON: {e}", file=sys.stderr)
        print(f"📄 Тело ответа: {response.text[:200]}", file=sys.stderr)
        return f"[JSON_ERROR]"
    except KeyError as e:
        print(f"\n🔑 Отсутствует ключ в ответе: {e}", file=sys.stderr)
        print(f"📦 Полный ответ: {result}", file=sys.stderr)
        return f"[KEY_ERROR]"
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {type(e).__name__}: {e}", file=sys.stderr)
        return f"[UNKNOWN: {type(e).__name__}]"
    
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