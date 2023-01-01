# программа считывает файл fruits.txt из папки data
# и создает папку Fruits, 
# в которую записывает файлы вида Fruits_А.txt ... Fruits_Я.txt,
# распределяя названия фруктов по алфавиту 

import os

path = os.path.join('data', 'fruits.txt')
f = open(path, 'r', encoding="UTF-8")
#alfavit = list(map(chr, range(ord('А'), ord("Я")+1)))

try:
    os.mkdir("Fruits")
except FileExistsError:
    print('Директория уже существеут')

for fruit in f:
    char = fruit[0]

    if char != '\n':
        file_name = 'Fruits_' + char + '.txt'
        lst_Fruits = os.listdir("Fruits")
        path_fruits = os.path.join('Fruits', file_name)
        if file_name in lst_Fruits:
            f_wr = open(path_fruits, 'a', encoding='UTF-8')
        else:
            f_wr = open(path_fruits, 'w', encoding='UTF-8')
        f_wr.write(fruit)
        f_wr.close()

