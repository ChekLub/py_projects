import sys
import os

def make_dir(dir_name):
    if not dir_name:
        print("Необходимо указать имя директории вторым параметром")
        return
    dir_path = os.path.join(os.getcwd(), dir_name)
    try:
        os.mkdir(dir_path)
        print(f'директория {dir_name} создана')
    except FileExistsError:
        print(f'директория {dir_name} уже существует')


def change_dir(dir_name):
    if not dir_name:
        print("Укажите имя директории вторым параметром")
        return
    try:

        cwd = os.getcwd()
        if cwd.find(dir_name) != -1:
            while os.path.split(cwd)[1] != dir_name:
                cwd = os.path.split(cwd)[0]
            dir_path = cwd
            os.chdir(dir_path)
        else:
            dir_path = os.path.join(os.getcwd(), dir_name)
            os.chdir(dir_path)

        print(f"Текущая директрия: {dir_path}")
    except FileExistsError:
        print('Указанной директории не существует')

def del_dir(dir_name):
    if not dir_name:
        print("Укажите имя директории вторым параметром")
        return
    dir_path = os.path.join(os.getcwd(), dir_name)
    try:
        os.rmdir(dir_path)
        print(f"Папка {dir_path} удалена ")
    except FileNotFoundError:
        print('Указанной папки не существует')


def list_dir():
    dir_path = os.path.join(os.getcwd())
    try:
        print(os.listdir(dir_path))
    except:
        print("Указанной папки не существует")

def print_help():
    print("help - получение справки")
    print("4 - создание директории")
    print("1 - смена директории")
    print("3 - удаление директории")
    print("2 - список папок и файлов в директории")
    print("quit - для завершения работы")

#dir_name = None #input("Введите имя папки")
