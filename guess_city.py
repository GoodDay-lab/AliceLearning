import random
from flask import Flask, request
import logging
import json
import requests
import math


app = Flask(__name__)
storage = {}
questions = {
    '1030494/6358ebfb2732813c1746': 'Париж',
    '997614/529b016475eb245d1387': 'Париж',
    '1652229/a4179ba6f690906effef': 'Нью-Йорк',
    '997614/c79728cb11e86d75ee94': 'Нью-Йорк',
    '213044/84d0f658561ff56a2e70': 'Москва',
    'count': 5
}


def get_coordinates(city_name):
    try:
        # url, по которому доступно API Яндекс.Карт
        url = "https://geocode-maps.yandex.ru/1.x/"
        # параметры запроса
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            # город, координаты которого мы ищем
            'geocode': city_name,
            # формат ответа от сервера, в данном случае JSON
            'format': 'json'
        }
        # отправляем запрос
        response = requests.get(url, params)
        # получаем JSON ответа
        json = response.json()
        # получаем координаты города
        # (там написаны долгота(longitude), широта(latitude) через пробел)
        # посмотреть подробное описание JSON-ответа можно
        # в документации по адресу https://tech.yandex.ru/maps/geocoder/
        coordinates_str = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        # Превращаем string в список, так как
        # точка - это пара двух чисел - координат
        long, lat = map(float, coordinates_str.split())
        # Вернем ответ
        return long, lat
    except Exception as e:
        return e


def get_distance(p1, p2):
    # p1 и p2 - это кортежи из двух элементов - координаты точек
    radius = 6373.0

    lon1 = math.radians(p1[0])
    lat1 = math.radians(p1[1])
    lon2 = math.radians(p2[0])
    lat2 = math.radians(p2[1])

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    distance = radius * c
    return distance


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
    

def make_response(req, res):
    if req['session']['new']:
        res['response']['text'] = "Привет! Меня зовут Алиса, пиши города!"
        return res
    
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    
    if not cities:
        res['response']['text'] = "Вы не написали ни один город!"
    
    elif len(cities) == 1:
        country = get_country(cities[0])
        
        res['response']['text'] = f"Этот город находится в стране - {country}"
    
    elif len(cities) == 2:
        coord1 = get_coordinates(cities[0])
        coord2 = get_coordinates(cities[1])
        distance = get_distance(coord1, coord2)
        
        res['response']['text'] = f"Дистанция между этими городами - {distance}"

    else:
        res['response']['text'] = "Очень много.. Это невозможно!"
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

