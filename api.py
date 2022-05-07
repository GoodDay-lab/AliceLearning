import requests


XAPIHOST = "translated-mymemory---translation-memory.p.rapidapi.com"
XAPIKEY = "1dd1dc9f5dmsh0b413011654feccp1cbeedjsn5e2241e4f5b5"


def get_translation(word, translation="ru|en"):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    params = {
        'q': word,
        'langpair': translation,
        'onlyprivate': '0',
        'mt': '1'
    }
    headers = {
        'X-RapidAPI-Host': XAPIHOST,
        'X-RapidAPI-Key': XAPIKEY
    }
    response = requests.get(url, params=params, headers=headers).json()
    return response['responseData']['translatedText']
