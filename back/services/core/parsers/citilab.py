import json
import re
from typing import NoReturn

from bs4 import BeautifulSoup

from back.services.core.parsers.response_handler import send_request
from back.services.core.parsers.database_handler import TestPlacePusher
from back.services.core.settings import DB_HOST, DB_LOGIN, DB_DATABASE, DB_PASSWORD

PRICE = 1980
TIME_TILL_RES_DAYS = 3

def get_cites() -> dict:
    response = send_request(url=f'https://citilab.ru/local/components/reaspekt/reaspekt.geoip/'
                                f'templates/my01/ajax_popup_city.php', payload={}, return_json=False)
    city_names = re.findall(r'(?<=title=\").*?(?=\")', response.text)
    city_codes = re.findall(r'(?<=data-code=").*?(?=\")', response.text)
    cites = dict(zip(city_codes, city_names))
    return cites


def parse_citilab() -> NoReturn:
    db_pusher = TestPlacePusher(DB_HOST, DB_LOGIN, DB_PASSWORD, DB_DATABASE)
    med_org = db_pusher.get_or_add_med_org('Citilab')
    cites = get_cites()
    for code, city in cites.items():
        db_pusher.get_or_add_city(city)

        response = send_request(url=f'https://citilab.ru/{code}/medcentres/', payload={}, return_json=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            data = soup.find_all('script')[42].string
        except IndexError:
            data = soup.find_all('script')[40].string

        json_data_raw = re.findall('(?<=var jsonData = ).*$', data)[0][:-1].replace('\'', '"')
        json_data = json.loads(json_data_raw)

        for place in json_data.get('mark'):
            if place['covid'] != '1':
                continue
            address = place['adr']
            coord = {'lat': place['lat'], 'lon': place['lng']}
            url = f'https://citilab.ru/{place["url"]}'
            db_pusher.add_test_place(city=city, med_org='Citilab', address=address, position=coord, url=url)
            print(f"Город : {city}\n"
                  f"Корона : {place['covid']}\n"
                  f"Адрес: {place['adr']}\n"
                  f"Координаты: {place['lat']} : {place['lng']}\n"
                  f"Цена: {PRICE}\n"
                  f"Срок готовности результатов: {TIME_TILL_RES_DAYS}")
            print('--------')


if __name__ == '__main__':
    parse_citilab()
