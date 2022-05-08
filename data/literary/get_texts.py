import os
import sys

import requests
from bs4 import BeautifulSoup

from itertools import groupby

PATH='authorship_attribution/literary/'
with open(PATH + 'links.txt', 'r', encoding='utf-8') as f:
    for url in f:
        author = url.split('author=')[1].replace('&amp;lang=ru', '').replace('\n', '')
        os.mkdir(PATH + author)
        print(author)
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'lxml')

        for tag_a in soup.find('div', class_='wrapper clearfix').find_all('div', class_='book_info_prev'):
            links = [tag_a.find('a').get('href', '') for tag in tag_a]
            books = []
            book_no = 0
            for a in tag_a:
                books.append('https://booksonline.com.ua/' + links[0])
                books_links = [el for el, _ in groupby(books)]
            for book_url in books_links:
                book_no += 1
                request = requests.get(book_url)
                original_stdout = sys.stdout
                with open(PATH + author + '/' + str(book_no) + '.txt', 'a') as out:
                    for page in range(1, 101):
                        page_url = book_url + '&' + 'page=' + str(page)
                        new_request = requests.get(page_url)
                        try:
                            for wrap in soup.find('div', class_='main_text').find_all('p'):
                                sys.stdout = out  # Change the standard output to the file we created.
                                print(wrap.get_text())
                                sys.stdout = original_stdout
                        except TypeError():
                            pass

