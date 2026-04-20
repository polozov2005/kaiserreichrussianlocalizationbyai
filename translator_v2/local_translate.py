import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# === НАСТРОЙКИ ===
INPUT_FILE  = "source.txt"
OUTPUT_FILE = "translated.txt"
SRC_LANG    = "en"
TGT_LANG    = "ru"
MODEL_NAME  = f"Helsinki-NLP/opus-mt-{SRC_LANG}-{TGT_LANG}"
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"
MAX_LENGTH  = 512  # Макс. длина токенов на вход
BATCH_SIZE  = 1    # Можно увеличить до 4-8, если хватает памяти
# =================

def get_processed_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def main():
    print(f"📦 Загрузка модели {MODEL_NAME} на {DEVICE}...")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)
    model.eval()  # Режим инференса

    start_line = get_processed_lines(OUTPUT_FILE)
    print(f"▶️ Возобновляем со строки {start_line + 1} (уже готово: {start_line})")

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, \
         open(OUTPUT_FILE, "a", encoding="utf-8") as fout:

        batch = []
        batch_indices = []

        for i, line in enumerate(fin, 1):
            if i <= start_line:
                continue

            original_line = line.rstrip("\n")
            
            # Пропускаем пустые строки
            if not original_line.strip():
                fout.write("\n")
                continue

            batch.append(original_line)
            batch_indices.append(i)

            # Обрабатываем батч
            if len(batch) >= BATCH_SIZE:
                try:
                    inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=MAX_LENGTH).to(DEVICE)
                    with torch.no_grad():
                        generated = model.generate(
                            inputs["input_ids"],
                            attention_mask=inputs["attention_mask"],
                            max_length=MAX_LENGTH,
                            num_beams=2,  # Небольшой beam search для качества
                            early_stopping=True
                        )
                    translated = tokenizer.batch_decode(generated, skip_special_tokens=True)
                    
                    for idx, text in zip(batch_indices, translated):
                        fout.write(text.strip() + "\n")
                        if idx % 100 == 0:
                            print(f"🔄 Строка {idx} обработана...")
                            
                except Exception as e:
                    print(f"⚠️ Ошибка на строках {batch_indices}: {e}")
                    for _ in batch:
                        fout.write("[TRANSLATION_ERROR]\n")
                
                # Очищаем батч
                batch = []
                batch_indices = []

        # Обрабатываем остаток
        if batch:
            try:
                inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=MAX_LENGTH).to(DEVICE)
                with torch.no_grad():
                    generated = model.generate(
                        inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        max_length=MAX_LENGTH,
                        num_beams=2,
                        early_stopping=True
                    )
                translated = tokenizer.batch_decode(generated, skip_special_tokens=True)
                for text in translated:
                    fout.write(text.strip() + "\n")
            except Exception as e:
                print(f"⚠️ Ошибка в финальном батче: {e}")
                for _ in batch:
                    fout.write("[TRANSLATION_ERROR]\n")

    print("\n✅ Перевод завершён.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено вручную. Файл сохранён. Запустите снова для продолжения.")