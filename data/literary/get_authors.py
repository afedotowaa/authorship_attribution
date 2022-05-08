from bs4 import BeautifulSoup
import requests


url = 'https://booksonline.com.ua/authors.php?letter=Н&lang=ru'  # обращение по той же ссылке
links = []  # список в котором будем хранить ссылки на авторов

request = requests.get(url)

soup = BeautifulSoup(request.content, 'lxml')

with open('links.txt', 'w') as f:
    for tag_a in soup.find('ul', id='resorts_authors').find_all('li', class_='cat-item'):
        links = ''

        for a in tag_a:
            author_link = str(a).split("href=")[1].split('><div')[0].replace('"',
                                                                             '')  # "почистим" ссылку для корректной записи
            f.write(author_link)
            f.write('\n')

    f.close()
