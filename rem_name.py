from locale import normalize
import random
from flask import Flask, request
import logging
import json
import requests
from api import get_translation

logging.basicConfig()

app = Flask(__name__)
storage = {}


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
    uuid = req['session']['user_id']
    
    if req['session']['new']:
        res['response']['text'] = 'Привет! Как тебя зовут?'
        return res
    
    if req['session']['message_id'] == 1:
        storage[uuid] = req['request']['nlu']['tokens'][0]
        res['response']['text'] = 'Приятно познакомиться! Меня зовут Alice'
        return res
    
    response = req['request']['command']
    word = response.replace("переведи слово ", '')
    translation = get_translation(word)
    res['response']['text'] = f"Ваш перевод: {translation} ({storage[uuid].capitalize()})"
    return res


app.run(port=8080)
