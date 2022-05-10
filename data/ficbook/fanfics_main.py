from bs4 import BeautifulSoup
import re
import urllib.request

# Константы
OPENER = urllib.request.urlopen
PARSER = 'html5lib'
ROOT = 'http://fanfics.me/'
ROOT_M = 'http://m.fanfics.me/'
AUTHORS_RE = re.compile(r'Автор*')
TRANSLATORS_RE = re.compile(r'Переводчик*')
EDITORS_RE = re.compile(r'Бет*')


class Story(object):
    def __init__(self, url=None, id=None):
        """Произведение на fanfics.me
        Если переданы и url и id, то используется ссылка.
        :type id: int
        :param url: Ссылка на произведение (фанфик)
        :param id: Id произведения (фанфика)
        Аттрибуты
            id  (int):                  id произведения
            chapter_count (int):        Количество глав
            title (str):                Название
            category (str):             Категория (гет, слэш, джен)
            summary (str):              Аннотация
            is_a_translation (bool):    Является ли произведние переводом
            authors (list of str):      Список авторов (переводчиков)
            editors (list of str):      Список редакторов (бет), если их нет то пуст
            fandoms (list of str):      Список фандомов
            parings (list of str):      Список пейрингов и персонажей
            rating (str):               Возрастные ограничения (General, PG-13,R,NC-17)
            genres (list of str):       Список жанров
            status (str):               Статус произведения (Закончен, В работе, Заморожен)
            size (str):                 Размер (Мини, Миди, Макси)
            views (int):                Количество просмотров
            views_today (int):          Просмотров за сегодня
            comments (int):             Количество комментариев
            recommendations (int):      Количество рекомендаций
            readers (int):              Количество читателей
            date_published (str):       Дата публикации (ДД.ММ.ГГГГ)
            date_updated (str):         Дата обновления (ДД.ММ.ГГГГ)
        """
        if url is None or url == '':
            if id is None:
                raise ValueError('No id nor url is specified ')
            else:
                url = ROOT + '/fic' + str(id)
                self.id = id
        else:
            self.id = int(url.split('/fic')[1])
        source = OPENER(url).read()
        soup = BeautifulSoup(source, PARSER)
        stat_block = soup.find('div', id='fic_info_content_stat')
        head_block = soup.find('div', class_='FicHead')
        temp = soup.find_all('div', class_='FicContentsChapterName')
        if not temp:
            self.chapter_count = 1
        else:
            temp = temp[-1]
            self.chapter_count = int(temp.a['href'].split('chapter=')[1]) + 1
        self.title = head_block.h1.contents[0].strip()
        self.category = head_block.h1.contents[1].text
        self.summary = soup.find('div', class_='summary_text_fic3').text
        self.summary = self.summary.strip()
        temp = head_block.find('div', class_='title', string=AUTHORS_RE)
        self.is_a_translation = False
        if temp is None:
            temp = head_block.find('div', class_='title', string=TRANSLATORS_RE)
            self.is_a_translation = True
        temp = temp.parent.find('div', class_='content')
        temp = temp.find_all(attrs={"data-show-member": True})
        self.authors = []
        for t in temp:
            self.authors.append(t.text)
        self.editors = []
        temp = head_block.find('div', class_='title', string=EDITORS_RE)
        if temp:
            temp = temp.parent.find('div', class_='content')
            temp = temp.find_all(attrs={"data-show-member": True})
            for t in temp:
                self.editors.append(t.text)
        temp = head_block.find_all(attrs={"data-show-fandom": True})
        self.fandoms = []
        for t in temp:
            self.fandoms.append(t.text)
        self.parings = []
        temp = head_block.find_all('a', {'href': re.compile('^/paring')})
        for t in temp:
            self.parings.append(t.text)
        temp = head_block.find_all('a', {'href': re.compile('^/character')})
        for t in temp:
            self.parings.append(t.text)
        temp = head_block.find('div', class_='title', string='Рейтинг:')
        temp = temp.parent.find('div', class_='content')
        self.rating = temp.text
        temp = head_block.find('div', class_='title', string='Жанр:')
        temp = temp.parent.find('div', class_='content')
        temp = temp.text.replace('Hurt/comfort', 'Hurt+comfort')
        self.genres = temp.split('/')
        temp = head_block.find('div', class_='title', string='Статус:')
        temp = temp.parent.find('div', class_='content')
        self.status = temp.text
        temp = head_block.find('div', class_='title', string='Размер:')
        temp = temp.parent.find('div', class_='content')
        self.size = temp.contents[0].replace('|', '').strip()

        temp = stat_block.find('td', string='Просмотров:')
        temp = temp.parent.find('td', title='Просмотров всего + Просмотров за сегодня')
        self.views = int(temp.contents[0].replace(' ', ''))
        self.views_today = int(temp.contents[1].text.replace('за сегодня', ''))
        temp = stat_block.find('td', class_='green')
        self.comments = int(temp.text.replace(' ', ''))
        temp = stat_block.find('td', class_='fem')
        self.recommendations = int(temp.text.replace(' ', ''))
        temp = stat_block.find('span', class_='blue')
        self.readers = int(temp.text.replace(' ', ''))
        temp = stat_block.find('td', string='Опубликован:')
        self.date_published = temp.nextSibling.text
        temp = stat_block.find('td', string='Изменен:')
        self.date_updated = temp.nextSibling.text


class Chapter(object):
    def __init__(self, story_id=None, chapter=0, url=None):
        """Произведение на fanfics.me
        Если переданы и url и story_id, то используется ссылка.
        По умолчанию возвращает первую главу
        :type story_id: int
        :type chapter: int
        :param url: Ссылка на главу
        :param story_id: Id произведения (фанфика)
        :param chapter: порядковый номер главы (начиная с 0)
        Аттрибуты
            title (str):                Название главы
            text (str):                 Содержание с некоторыми тегами (i,b,s)
        """
        if url is None or url == '':
            if story_id is None:
                raise ValueError('No id nor url is specified ')
            else:
                url = ROOT_M + '/read.php?&id=' + str(story_id) + '&chapter=' + str(chapter)
        else:
            url = url.split('fanfics.me')[1]
            url = ROOT_M + url
        source = OPENER(url).read()
        soup = BeautifulSoup(source, PARSER)
        text_list = []
        try:
            temp = soup.find('div', id='c')
            self.title = soup.find('h2').text
            for t in temp.find_all('a'):
                t.decompose()
            for t in temp.find_all('p'):
                text_list.append(''.join(str(s) for s in t.contents))
            self.text = '\n'.join(text_list)
        except:
            raise ValueError('Chapter not found')

a = Story()

