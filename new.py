from locale import normalize
import random
from flask import Flask, request
import logging
import json
import requests

logging.basicConfig()

app = Flask(__name__)
storage = {}
questions = {
    '1030494/6358ebfb2732813c1746': 'Париж',
    '1652229/a4179ba6f690906effef': 'Нью-Йорк',
    '213044/84d0f658561ff56a2e70': 'Москва',
    'count': 3
}

expecting_country = False
city_for_country = ""

def normalize_answer(string):
    return string.replace(' ', '')


@app.route("/post", methods=["POST"])
def handle_request():
    logging.info("Got a request..")
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    response = make_response(request.json, response)
    logging.info("Maked a response..")
    return json.dumps(response)
    

def get_country(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': city_name,
            'format': 'json'
        }
        data = requests.get(url, params).json()
        # все отличие тут, мы получаем имя страны
        return data['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['AddressDetails']['Country']['CountryName']
    except Exception as e:
        return e


def make_response(req, res):
    global expecting_country, city_for_country
    if req['session']['new']:
        res['response']['text'] = "Привет! Меня зовут Алиса, давай сыграем?"
        res['response']['buttons'] = [
        {
            'title': 'Да',
            'hide': True
        },
        {
            'title': 'Нет',
            'hide': True
        }
        ]
        return res

    if expecting_country:
        country = ""
        logging.info("I AM HERE")
        for ent in req['request']['nlu']['entities']:
            if ent['type'] == 'YANDEX.GEO':
                if 'country' in ent['value']:
                    country = ent['value']['country']
                    break
        if country == get_country(city_for_country).lower():
            res['response']['text'] = "Правильно!!"
        else:
            res['response']['text'] = 'Неверно!'
        expecting_country = False
        return res
    
    if "помощь" in req['request']['nlu']['tokens']:
        res['response']['text'] = \
        """
            Чтобы выиграть, вам надо правильно называть города,
            кстати, сейчас ваш ход: (пишите)
        """
        return res
    
    if 'да' in req['request']['command']:
        init_game(req['session']['user_id'])
    elif 'нет' in req['request']['command']:
        res['response']['text'] = "Раз нет, значит, нет.."
        res['response']['end_session'] = True
        return res
    
    city = ""
    for ent in req['request']['nlu']['entities']:
        if ent['type'] == 'YANDEX.GEO':
            if 'city' in ent['value']:
                city = ent['value']['city']
                break
    
    user_id = req['session']['user_id']
    data = storage[user_id]
    res['response']['buttons'] = []
           
    if data['rigth_answer'] != None:
        is_rigth = city == data['rigth_answer'].lower()
        logging.warning(data['rigth_answer'])
        if is_rigth:
            expecting_country = True
            city_for_country = city
            res['response']['text'] = "А назовите ещё и страну, в которой находится этот город!"
            storage[user_id]['result'] += is_rigth
            return res
        else:
            pass
        res['response']['buttons'].append({
                'title': 'Помощь',
                "payload": {},
                "hide": True
            })
    
    if data['cur'] < questions['count']:
        if 'card' not in res['response']:
            res['response']['card'] = {}
        logging.warning(data['q'][data['cur']])
        res['response']['text'] = "some problems.."
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = data['q'][data['cur']]
        data['rigth_answer'] = questions[data['q'][data['cur']]]
        data['cur'] += 1
        return res
    else:
        res['response']['text'] = f"Вы прошли! С результатом {data['result']}"
        res['response']['end_session'] = True
        return res


def init_game(user_id):
    list_ = list(questions.keys())
    random.shuffle(list_)
    storage[user_id] = {
        'q': list_,
        'cur': 0,
        'rigth_answer': None,
        'result': 0
    }
    return


app.run(port=8080)

