# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize

from collections import Counter

import re
import pymorphy2

import os
import csv
import glob
import pandas as pd
morph = pymorphy2.MorphAnalyzer()


def get_pos(x):
    """ получение части речи """
    return morph.parse(x)[0].tag.POS


def get_normal_form(word):
    """ приведение слова к нормальной форме """
    return morph.parse(word)[0].normal_form


def get_sentences(*args, **kvargs):
    """ получение предложений из текста """
    return sent_tokenize(*args, **kvargs)


def get_words(text):
    """ получение слов из текста """
    words = (
        re.sub(r'(^[^a-zA-Zа-яА-Я\d]+)|([^a-zA-Zа-яА-Я\d]+$)', '', word)
        for word in text.split())
    return tuple(word for word in words if word)


def get_normalized_words(text):
    """ получение списка слов, приведенных к нормальной форме """
    words = get_words(text)
    return tuple(get_normal_form(word) for word in words)


def ngrams_letters_for_word(word, n):
    """ получение n-грамм символов в слове """
    for i in range(len(word) - n + 1):
        return word[i:i + n]


def ngrams_letters(text, n):
    """ получение n-грамм символов в тексте """
    words = get_words(text)
    output = list()
    for word in words:
        ngrams = ngrams_letters_for_word(word, n)
        if ngrams:
            output.append(ngrams)
    return output


def ngrams_words(text, n):
    """  поучение n-грамм слов в тексте """
    parts = re.split(r'[\.!?;]+', text)
    output = list()
    for part in parts:
        words = [morph.parse(x)[0].normal_form for x in get_normalized_words(part)]
        for i in range(len(words) - n + 1):
            output.append(tuple(words[i:i + n]))
    return output


def get_punctuation_freq(text):
    """ распределение частот знаков пунктуации """
    punct = re.findall(r'[\.,!?;:]{1,6}', text)
    punct += re.findall(r'[\'\"\(\)]', text)
    punct += re.findall(r'\b\-+\b', text)
    counter = Counter(punct)
    common = counter.most_common(35)
    freq = {a[0]: a[1] / len(get_sentences(text)) for a in common}
    return freq


def get_common_ngrams_words_freq(text, n, count=350):
    """ распределение 350 часто встречающихся n-грамм слов в тексте """
    ngrams_list = ngrams_words(text, n)
    counter = Counter(ngrams_list)
    common = counter.most_common(count)
    freq = {a[0]: a[1] / len(ngrams_list) for a in common}
    return freq


def get_common_ngrams_letters_freq(text, n, count=250):
    """ распределение 250 часто встречающихся n-грамм символов в тексте """
    ngrams_list = ngrams_letters(text, n)
    counter = Counter(ngrams_list)
    common = counter.most_common(count)
    freq = {a[0]: a[1] / len(ngrams_list) for a in common}
    return freq


def get_part_of_speech_freq(text):
    """ распределение частей речи в тексте """
    words = [get_pos(x) for x in get_words(text)]  # if morph.parse(x)[0].tag.POS]
    counter = Counter(words)
    common = counter.most_common(20)
    freq = {a[0]: a[1] / len(words) for a in common}
    return freq


def get_average_paragraph_length(text):
    """ средняя длина абзаца """
    return len(get_sentences(text)) / len(re.split(r'\n+', text))


def get_average_word_length_in_letters(text):
    """ средняя длина слова в символах """
    words = get_words(text)
    return sum(map(len, words)) / len(words)


def get_average_sentense_length(text):
    """ средняя длина предложения """
    return len(get_words(text)) / len(get_sentences(text))


def get_chars_statistic(text):
    """ частотное распределение букв русского алфавита """
    chars = re.findall(r'[a-яА-Я]', text)
    counter = Counter(chars)
    common = counter.most_common(33)
    freq = {a[0]: a[1] / len(chars) for a in common}
    return freq


def normalize(data):
    """ нормирование вектора признаков"""
    norm_data = []
    for x in data:
        x = (x - min(data)) / (max(data) - min(data))
        norm_data.append(x)
    return norm_data


