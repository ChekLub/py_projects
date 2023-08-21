# Data_Analysis
Задачи по аналитике данных. 
Примеры дашбордов в Superset. 
АВ-тесты: t-тест, тест Манна-Уитни, с применением бустрепа и бакетного преобразования.
Прогнозирование временных рядов.
Поиск аномалий в метриках.
Автоматизация системы оповещений с помощью телеграм-бота.
Внутри есть Readme с подробным описанием задач.

# taster_wine
В папĸе data находятся 43 CSV файла с отзывами на различные вина
task.pdf - формулировка задачи
taster_wine.ipynb - решение задачи на python (pandas)

Задача: 
- провести очистку данных
- исследовать взаимосвязи оценки вин и стоимости
- определить ТОП-5 экспертов по оценке вина
- визуализировать данные (баллы оценки, стоимость вин, ценовые диапазоны вин, которые оценили ТОП-5 экспертов)
- определить маркеры высокой оценки в текстовых рецензиях и регионах происхождения вина

Решено в pandas, визуализация matplotlib: гистограммы (bins), круговые диаграммы с детализацией сектора (pie), график рассеяния (scatter), столбчатые диаграммы (bar). Для разбора рецензий для выявления ключевых слов, влияющих на высокую оценку, использована библиотека nltk. 

# currency_from_cbr_plot.ipynb
Задача: построить график курса доллара, евро или йены за желаемый период, начиная с 01.01.2019, с ЦБ http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2019&date_req2=10/02/2021&VAL_NM_RQ=R01235
Вывести минимальный, максимальный и средний курс за период - цену и дату.
Сделать возможность выбирать валюту (евро, доллар, иена) и диапазон дат через виджет.

Задача решена с использованием модулей requests и xml.etree.ElementTree.

# user_churn/Churn_users.ipynb
В папке user_churn представлено решение задачи прогнозирования оттока клиентов компании. Решено на платформе kaggle.
Проведен разведовательный анализ данных (РАД). Визуализация признаков гистограммами, построена карта корреляции признаков.
Для решения задачи классификации в sklearn псотроен пайплайн со стандартизацией числовых признаков, one-hot-encoding категориальных признаков, логистической регрессией для предсказания. Для поиска коэффициента регуляризации логистической регрессии использована кросс-валидация.
Также задача решена градиентным бустингом с использованием бибилиотеки catboost.
В качестве метрики обеих моделей использована roc_auc.
Задача решалась на платформе kaggle, поэтому результаты записывались в файл 'submission.csv' и отправлялись на проверку.
Точность предсказания составила 85%.

# py_projects/yolo8/
В папке yolo8 представлено решение задачи о генерации набора изображений (прямоугольник рандомного цвета, размера и ориентации в заданном диапазоне на констрастном фоне) и обучении нейросети yolo для распознавания этих изображений и выдачи ограничиваюших прямоугольников. 
gen_rect.py - Скрипт для генерации изображений
yolov8n_custom4_обучение - папка, где сохранены результаты обучения yolo8, веса и изображения
yolov8n_v8_test_распознавание  - приведены несколько распознанных изображений
 ## gen_rect.py
Скрипт для генерации изображений прямоугольников. 
Создается класс прямоугольник в соответствии с заданием.
Задание: Реализовать на языке Python класс, один из методов которого будет создавать изображение и описание фигур, находящихся на этом изображении. Сгенерированное изображение должно быть размером 640х480 пикселей и представляет собой однотонный фон случайного цвета, на котором размещен прямоугольник случайного размера (без выхода за границы изображения) со стороной от 150 до 250 пикселей случайного цвета, отличного от цвета фона, повернутого на случайный угол от 0 до 89 градусов.
Выход метода класса:
1) сгенерированное изображение;
2) параметры описывающего прямоугольника (координаты x, y верхнего левого угла, ширина (w) и высота (h));
3) координаты четырех углов сгенерированного прямоугольника.
Затем создается директория, в которую сохраняются полученные изображения.

# weather_from_weather_net.ipynb
Задача: получить с сайта meteostat.net погоду за указанный пользователем период времени в Москве.
а) получить данные с сервера
в) составить датафрейм с погодами за указанный период дата, мин, макс, сред
г) составить данные по месяцам мин - min макс - max сред - mean
д) составить среднюю температуру с промежутком с 30 минут, заполнив пробелы методом linear или cubic или каким-то другим и построить на графике за какой-то один день, выбранный пользователем

Для обращения к сайту и получения данных используется скрипт # get_weather.py

# get_weather.py
Скрипт для получения данных (дата, погода) с сайта meteostat.net
url = 'https://meteostat.p.rapidapi.com/stations/daily'
Для работы скрипта необходимо ввести свой API-Key в headers:
headers = {
           'X-RapidAPI-Key': '###',
           'X-RapidAPI-Host': 'meteostat.p.rapidapi.com'
           }

# meteostation_widgets.ipynb
Задача: сделать функцию, которая интерактивно выводит метеостанции , находящиеся в выбранном диапазоне высот, с учетом полушария.
Названия метеостанций и их координаты лежат в файле ghcnd-stations.txt. (Название станции, широта, долгота, высота, ...) 
а) загрузить файл ghcnd-stations.txt
б) найти зонд, который выше всех и зонд, который ниже всех относительно уровня моря - координаты и название населённого пункта
в) перевести широту и долготу из градусов в радианы
г) вывести список метеостанций (названия) с высотами в диапазоне, выбранном на ползунке
д) сделать пункт г) в виде ф-ии - принимает кортеж из двух чисел (начальная и конечная высота), ничего не возвращает, печатает список станций print'ом
е) добавить выборку по северному и южному полушарию

# my_utilyty.py
Задача: Напишите небольшую консольную утилиту, позволяющую работать с папками текущей директории.
Утилита должна иметь меню выбора действия, в котором будут пункты:
1. Перейти в папку
2. Просмотреть содержимое текущей папки
3. Удалить папку
4. Создать папку
При выборе пунктов 1, 3, 4 программа запрашивает название папки и выводит результат действия: "Успешно создано/удалено/перешел", "Невозможно создать/удалить/перейти"
Функции создания/удаления/просмотра/активации папок прописаны в скрипте act.py
          
# scraper.py
Делаем парсинг сайта 'https://www.sravni.ru/karty/' с использованием библиотеки BeautifulSoup и requests.
записываем в файл csv информацию о банковских картах ['Банк', 'Платежная система', 'Льготный период', 'Кредитный лимит', 'Обслуживание']

# fraction.py
Программа, выполняющая операции (сложение и вычитание) с простыми дробями.
Дроби вводятся и выводятся в формате: n x/y, где n - целая часть, x - числитель, у - знаменатель.
Дроби могут быть отрицательные и не иметь целой части, или иметь только целую часть.

Примеры:
Ввод: 5/6 + 4/7 (всё выражение вводится целиком в виде строки)
Вывод: 1 17/42  (результат обязательно упростить и выделить целую часть)
Ввод: -2/3 - -2
Вывод: 1 1/3

# Fruits_to_files.py
программа считывает файл fruits.txt из папки data и создает папку Fruits, 
в которую записывает файлы вида Fruits_А.txt ... Fruits_Я.txt, распределяя названия фруктов по алфавиту 

