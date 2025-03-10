import os
import requests
import hashlib
from tkinter import messagebox
import tkinter as tk

REPO_URL = "https://raw.githubusercontent.com/ваш_аккаунт/репозиторий/main/"
VERSION_FILE = REPO_URL + "version.txt"
FILES_TO_UPDATE = ["core_logic.py", "gui_interface.py", "config.json"]


def check_updates():
    try:
        # Проверка текущей версии
        local_version = open("version.txt").read().strip() if os.path.exists("version.txt") else "0.0"

        # Получение удаленной версии
        remote_version = requests.get(VERSION_FILE).text.strip()

        if remote_version > local_version:
            root = tk.Tk()
            root.withdraw()
            if messagebox.askyesno("Обновление", f"Доступна новая версия {remote_version}. Установить?"):
                update_files(remote_version)
                messagebox.showinfo("Обновление", "Программа будет перезапущена")
                os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")


def update_files(new_version):
    for file in FILES_TO_UPDATE:
        content = requests.get(REPO_URL + file).content
        with open(os.path.join("app", file), "wb") as f:
            f.write(content)

    with open("version.txt", "w") as f:
        f.write(new_version)


def main():
    check_updates()
    os.system("python app/gui_interface.py")


if __name__ == "__main__":
    main()