sharov_keys = ['быть', 'весь', 'вот', 'время', 'видеть', 'вдруг', 'большой', 'взять', 'ведь', 'ваш', 'вода', 'всё', 'больше', 'белый', 'вечер', 'вопрос', 'вернуться', 'взгляд', 'бояться', 'вместе', 'вообще', 'быстро', 'бывать', 'война', 'будто', 'бросить', 'как-будто', 'брать', 'войти', 'вести', 'воздух', 'верить', 'брат', 'бежать', 'ветер', 'берег', 'волос', 'видно', 'вещь', 'великий', 'впрочем', 'внимание', 'бутылка', 'возле', 'вздохнуть', 'близкий', 'бумага', 'вперед', 'вполне', 'вера', 'вовсе', 'врач', 'бить', 'вокруг', 'вниз', 'баба', 'боль', 'вместо', 'вроде', 'возвращаться', 'власть', 'важный', 'водка', 'ах', 'бывший', 'возможность', 'бабушка', 'бок', 'видимо', 'век', 'веселый', 'висеть', 'возможно', 'взглянуть', 'вновь', 'военный', 'бой', 'армия', 'вверх', 'враг', 'впервые', 'быстрый', 'воля', 'виноватый', 'вино', 'волна', 'больница', 'броситься', 'впереди', 'весело', 'внимательно', 'возникнуть', 'воскликнуть', 'бедный', 'вагон', 'взяться', 'бегать', 'внезапно', 'больно', 'верный', 'восемь', 'внутренний', 'велеть', 'возраст', 'ворота', 'беда', 'вдоль', 'весна', 'болеть', 'автобус', 'бабка', 'вечный', 'болезнь', 'весьма', 'автор', 'бровь', 'будущее', 'больной', 'врать', 'билет', 'адрес', 'бросать', 'автомат', 'внизу', 'верно', 'вернуть', 'впечатление', 'буква', 'волноваться', 'больший', 'вероятно', 'видный', 'банк', 'борьба', 'автомобиль', 'воспоминание', 'возможный', 'водитель', 'верхний', 'боевой', 'ветка', 'беседа', 'бледный', 'восторг', 'абсолютно', 'богатый', 'вкус', 'брюки', 'вряд', 'включить', 'бумажка', 'будущий', 'ага', 'близко', 'ботинок', 'вокзал', 'возразить', 'везти', 'возникать', 'английский', 'ведро', 'ближайший', 'банка', 'вина', 'валяться', 'борт', 'бандит', 'веревка', 'внутри', 'бродить', 'американский', 'бормотать', 'волк', 'во-первых', 'буквально', 'баня', 'борода', 'войско', 'вздрогнуть', 'водить', 'аккуратно', 'вернее', 'вот-вот', 'вдвоем', 'взрыв', 'бесконечный', 'взрослый', 'вечно', 'блестеть', 'бороться', 'биться', 'вариант', 'волнение', 'башня', 'вовремя', 'воевать', 'везде', 'большинство', 'видать', 'вечерний', 'барон', 'ванная', 'асфальт', 'белье', 'боец', 'аппарат', 'беспокоиться', 'внук', 'важно', 'бокал', 'бригада', 'во-вторых', 'божий', 'более', 'вершина', 'блестящий', 'артист', 'база', 'благородный', 'вообще-то', 'внешний', 'ворот', 'бык', 'академик', 'библиотека', 'болтать', 'было', 'вор', 'бочка', 'варить', 'влажный', 'бревно', 'балкон', 'вздыхать', 'видеться', 'вздох', 'батарея', 'благодарить', 'возмутиться', 'возвращение', 'возражать', 'безопасность', 'ангел', 'август', 'волшебный', 'вождь', 'воображение', 'восьмой', 'болото', 'беседовать', 'вежливо', 'бессмысленный', 'бомба', 'висок', 'базар', 'блеск', 'воскресенье', 'барак', 'бедро', 'возиться', 'воздушный', 'восток', 'воин', 'бросаться', 'благодаря', 'бар', 'веко', 'безумный', 'воротник', 'бригадир', 'агент', 'актер', 'атака', 'внезапный', 'благодарность', 'буфет', 'вне', 'восточный', 'владеть', 'бред', 'беречь', 'анекдот', 'вглядываться', 'вздрагивать', 'вон', 'брак', 'американец', 'бизнес', 'босой', 'верх', 'воспользоваться', 'бабочка', 'влезть', 'взор', 'впрямь', 'винтовка', 'арестовать', 'аэропорт', 'весенний', 'визит', 'волновать', 'будка', 'великолепный', 'вкусный', 'вначале', 'а-а', 'виднеться', 'воробей', 'башка', 'вправду', 'возить', 'большевик', 'буркнуть', 'браться', 'велосипед', 'взвод', 'владелец', 'братец', 'адвокат', 'аж', 'вопль', 'вдали', 'внутрь', 'бег', 'бумажный', 'восемьдесят', 'ванна', 'ветвь', 'береза', 'блюдо', 'вертолет', 'вертеться', 'бешеный', 'вмешаться', 'аккуратный', 'болтаться', 'бывало', 'ввести', 'взлететь', 'валить', 'валенок', 'впоследствии', 'беспокойство', 'влюбиться', 'виски', 'внешность', 'внимательный', 'верста', 'боковой', 'величество', 'витрина', 'беспокоить', 'ворваться', 'акт', 'вилка', 'академия', 'ахнуть', 'богатство', 'букет', 'бульвар', 'ад', 'батюшка', 'версия', 'ведать', 'водиться', 'восемнадцать', 'арест', 'благодарный', 'вдова', 'вольный', 'акция', 'бесконечно', 'бутерброд', 'виновато', 'веранда', 'аллея', 'влияние', 'авторитет', 'бодро', 'внучка', 'бассейн', 'безусловно', 'бесполезный', 'вечность', 'воровать', 'внести', 'восхищение', 'вплотную', 'больничный', 'вертеть', 'воспринимать', 'восстановить', 'атмосфера', 'батальон', 'будить', 'ветерок', 'брести', 'включать', 'благо', 'близость', 'бетонный', 'бесшумно', 'вложить', 'ворона', 'видение', 'вручить', 'апрель', 'барышня', 'битва', 'брюхо', 'владыка', 'ай', 'аромат', 'бытие', 'блок', 'визг', 'абсолютный', 'армейский', 'блондинка', 'включая', 'бездна', 'бережно', 'ведьма', 'взорваться', 'воспитание', 'бегом', 'бодрый', 'бомж', 'вообразить', 'беззвучно', 'бензин', 'блокнот', 'бюро', 'возвращать', 'бинокль', 'бурный', 'безумие', 'бородатый', 'верховный', 'буря', 'величина', 'всадник', 'веселье', 'анализ', 'вежливый', 'вправо', 'алый', 'актриса', 'блеснуть', 'бронзовый', 'ворчать', 'вредный', 'безнадежно', 'вонючий', 'воевода', 'архив', 'весть', 'временной', 'альбом', 'возбудить', 'бас', 'беспомощный', 'боярин', 'барабан', 'влево', 'волшебник', 'белеть', 'вена', 'весло', 'врезаться', 'англичанин', 'аппетит', 'акцент', 'аэродром', 'визжать', 'муж', 'ответ', 'центр', 'правило', 'смерть', 'рынок', 'совет', 'счет', 'сердце', 'неделя', 'чувство', 'глава', 'наука', 'глаза', 'работать', 'смотреть', 'понять', 'пойти', 'спросить', 'понимать', 'получить', 'выйти', 'любить', 'остаться', 'простить']
uni_keys = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'щ', 'ш', 'ъ', 'ь', 'э', 'ю', 'я']
pos_keys = ['NOUN', 'VERB', 'ADJF', 'PREP', 'CONJ', 'NPRO', 'ADVB', 'PRCL', 'INFN', 'GRND', 'PRTF', 'ADJS', 'NUMR', 'PRED', 'COMP', 'PRTS', 'INTJ']
punct_keys = ['!', '"', '!!', '!!!', ',', '-', '.', ':', ';', '?', '..', '...', ',.', '??', '???', '?!', '!?', '/']
tri_keys = ['арб', 'бед', 'без', 'бес', 'бла', 'бог', 'бол', 'бро', 'буд', 'был', 'быт', 'вел', 'вер', 'вес', 'веч', 'вид', 'вла', 'вно', 'воз', 'вой', 'вол', 'вос', 'вре', 'все', 'вст', 'вся', 'выс', 'где', 'гес', 'гла', 'гов', 'год', 'гол', 'гор', 'гос', 'гот', 'гре', 'дав', 'даж', 'дал', 'дев', 'дей', 'дел', 'ден', 'дер', 'для', 'дни', 'доб', 'дов', 'дол', 'дом', 'дос', 'дре', 'дру', 'дум', 'душ', 'евг', 'его', 'ему', 'есл', 'еще', 'жен', 'жиз', 'заб', 'зав', 'зак', 'зам', 'зан', 'зап', 'зас', 'зде', 'зем', 'зна', 'изв', 'или', 'име', 'имп', 'имя', 'иск', 'исп', 'ист', 'каж', 'каз', 'как', 'кам', 'ког', 'кол', 'ком', 'кон', 'кот', 'кра', 'лег', 'лет', 'лид', 'лиц', 'лиш', 'луч', 'люб', 'люд', 'мал', 'мат', 'мед', 'мен', 'мес', 'меч', 'мил', 'мин', 'мир', 'мне', 'мно', 'мог', 'мое', 'мож', 'мои', 'мой', 'мол', 'моя', 'над', 'наз', 'нак', 'нам', 'нап', 'нас', 'нач', 'наш', 'нев', 'нед', 'ней', 'нем', 'нео', 'неп', 'нес', 'нет', 'неу', 'ник', 'нич', 'нов', 'обе', 'обр', 'объ', 'оде', 'оди', 'одн', 'ока', 'она', 'они', 'опя', 'ост', 'отв', 'оте', 'отк', 'отц', 'оче', 'пер', 'пис', 'пла', 'поб', 'пов', 'под', 'поз', 'пок', 'пол', 'пом', 'пон', 'поп', 'пор', 'пос', 'пот', 'поч', 'пра', 'пре', 'при', 'про', 'пус', 'пут', 'раб', 'рад', 'раз', 'рас', 'реш', 'рим', 'род', 'рук', 'сам', 'све', 'сво', 'свя', 'сде', 'себ', 'сег', 'сем', 'сен', 'сер', 'сес', 'сил', 'ска', 'ско', 'сла', 'сле', 'сло', 'слу', 'сме', 'смо', 'соб', 'сов', 'сос', 'спо', 'спр', 'сре', 'ста', 'сто', 'стр', 'суд', 'сча', 'так', 'там', 'тво', 'теб', 'тем', 'теп', 'тог', 'тол', 'том', 'тор', 'тот', 'тре', 'три', 'уви', 'уда', 'уже', 'узн', 'ули', 'уме', 'уст', 'фла', 'хот', 'хоч', 'хра', 'хри', 'цел', 'час', 'чел', 'чем', 'чер', 'что', 'чув', 'эти', 'это', 'юни', 'юно']
bigr_keys = ['ав', 'ак', 'ал', 'ам', 'ан', 'ап', 'ар', 'ат', 'аф', 'ба', 'бе', 'би', 'бл', 'бо', 'бр', 'бу', 'бы', 'ва', 'вв', 'вд', 'ве', 'вз', 'ви', 'вк', 'вл', 'вм', 'вн', 'во', 'вп', 'вр', 'вс', 'вт', 'вх', 'вч', 'вы', 'га', 'гд', 'ге', 'ги', 'гл', 'гн', 'го', 'гр', 'гу', 'да', 'дв', 'де', 'ди', 'дл', 'дн', 'до', 'др', 'ду', 'ды', 'дя', 'ев', 'ег', 'ед', 'ее', 'еж', 'ей', 'ем', 'еп', 'ес', 'ех', 'ещ', 'жа', 'жд', 'же', 'жи', 'жр', 'за', 'зв', 'зд', 'зе', 'зи', 'зл', 'зм', 'зн', 'зо', 'зр', 'иб', 'иг', 'ид', 'из', 'ил', 'им', 'ин', 'ио', 'ис', 'ит', 'их', 'ищ', 'ка', 'кв', 'ке', 'ки', 'кл', 'кн', 'ко', 'кр', 'кт', 'ку', 'ла', 'ле', 'ли', 'ло', 'лу', 'ль', 'лю', 'ма', 'ме', 'ми', 'мн', 'мо', 'мр', 'му', 'мы', 'мя', 'на', 'не', 'ни', 'но', 'нр', 'ну', 'ны', 'об', 'ов', 'ог', 'од', 'ож', 'оз', 'ок', 'ол', 'он', 'оп', 'ор', 'ос', 'от', 'ох', 'оч', 'ош', 'па', 'пе', 'пи', 'пл', 'по', 'пр', 'пу', 'пы', 'пь', 'пя', 'ра', 'ре', 'ри', 'ро', 'ру', 'ры', 'ря', 'са', 'сб', 'св', 'сд', 'се', 'сж', 'си', 'ск', 'сл', 'см', 'сн', 'со', 'сп', 'ср', 'ст', 'су', 'сх', 'сц', 'сч', 'сы', 'сю', 'та', 'тв', 'те', 'ти', 'то', 'тр', 'ту', 'тщ', 'ты', 'тю', 'тя', 'уб', 'ув', 'уг', 'уд', 'уе', 'уж', 'уз', 'ук', 'ул', 'ум', 'ун', 'уп', 'ур', 'ус', 'ут', 'ух', 'уч', 'уш', 'фа', 'фе', 'фи', 'фл', 'фо', 'фр', 'ха', 'хв', 'хи', 'хл', 'хо', 'хр', 'ху', 'ца', 'цв', 'це', 'ци', 'ча', 'че', 'чи', 'чл', 'чт', 'чу', 'ша', 'ше', 'ши', 'шк', 'шл', 'шу', 'ще', 'эл', 'эн', 'эт', 'юл', 'юн', 'юп', 'яв', 'яз', 'яр', 'яс']

