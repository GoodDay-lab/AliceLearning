import random
from flask import Flask, request
import logging
import json

logging.basicConfig(
    filename="server.log"
)

app = Flask(__name__)
storage = {}
questions = {
    '1030494/6358ebfb2732813c1746': 'Париж',
    '997614/529b016475eb245d1387': 'Париж',
    '1652229/a4179ba6f690906effef': 'Нью-Йорк',
    '997614/c79728cb11e86d75ee94': 'Нью-Йорк',
    '1533899/0a547d94785e38d6f477': 'Москва',
    '1521359/1a1ae17f3c8b531490e6': 'Москва',
    'count': 6
}


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
    return json.dump(response)
    

def make_response(req, res):
    if 'прив' in req['request']['text']:
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
    
    if 'да' in req['request']['text']:
        init_game(req['session']['user_id'])
    elif 'нет' in req['request']['text']:
        res['response']['text'] = "Раз нет, значит, нет.."
        res['response']['end_session'] = True
        return res
    
    user_id = req['session']['user_id']
    data = storage[user_id]
    if data['cur'] < questions['count']:
        res['response']['card'] = {
            'type': 'BitImage',
            'image_id': data[data['cur']],
            'title': 'Угадайте город!',
            'buttons': [
            {
                'title': 'Москва',
                'payload': {'answer': 'Москва'}
            },
            {
                'title': 'Париж',
                'payload': {'answer': 'Париж'}
            },
            {
                'title': 'Нью-Йорк',
                'payload': {'answer': 'Нью-Йорк'}
            }]
        }
        return res
    else:
        res['response']['end_session'] = True
        return res


def init_game(user_id):
    storage[user_id] = {
        'q': random.shaffle(list(questions.keys())),
        'cur': 0
    }
    return


if __name__ == '__main__':
    app.run(port=443)

