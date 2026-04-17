import subprocess
import datetime
import os
import sys

REPO_PATH = r"."  # Для Windows пример

def run_git_command(command, cwd):
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    if not os.path.isdir(REPO_PATH):
        print(f"Папка репозитория не найдена: {REPO_PATH}")
        sys.exit(1)

    now = datetime.datetime.now()
    commit_message = now.strftime("%d:%m:%Y %H:%M:%S")

    print(f"Начало коммита: {commit_message}")

    success, out, err = run_git_command("git add .", REPO_PATH)
    if not success:
        print(f"Ошибка git add: {err}")

    cmd_commit = f'git commit --allow-empty -m "{commit_message}"'
    success, out, err = run_git_command(cmd_commit, REPO_PATH)
    
    if not success:
        if "nothing to commit" in err:
            print("Нет изменений для коммита.")
        else:
            print(f"Ошибка git commit: {err}")

    success, out, err = run_git_command("git push", REPO_PATH)
    if success:
        print("Успешно отправлено на GitHub!")
    else:
        print(f"Ошибка git push: {err}")

if __name__ == "__main__":
    main()