PATH = os.curdir + '/filtered40000/'

list_names = os.listdir(PATH)

roots = []
for name in list_names:
    if not (name.endswith('.py') or name.endswith('.txt') or 'DS_Store' in name):
        roots.append(PATH + '/' + name)
print(roots)

label = 0

for t_path in roots:
    label += 1
    for root, dirs, files in os.walk(t_path):
        for filename in files:
            file_path = t_path + '/' + filename
            with open(file_path, 'r', encoding='utf-8') as f:
                print(file_path)
                text = f.read().lower()
                normalized_words = get_normalized_words(text)
                sharov_row = [normalized_words.count(word) / len(normalized_words) for word in sharov_keys]
                uni_row = [text.count(word) / len(text) for word in sorted(uni_keys)]
                punct_row = [text.count(word) / len(text) for word in sorted(punct_keys)]
                tri_row = [text.count(word) / len(text) for word in sorted(tri_keys)]
                bigr_row = [text.count(word) / len(text) for word in sorted(bigr_keys)]
                pos_row = [get_pos(x) for x in get_words(text)]
                pos = [pos_row.count(word) / len(pos_row) for word in sorted(pos_keys)]
                data = punct_row
                for x in pos:
                    data.append(x)
                for x in uni_row:
                    data.append(x)
                for x in bigr_row:
                    data.append(x)
                for x in tri_row:
                    data.append(x)
                for x in sharov_row:
                    data.append(x)
                final_data = normalize(data)
                final_data.insert(0, label)
                with open(t_path + ' features' + '.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)

                    writer.writerow(final_data)
                    csvfile.close()

col_names = ['label'] + sharov_keys + uni_keys + punct_keys + tri_keys + bigr_keys + pos_keys
all_files = glob.glob(os.path.join(PATH, "*features.csv"))
all_csv = (pd.read_csv(f, sep=',', names=col_names) for f in all_files)
df_merged = pd.concat(all_csv)
df_merged.to_csv("all_authors.csv")

