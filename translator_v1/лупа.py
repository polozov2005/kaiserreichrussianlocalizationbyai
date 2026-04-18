import os
from pathlib import Path

def find_first_difference(file1_path, file2_path):
    """Сравнивает два файла построчно. Возвращает None, если идентичны, 
    или кортеж (номер_строки, строка_из_файла1, строка_из_файла2) при отличии."""
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1, \
             open(file2_path, 'r', encoding='utf-8') as f2:
            
            line_num = 1
            while True:
                line1 = f1.readline()
                line2 = f2.readline()

                # Оба файла закончились
                if not line1 and not line2:
                    return None
                
                # Нашли отличие
                if line1 != line2:
                    return line_num, line1, line2
                
                line_num += 1
    except UnicodeDecodeError:
        return ("binary",)

def compare_folders(dir1, dir2):
    p1 = Path(dir1)
    p2 = Path(dir2)

    if not p1.is_dir() or not p2.is_dir():
        print("❌ Одна или обе папки не существуют.")
        return

    # Собираем имена всех файлов (игнорируем подпапки)
    files1 = {f.name for f in p1.iterdir() if f.is_file()}
    files2 = {f.name for f in p2.iterdir() if f.is_file()}
    all_files = sorted(files1.union(files2))

    print(f"📂 Найдено файлов для сравнения: {len(all_files)}\n" + "-"*50)

    identical = diff = missing = 0

    for fname in all_files:
        f1_path = p1 / fname
        f2_path = p2 / fname

        if fname not in files1:
            print(f"⚠️ {fname}: отсутствует в {dir1}/")
            missing += 1
            continue
        if fname not in files2:
            print(f"⚠️ {fname}: отсутствует в {dir2}/")
            missing += 1
            continue

        result = find_first_difference(f1_path, f2_path)

        if result is None:
            print(f"✅ {fname}: идентичны")
            identical += 1
        elif result[0] == "binary":
            print(f"⚠️ {fname}: бинарный файл (пропущено)")
            missing += 1
        else:
            line_num, l1, l2 = result
            reason = ""
            if not l1: reason = " (файл 1 закончился раньше)"
            elif not l2: reason = " (файл 2 закончился раньше)"
            
            print(f"❌ {fname}: отличие на строке {line_num}{reason}")
            # rstrip() убирает только переносы строк, repr() показывает скрытые символы
            print(f"   📄 {dir1}: {repr(l1.rstrip())}")
            print(f"   📄 {dir2}: {repr(l2.rstrip())}")
            diff += 1

    print("-" * 50)
    print(f"📊 Итог: {identical} идентичных | {diff} с отличиями | {missing} отсутствуют/бинарные")

# Запуск сравнения
compare_folders('split_output', 'split_input')