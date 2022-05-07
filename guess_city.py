import random
from flask import Flask, request
import logging
import json


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
    
    user_id = req['session']['user_id']
    data = storage[user_id]
    
    if data['cur'] < questions['count']:
        res['response']['text'] = "some problems.."
        res['response']['card'] = {
            'type': 'BigImage',
            'image_id': data['q'][data['cur']],
        }
        res['response']['buttons'] = [
            {
                'title': 'Помощь',
                "payload": {},
                "hide": True
            }
        ]
        
        if data['rigth_answer'] != None:
            is_rigth = req['request']['command'] == data['rigth_answer'].lower()
            res['response']['card']['title'] = ("Верно!" 
                                                if is_rigth
                                                else 'Неверно!')
            storage[user_id]['result'] += is_rigth
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

