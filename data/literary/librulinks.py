import requests
from bs4 import BeautifulSoup


url = 'http://lib.ru/PROZA/'
with open('librulinks.txt', 'w') as f:
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'lxml')
    for link in soup.find_all('a', href=True):
        f.write(link['href'])
        f.write('\n')
f.close()