import os

file_path = r"C:\Users\Globa\Documents\Paradox Interactive\Hearts of Iron IV\mod\KaiserreichRussianLocalization\translator_v2\missing_cyrillic\missing_cyrillic_contents.log"

if not os.path.exists(file_path):
    print("❌ Файл не найден. Проверьте указанный путь.")
else:
    # HOI4 моды часто используют UTF-8, но иногда CP1251. Пробуем оба варианта.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    if not lines:
        print("⚠️ Файл пуст.")
    else:
        # Убираем символы переноса строки (\n, \r) для точного подсчёта видимых символов
        lengths = [len(line.rstrip('\n\r')) for line in lines]
        
        max_length = max(lengths)
        avg_length = sum(lengths) / len(lengths)

        print(f"📊 Результаты анализа:")
        print(f"   • Всего строк: {len(lines)}")
        print(f"   • Максимальная длина строки: {max_length}")
        print(f"   • Средняя длина строки: {avg_length:.2f}")