import requests
import sys
import time
import re

# ================= НАСТРОЙКИ =================
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"          # Модель в Ollama
SOURCE_LANG = "English"            # Исходный язык
TARGET_LANG = "Russian"            # Целевой язык
TIMEOUT_SEC = 120                  # Таймаут на строку
DELAY_SEC = 0.0                    # Задержка между запросами
# =============================================

def fix_hoi4_tags(text: str) -> str:
    """Восстанавливает сломанные теги § после перевода (фолбэк)."""
    # Исправляем "Секция X" → "§X" (частая ошибка перевода)
    text = re.sub(r'Секция ([YGLHRT!WPBNCS])', r'§\1', text, flags=re.IGNORECASE)
    # Исправляем двойные экранированные переносы
    text = text.replace('\\n', '\n')
    return text

def translate_line(line: str) -> str:
    """Отправляет строку в Ollama и возвращает перевод."""
    if not line.strip():
        return line

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a professional game localizer for Hearts of Iron IV mods. "
                    f"Translate the following text from {SOURCE_LANG} to {TARGET_LANG}.\n\n"
                    f"🔒 STRICT RULES:\n"
                    f"1. PRESERVE ALL game markup tags EXACTLY: §Y, §G, §R, §H, §L, §!, §P, §W, §N, §B, §C, §S, etc.\n"
                    f"2. PRESERVE ALL variables and keys: [FROM.GetLeader], $event.key$, [ROOT.GetName], etc.\n"
                    f"3. PRESERVE line breaks: \\n must stay as \\n (do not translate, escape, or remove them).\n"
                    f"4. Do NOT translate proper names, titles, or game-specific terms unless they have established Russian equivalents.\n"
                    f"5. Return ONLY the translated text — no explanations, no markdown, no quotes, no extra formatting.\n\n"
                    f"Example input: \"§YBorn:§! §LMay 18th§! in [FROM.GetCapital]\"\n"
                    f"Example output: \"§YРождён:§! §L18 мая§! в [FROM.GetCapital]\""
                )
            },
            {"role": "user", "content": line.strip()}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2048,
            # enable_thinking удалён для совместимости
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=TIMEOUT_SEC)
        
        if response.status_code != 200:
            print(f"\n❌ HTTP {response.status_code}", file=sys.stderr)
            return f"[HTTP_{response.status_code}]"
        
        result = response.json()
        
        if "error" in result:
            print(f"\n❌ Ollama error: {result['error']}", file=sys.stderr)
            return f"[OLLAMA_ERROR]"
        
        content = result.get("message", {}).get("content", "").strip()
        
        if not content:
            print(f"\n⚠️ Пустой ответ", file=sys.stderr)
            return f"[EMPTY]"
        
        # 🔧 Пост-обработка: чиним теги и переносы
        content = fix_hoi4_tags(content)
        
        return content
        
    except requests.exceptions.Timeout:
        print(f"\n⏱️ Таймаут", file=sys.stderr)
        return f"[TIMEOUT]"
    except requests.exceptions.ConnectionError:
        print(f"\n🔌 Нет соединения с Ollama", file=sys.stderr)
        return f"[CONNECTION_ERROR]"
    except Exception as e:
        print(f"\n💥 Ошибка: {type(e).__name__}", file=sys.stderr)
        return f"[ERROR]"

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
                print(f"🔄 Строка {i}/{total}", end="\r")
                translated = translate_line(line)
                f_out.write(translated + "\n")
                f_out.flush()  # 🔥 Гарантирует запись на диск при сбое
                if DELAY_SEC > 0:
                    time.sleep(DELAY_SEC)

            print(f"\n✅ Готово! Перевод сохранён в {output_file}")

    except FileNotFoundError:
        print(f"❌ Файл {input_file} не найден.", file=sys.stderr)
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()