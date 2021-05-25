import json
import re
import requests
import config


def get_iata(city):
    url = 'http://autocomplete.travelpayouts.com/places2?term=' + city + ''
    resp_text = requests.get(url).text

    iata = re.findall('"code": "([A-Z]{3})"', resp_text)
    if not iata:
        print('Совпадений не найдено!')
    else:
        return iata[0]


# get possible IATA codes from service backend
def get_iata_be(query):
    rq_url = "{}/autocomplete".format(config.BACKEND_ORIGIN)
    rq_params = {
        "term": query
    }
    return requests.get(rq_url, rq_params).json()


# get itineraries from backend by specified parameters
def get_itineraries_be(src_iata, dest_iata, outbound_from, outbound_to):
    rq_url = '{}/paths_for'.format(config.BACKEND_ORIGIN)
    rq_json = {
        "countryCode": "RU",
        "currencyCode": "RUB",
        "locale": "ru-RU",
        "originCode": src_iata,
        "destinationCode": dest_iata,
        "outboundDateFrom": [
            outbound_from.year,
            outbound_from.month,
            outbound_from.day
        ],
        "outboundDateTo": [
            outbound_to.year,
            outbound_to.month,
            outbound_to.day
        ],
        "adultsCount": 1,
        "childrenCount": 0,
        "infantsCount": 0,
        "typesAllowed": [
            "AIRCRAFT",
            "BUS",
            "TRAIN"
        ]
    }
    return requests.post(rq_url, json=rq_json).json()


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
