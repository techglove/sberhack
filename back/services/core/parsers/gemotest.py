import logging
import re
from typing import NoReturn

from back.services.core.parsers.database_handler import TestPlacePusher
from back.services.core.parsers.response_handler import send_request
from back.services.core.settings import DB_HOST, DB_LOGIN, DB_DATABASE, DB_PASSWORD


def parse_gemotest() -> NoReturn:
    response = send_request(url='https://gemotest.ru/covid-19/assets/placemarks.json', payload={}, return_json=True)
    logging.info(response)
    db_pusher = TestPlacePusher(DB_HOST, DB_LOGIN, DB_PASSWORD, DB_DATABASE)
    db_pusher.get_or_add_med_org('Gemotest')
    for place in response.get('features'):
        city = place['properties']['description']['city']

        coordinates_raw = place['geometry']['coordinates']
        coordinates = {'lat': coordinates_raw[0], 'lon': coordinates_raw[1]}

        address = place['properties']['description']['address']

        pcr_test_price_raw = place['properties']['description']['features'][0]['price'].replace(' ', '')\
            .replace(u'\xa0', '')
        pcr_test_price = str(sum([int(s) for s in re.findall(r'-?\d+\.?\d*', pcr_test_price_raw)]))

        antibodies_test_price = '900'
        time_of_completion_raw = place['properties']['description']['features'][0]['title']
        time_of_completion = re.search(r'(?<=тест за )[^.]*', time_of_completion_raw).group(0)
        db_pusher.get_or_add_city(city)
        db_pusher.add_test_place(city=city,
                                 med_org='Gemotest',
                                 address=address,
                                 position=coordinates,
                                 url='https://gemotest.ru/',
                                 pcr_test_price=pcr_test_price,
                                 antibodies_test_price=antibodies_test_price,
                                 time_of_completion=time_of_completion)
        print(f"Город: {place['properties']['description']['city']}\n"
              f"Адрес: {place['properties']['description']['address']}\n"
              f"Координаты: {place['geometry']['coordinates']}")
        print('--------')


if __name__ == '__main__':
    parse_gemotest()
