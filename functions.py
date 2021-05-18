import json
import re
import dateparser
import datetime
import requests


def get_iata(city):
    url = 'http://autocomplete.travelpayouts.com/places2?term=' + city + ''
    resp_text = requests.get(url).text

    iata = re.findall('"code": "([A-Z]{3})"', resp_text)
    if not iata:
        print('Совпадений не найдено!')
    else:
        return iata[0]


def get_url(departure_iata, arrival_iata, day_month):
    base = 'https://www.aviasales.ru/search/'
    res = base + departure_iata + day_month + arrival_iata
    return res


def get_price_one_way(departure_iata, arrival_iata):
    link = f'http://min-prices.aviasales.ru/calendar_preload?one_way=true&origin={departure_iata}&destination={arrival_iata}'
    data = json.loads(requests.get(link).text)
    if data['best_prices']:
        return data['best_prices'][0]
    else:
        return None
