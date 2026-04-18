import os

def find_first_difference(file1_path, file2_path):
    # Проверяем существование файлов
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("❌ Один или оба файла не найдены.")
        return

    with open(file1_path, 'r', encoding='utf-8') as f1, \
         open(file2_path, 'r', encoding='utf-8') as f2:
        
        line_num = 1
        while True:
            line1 = f1.readline()
            line2 = f2.readline()

            # Оба файла закончились одновременно
            if not line1 and not line2:
                print(f"✅ Файлы полностью идентичны.")
                break

            # Нашли отличие
            if line1 != line2:
                reason = ""
                if not line1:
                    reason = " (файл 1 закончился раньше)"
                elif not line2:
                    reason = " (файл 2 закончился раньше)"
                
                # repr() покажет невидимые символы (пробелы, \r, \n)
                print(f"📍 Первое отличие на строке {line_num}{reason}")
                print(f"   📄 split_output: {repr(line1.rstrip())}")
                print(f"   📄 split_input: {repr(line2.rstrip())}")
                break

            line_num += 1

# Запуск сравнения
find_first_difference('split_output/part_181.txt', 'split_input/part_181.txt')