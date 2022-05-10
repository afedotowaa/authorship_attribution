import re
import sys, threading
from bs4 import BeautifulSoup
import requests
import os
import sys


def get_text_links(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'lxml')
    links = []
    for link in soup.find_all('a', href=True):
        if 'text' in link['href'] and not '/' in link['href']:
            links.append(link['href'])
    return links


def get_text(url):
    sys.setrecursionlimit(10 ** 9)  # max depth of recursion
    threading.stack_size(2 ** 27)  # new thread will get stack of such size
    url = requests.get(url)
    html = BeautifulSoup(url.content, features='lxml')
    data = re.sub('<[^<]+?>', '', str(html))
    return data


with open('librulinks.txt', 'r') as f:
    for line in f:
        author = str(line)
        print(author)
        if len(author) > 3:
            os.mkdir(author.replace('\n', ''))
            url = 'http://lit.lib.ru/' + line.replace('\n', '')
            links = get_text_links(url)
            for text_name in links:
                current_link = url + text_name
                text = get_text(current_link)
                f = open(author.replace('\n', '') + '\\' + str(text_name) + '.txt', 'w', encoding='utf-8')
                try:
                    f.write(str(text))
                except TypeError:
                    text = 'none'
                finally:
                    f.write(str(text))
