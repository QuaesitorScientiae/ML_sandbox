

def get_telegram_adv(user_name, Dir_Path= 'Set_A', iter_number=25, text_limit=True):
    '''
    :param user_name - Название телеграм канала:
    :param iter_number - Количество иттераций по дате публикации постов каждый шаг 20 постов max:
    :return:
    :text (str) - Текст постов канала (очищенный)
    web_names_set - список ссылок на внешние ресурсы, на которые ссылается канал
    telegram_names_set - список телеграм каналов на которые ссылантся канал
    set(lang) (set) - язык постов
    av_post_len - среднее значение символов в одном посте
    '''


    import requests
    from fake_useragent import UserAgent
    import random
    import time
    from bs4 import BeautifulSoup
    import re
    import os
    import io
    import json



    url = 'https://t.me/s/{}'.format(user_name)
    useragent = {'User-Agent': UserAgent().random}
    text = ''

    try:
        r = requests.get(url, headers=useragent)
        time.sleep(random.randrange(1, 10))
        text = get_text(r, user_name, Dir_Path)
        number = re.findall(r"data-post=\"{}\/(\d+)".format(user_name), r.text)
        # print(number)
        if not len(number) == 0:
            last_post_num = int(number[-1])
            post_num = last_post_num
            if last_post_num < (iter_number+1)*20:
                iter_number = last_post_num//20 - 1
            for items in range(iter_number):
                r = requests.get('https://t.me/s/{}?before={}'.format(user_name, post_num), headers=useragent)
                get_text(r,user_name + str(post_num), Dir_Path)
                time.sleep(random.randrange(1, 7))
                temp_posts = re.findall(r"data-post=\"{}\/(\d+)".format(user_name), r.text)
                post_num = int(temp_posts[0])-1

    except Exception as ex:
        print(ex)
        return

def get_text(r, filename, Dir_Path):
    # Извлечение текста
    from bs4 import BeautifulSoup
    import re
    text = ''
    text_post = ''
    soup = BeautifulSoup(r.text, 'lxml')
    popular = soup.find_all('div', {'class': 'tgme_widget_message_text'})
    iterr = 0
    for item in popular:
        soup_temp = BeautifulSoup(item.text, 'lxml')
        text_post = re.sub(r'https?:\/\/.*[\r\n]*', '', soup_temp.text, flags=re.MULTILINE)
        text = text + '\n'+ text_post
        if (len(text_post) > 150) and (len(text_post) < 2000) and (lang_detect(text_post) == 'ru'):
            try:
                with open('./telegram_Dataset/{}/@{}_telegram.txt'.format(Dir_Path, filename+'_'+str(iterr)), "w", encoding="utf-8") as some_file:
                    print(text_post, file=some_file)
                    some_file.close()
                    iterr = iterr+1
            except Exception as ex:
                print(ex)
    return text

def lang_detect (text = ''):
    # Определение языка канала
    from bs4 import BeautifulSoup
    from langdetect import detect
    import re

    if text !='':
        try:
            lang = detect(text[400:])
            print('Язык поста {}'.format(lang))
            return lang
        except Exception as ex:
            print(ex)
            return 'no text'
    else:
        return 'no text'

def pipline(content):
    import string
    import re
    from tokenizer_exceptions import normalizer_exc_rus
    print(content[:200])
    content = normalizer_exc_rus(content).lower()
    spec_chars = string.punctuation + '\xa0«»\t—…'
    content = re.sub('\n', ' ', content)
    content = re.sub('\r', ' ', content)
    content = remove_chars_from_text(content, spec_chars)
    content = remove_chars_from_text(content, string.digits)
    content = " ".join(content.split())
    print(content[:200])
    return content

def remove_chars_from_text(text, chars):
    # return "".join([ch for ch in text if ch not in chars])
    content = ''
    for ch in text:
        if ch not in chars:
            content = content + ''.join(ch)
        else:
            content = content + ''.join(' ')
    return content




def main():
    import os


    next_iter_names = {
        # 'china': ['maslovasia', 'china80s', 'raspp_info', 'prchand', 'awaken_dragon', 'asiatica_ru'],
        # 'africa': ['zangaro', 'africablack', 'natasakado_official', 'dnobangui', 'africafordummies', 'westernafrica', 'meskob', 'catcherinsudan', 'africanists'],
        # 'middleeast': ['syriaagency', 'turk_gambit_ca', 'shatergaddafi', 'turkkulubu', 'mideastr', 'tangermanar', 'marocrus', 'arabstatesofgulf', 'assadstash', 'meastru', 'strana_tuaregov']
        # 'latamerica': ['pqntc1', 'privetfidel', 'altimurla','favelasemrus', 'pincheponchito', 'laprimaveradelpatriarca', 'lat_america', 'tupireport', 'venezuelanewsnetwork', 'sputnikmundo']
        # 'news_ru': ['boris_rozhin', 'rt_russian', 'infantmilitario', 'svarschiki', 'divgen'],
        # 'news_ua': ['rezident_ua', 'taynaya_kantselyariya', 'the_military_analytics', 'spletnicca'],
        #'IranPakistanAfganistan': ['IranPakistanAfganistan', 'afgbezparandzhi'],
        'KNDR': ['RusEmbDPRK'],
        'Iran': ['irandezhurniy', 'paxIranica'],
        'Afganistan': ['afgbezparandzhi'],
        'Ethiopia': ['Ethiopia_tezeta', 'meskob'],
        #'Pakistan': [''],
        'China': ['maslovasia', 'china80s', 'raspp_info', 'prchand', 'awaken_dragon', 'asiatica_ru'],
        'India': ['india_tv2020', 'ninerasas', 'indiareads', 'speciallassi', 'indiaanalytics', 'Indosphere', 'India_sangrahalaya'],
        'Turkey': ['turkeyabout'],
        'Libya': ['ShaterGaddafi'],
        'Morocco': ['tangermanar', 'marocrus'],
        'Syria': ['NovostiDamask'],
        'CAR': ['dnobangui'],# Центрально-африканская Республика
        'Sudan': ['CatcherInSudan'],
        'Argentina': ['argentinarusa'],
    }

    for item in next_iter_names.keys():

        if not os.path.exists('./telegram_Dataset/{}'.format(item)):
            os.makedirs('./telegram_Dataset/{}'.format(item))


        for items in next_iter_names[item]:
            print('Канал {}'.format(items))
            get_telegram_adv(items, item)


if __name__ == '__main__':
    main()