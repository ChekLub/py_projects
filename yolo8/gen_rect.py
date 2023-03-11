from PIL import Image, ImageDraw
import random
import math
import numpy as np
import shutil
import os
import sys


class Rectng:
    def __init__(self, wh_back=(640, 480), l_rect=(150, 250), alpha=(0, 89)):

        self.im = None

        self.xy = []  # координат вершин прямоугольника (x, y)
        self.bnd_box = [0, 0, 0, 0]  # координаты левой верхней вершины описывающего прямоугольника , ширина и высота описывающего прямоугольника
        self.bnd_box_norm = [0, 0, 0, 0]  # нормализованные параметры описывающего прямоугольника

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.color_back = tuple([r, g, b])  # цвет фона

        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color_rect = tuple([r, g, b])  # цвет прямоугольника
            if color_rect != self.color_back:
                break
        self.color_rect = color_rect

        self.wh_back = wh_back  # размеры фона
        self.w = random.randint(l_rect[0], l_rect[1])
        self.h = random.randint(l_rect[0], l_rect[1])  # размеры прямоугольника

        self.alpha = math.radians(random.randint(alpha[0], alpha[1]))  # угол поворота прямоугольника относительно его центра в радианах

    def gen_draw(self, save=0):  # генератор изображения

        w = self.w
        h = self.h
        alpha = self.alpha

        xy_rect = np.array([[-w / 2, h / 2], [-w / 2, -h / 2], [w / 2, -h / 2],
                            [w / 2, h / 2]])  # координаты вершин прямоугольника относительно его центра
        rotate = np.array([[math.cos(alpha), math.sin(alpha)], [-math.sin(alpha), math.cos(alpha)]])  # матрица поворота углов прямоугольника относительно его центра
        xy_rect_rotate = np.matmul(xy_rect, rotate)  # координаты вершин после поворота на угол альфа

        xc_min = math.ceil(abs(min(xy_rect_rotate[:, 0])))  # мин возможное горизонтальное положение центра прямоугольника на фоне
        xc_max = self.wh_back[0] - math.ceil(max(xy_rect_rotate[:, 0]))  # мах возможное горизонтальное положение центра прямоугольника на фоне
        xc = random.randint(xc_min, xc_max)  # x центра прямоугольника
        x = xy_rect_rotate[:, 0] + xc  # х координаты  вершин

        yc_min = math.ceil(abs(min(xy_rect_rotate[:, 1])))  # аналогично для y
        yc_max = self.wh_back[1] - math.ceil(max(xy_rect_rotate[:, 1]))
        yc = random.randint(yc_min, yc_max)
        y = xy_rect_rotate[:, 1] + yc

        self.xy = list(zip(x, y))  # список кортежей координат вершин прямоугольника (x, y)

        # Описывающй прямоугольник:

        # self.bnd_box[0] = min(x) # координаты левого верхнего угла описывающего прямоугольника.
        # self.bnd_box[1] = min(y) # Однако используемая мной версия yolo5 для последующего задания
        # в качестве метки требует координаты центра описывающего прямоугольника,
        # поэтому я сохраняла именно их:

        self.bnd_box[0] = xc  # координаты центра описывающего прямоугольника
        self.bnd_box[1] = yc
        self.bnd_box[2] = max(x) - min(x)  # ширина описывающего прямоугольника
        self.bnd_box[3] = max(y) - min(y)  # высота описывающего прямоугольника

        # Нормализованные параметры описывающего прямоугольника:
        self.bnd_box_norm[0] = self.bnd_box[0] / self.wh_back[0]  # х bnd_box
        self.bnd_box_norm[1] = self.bnd_box[1] / self.wh_back[1]  # y bnd_box
        self.bnd_box_norm[2] = self.bnd_box[2] / self.wh_back[0]  # w bnd_box
        self.bnd_box_norm[3] = self.bnd_box[3] / self.wh_back[1]  # h bnd_box

        # Отрисовка изображения:
        self.im = Image.new('RGB', self.wh_back, self.color_back)  # создаем обЪект Image -  фон
        draw = ImageDraw.Draw(self.im)  # создаем обЪект draw, который будет отрисовываться на фоновом обЪекте im
        draw.polygon(self.xy, fill=self.color_rect)  # создаем прямоугольник

        # отрисовка ограничивающего прямоугольника:
        # a = (self.bnd_box[0]-self.bnd_box[2]/2, self.bnd_box[1]-self.bnd_box[3]/2)
        # b = (self.bnd_box[0]+self.bnd_box[2]/2, self.bnd_box[1]-self.bnd_box[3]/2)
        # c = (self.bnd_box[0]+self.bnd_box[2]/2, self.bnd_box[1]+self.bnd_box[3]/2)
        # d = (self.bnd_box[0]-self.bnd_box[2]/2, self.bnd_box[1]+self.bnd_box[3]/2)
        # draw.line( (a, b, c, d, a),  fill= 'red' )

        self.im.show()  # рисуем

        # Описывающий прямоугольник и Координаты прямоугольника: Вспомогательно, для быстрого вывода
        # print(f' Описывающий прямоугольник:\n x={self.bnd_box[0]} \n y={self.bnd_box[1]} \n w={self.bnd_box[2]} \n h={self.bnd_box[3]} \n')
        # print(f'Координаты прямоугольника:\n' )
        # for i, coord in enumerate(self.xy):
        #   print(f'x{i+1} = {coord[0]}, y{i+1} = {coord[1]}')

        return self.im, self.bnd_box, self.xy

    def save_for_yolo(self, draw_name='Rect.png'):
        self.im.save(draw_name)

        f_name = draw_name.split('.')[0] + '.txt'
        f = open(f_name, 'w')
        f.write('0' + ' ' + str(self.bnd_box_norm[0]) + ' ' + str(self.bnd_box_norm[1]) + ' ' + str(
            self.bnd_box_norm[2]) + ' ' + str(self.bnd_box_norm[3]))
        f.close()


