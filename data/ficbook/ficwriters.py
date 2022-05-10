import requests
import sys
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
fandoms = ['Гарри Поттер', 'Naruto', 'Вселенная Марвел', 'Шерлок BBC', 'Star Wars']
russian = re.compile("[а-яА-Я]+")
sys.stdout = open('ficwriters.txt', 'w')

for user in range(1, 100):
    url = 'https://fanfics.me/user' + str(user) + '/fics'
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        if 'Работы' not in str(soup.find('li', class_='activ2')):
            continue
        else:
            for fic in soup.find_all('div', class_='ContentTable_Half')[-1]:
                if 'фанфик' in fic:
                    df_list = pd.read_html(r.text)  # this parses all the tables in webpages to a list
                    df = df_list[0]
                    fandom = str(df[0][1]).split('(')[0]
                    for f in fandoms:
                        if f in fandom:
                            print(url, fandom)
    except TimeoutError:
        time.sleep(40)
        pass
