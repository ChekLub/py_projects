'''
Делаем парсинг 'https://www.sravni.ru/karty/'
записываем в файл csv информацию о банковских картах
'''

from bs4 import BeautifulSoup
import requests
import csv
import random, time

HOST = 'https://www.sravni.ru/karty/'

URL = 'https://www.sravni.ru/karty/'

def get_html(url, params=''):
    r = requests.get(url, params= params)
    r.encoding = 'utf-8'
    return r

def get_content(html):

    params = {
        'card': 'style_card__Ekris',
        'bank': '_v2mr5d',
        'pay_system': '_xu8phs',
        'grace_period': '_5gmjom _1livb46',
        'credit_limit': '_5gmjom _1livb46',
        'service': '_5gmjom _1livb46'
    }

    soup = BeautifulSoup(html.text,'html.parser')
    items = soup.find_all('div', class_=params['card'])

    cards = []
    for item in items:
        cards.append(
            {
            'bank': item.find('div', class_=params['bank']).get('title'),
            'pay_system': item.find('div', class_=params['pay_system']).get('title'),
            'grace_period': item.find(string=['Льготный период']).find_next('div', class_=params['grace_period']).get_text(strip=True),
            'credit_limit': item.find(string=['Кредитный лимит']).find_next('div', class_=params['credit_limit']).get_text(strip=True),
            'service': item.find(string=['Обслуживание']).find_next('div', class_=params['service']).get_text(strip=True)
            })
    return cards

def save_csv(items, filename):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Банк', 'Платежная система', 'Льготный период', 'Кредитный лимит', 'Обслуживание'])
        for item in items:
            writer.writerow([item['bank'], item['pay_system'], item['grace_period'], item['credit_limit'], item['service']])

html = get_html(URL)

value = random.random()
scaled_value = 1 + (value * (9 - 5))
print(scaled_value)
time.sleep(scaled_value)

cards = get_content(html)
save_csv(cards, 'cards.csv')