# файлы картинок и меток должны лежат в соответствующих папках:
#datasets -> picters
#                    -> images
#                    -> labels

path = 'D://NIIAS/My_Yolo5/datasets'
os.chdir(path)
p_pict = os.path.join(path, 'picters')  # Папака, где будут сохранены картинки и файлы меток

try:
    os.mkdir('picters')
    os.chdir(p_pict)
except FileExistsError:
    shutil.rmtree(p_pict)
    os.mkdir('picters')
    os.chdir(p_pict)


os.mkdir('images')
os.mkdir('labels')

p_img = os.path.join(p_pict, 'images')
p_lbl = os.path.join(p_pict, 'labels')

# Создаем наш датасет:
n = 0
while n <= 4:
    rect = Rectng()
    rect.gen_draw()
    f_name = 'Rect' + str(n) + '.jpg'
    rect.save_for_yolo(f_name)
    print(n)
    n += 1


#Далее разносим картинки и метки в разные папки таким образом, как требуется для обучения сети:
fil_jpg = []  # спсок имен файлов .jpg
fil_lbl = []  # спсок имен файлов .txt

ldir = os.listdir()
for fil in ldir:
    if len(fil.split('.')) > 1:
        if fil.split('.')[1] == 'jpg':
            fil_jpg.append(fil)
        elif fil.split('.')[1] =='txt':
            fil_lbl.append(fil)


for fil in fil_jpg:
    shutil.move(fil, p_img)  # перемещаем файлы с картинками в папку images

for fil in fil_lbl:
    shutil.move(fil, p_lbl)  # перемещаем файлы с метками в папку labels

#Делим выборку на тестовую и тренировочную:
train_list = os.listdir(p_img)  # список имен всех картинок
test_samples = random.sample(train_list, k=int(0.2*n)) # список имен тестовых картинок
train_samples = [i for i in train_list if i not in test_samples] # список имен обучающих/тренировочных картинок

train_list_labl = os.listdir(p_lbl) # список имен файлов меток
train_im = []  # список имен файлов обучающих картинок без формата, для разделения файлов с метками в соответствии с именами
for im in train_samples:
    train_im.append(im.split('.')[0])

test_im = []
for im in test_samples:
    test_im.append(im.split('.')[0])

train_labl_samples = []
test_labl_samples = []

for fil in train_list_labl:
    if fil.split('.')[0] in train_im:  # если имя файла метки есть в списке имен тренировочной выборки картинок, то оно заносится в списокtrain_labl_samples
        train_labl_samples.append(fil)
    elif fil.split('.')[0] in test_im:
        test_labl_samples.append(fil)


os.chdir(p_img)
os.mkdir('train')
p_im_train = os.path.join(p_img, 'train')
os.mkdir('val')
p_im_test = os.path.join(p_img, 'val')

for fil in train_samples:
    shutil.move(fil, p_im_train)

for fil in test_samples:
    shutil.move(fil, p_im_test)


os.chdir(p_lbl)
os.mkdir('train')
p_lb_train = os.path.join(p_lbl, 'train')
os.mkdir('val')
p_lb_test = os.path.join(p_lbl, 'val')

for fil in train_labl_samples:
    shutil.move(fil, p_lb_train)

for fil in test_labl_samples:
    shutil.move(fil, p_lb_test)


