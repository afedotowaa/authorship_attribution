import requests
import os
import re

from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 Safari/537.36'
}


def request_to_url(url):
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.content, 'lxml')
    return soup


def auth_on_url(url):
    user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                     'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/75.0.3770.142 Safari/537.36'
    session = requests.Session()
    r = session.get(url, headers={
        'User-Agent': user_agent_val
    })

    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})
    _xsrf = session.cookies.get('_xsrf', domain=".fanfics.me")

    post_request = session.post(url, {
        'backUrl': 'https://fanfics.me/',
        'username': 'afedotowaaa',
        'password': 'Thomas1309!',
        '_xsrf': _xsrf
    })
    return post_request.text


with open('ficwriters.txt', 'r') as f:
    for url in f:
        author_folder = 'data/' + str(url).split('https://fanfics.me/')[1].replace('/fics', '').replace('\n', '')
        os.mkdir(author_folder)
        soup = request_to_url(url)
        links = []
        # book_no = 0
        for tag_a in soup.find_all('div', class_='FicTable_Title'):
            fic_id = tag_a.find('a').get('href', '')
            fic_link = 'https://fanfics.me/' + 'read.php?id=' + str(fic_id).replace('/fic', '')
            with open(author_folder + '/' + str(fic_id) + '.txt', 'a', encoding='utf-8') as out:
                soup = auth_on_url(fic_link)
                out.write(re.sub('<[^<]+?>', '', str(soup)))
                '''
                try:
                    for tag_a in soup.find('div', class_='chapter').find_all('p'):
                        for text in tag_a:
                            out.write(re.sub('<[^<]+?>', '', str(text)))
                except TypeError:
                    pass
            '''
