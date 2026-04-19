import os
import shutil

SOURCE_DIR = "english_localisation"
TARGET_DIR = "localisation"

def convert_localization(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Исходная папка '{src_dir}' не найдена.")

    os.makedirs(dst_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        # Формируем относительный путь от исходной директории
        rel_path = os.path.relpath(root, src_dir)
        # Заменяем english на russian в названиях папок
        rel_path = rel_path.replace("english", "russian")
        
        target_root = os.path.join(dst_dir, rel_path)
        os.makedirs(target_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            
            # Обновляем название файла
            new_file = file.replace("english", "russian")
            new_file = new_file.replace("l_english", "l_russian")
            target_file = os.path.join(target_root, new_file)

            # Обрабатываем только YAML-файлы локализации
            if file.lower().endswith(".yml"):
                with open(src_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Заменяем ключ языка в содержимом
                content = content.replace("l_english", "l_russian")
                
                # Записываем в UTF-8 без BOM, с сохранением исходных переносов строк
                with open(target_file, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
            else:
                # Остальные файлы копируются без изменений
                shutil.copy2(src_file, target_file)

    print("Обработка завершена. Файлы скопированы и адаптированы для HOI4.")

if __name__ == "__main__":
    convert_localization(SOURCE_DIR, TARGET_DIR)