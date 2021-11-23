# coding: utf-8
from bs4 import BeautifulSoup
import requests
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from threading import Thread

ROOT_URL = 'https://play.google.com'


def scroll_page(url):
    """Получение даннаых с сайта с автоподргузкой"""

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')

    driver = webdriver.Firefox(executable_path='geckodriver', options=options)
    driver.get(url)

    while True:
        h_now = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        h_new = driver.execute_script("return document.body.scrollHeight")
        # скролим до тех пор пока не достигнем дна сайта
        if h_now == h_new:
            break

    full_page = driver.page_source
    driver.quit()
    return full_page


def check_app(app_link, must_include, i):
    """Парсим данные с страницы приложения.
    Поскольку какие-то данные могут отсутствовать, нужно оставлять их прочеркнутыми

    app_link - страница с которой парсим данные
    must_include - слово должно встречаться в описании или заголовке
    i - номер страницы"""

    global ROOT_URL
    global PROGRESS
    global to_convert

    app_page = requests.get(ROOT_URL + app_link)
    soup = BeautifulSoup(app_page.text, "html.parser")

    try:
        title = soup.find('h1', class_='AHFaub').find('span').text
    except:
        title = ''

    try:
        author = soup.findAll('a', class_='hrTbp R8zArc')[0].text
    except:
        author = ''

    try:
        category = soup.findAll('a', class_='hrTbp R8zArc')[1].text
    except:
        category = ''

    try:
        description = soup.findAll('div', class_='DWPxHb')[0].find('div').text.replace('\t', '')
    except:
        description = ''

    try:
        update = soup.findAll('div', class_='DWPxHb')[1].text
    except:
        update = ''

    try:
        rate = soup.find('div', class_='BHMmbe').text
    except:
        rate = ''

    try:
        numrate = ''.join(re.findall(r'\d', soup.findAll('span', class_='EymY4b')[0].text))
    except:
        numrate = ''

    if must_include in title.lower() or must_include in description.lower():
        info = {'URL': ROOT_URL + app_link,
                'Title': title,
                'Author': author,
                'Category': category,
                'Description': description,
                'Last Update': update,
                'Rating': rate,
                'Rate number': numrate}
        to_convert.append(info)

    # программа работает, а не зависла!
    print("\r" + PROGRESS.format(i), end='', flush=True)


search_word = input()
search_page = 'https://play.google.com/store/search?q={}&c=apps'.format(search_word)

soup = BeautifulSoup(scroll_page(search_page), "html.parser")
applist = soup.findAll('a', class_='JC71ub')
app_links = [link['href'] for link in applist]

PROGRESS = 'Total to parse: {}. '.format(len(app_links)) + ' {} pages already parsed'

to_convert = []

thread = [Thread(target=check_app(_, search_word, i), daemon=True) for i, _ in enumerate(app_links)]

for t in thread:
    t.start()
    t.join()


with open("data.json", "w", encoding='utf-8') as write_file:
    json.dump({i: data for i, data in enumerate(to_convert)}, write_file, ensure_ascii=False)
