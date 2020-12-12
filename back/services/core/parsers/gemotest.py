import logging
from typing import NoReturn

from back.services.core.parsers.response_handler import send_request


def parse_gemotest() -> NoReturn:
    response = send_request(url='https://gemotest.ru/covid-19/assets/placemarks.json', payload={}, return_json=True)
    logging.info(response)
    for place in response.get('features'):
        print(f"Город: {place['properties']['description']['city']}\n"
              f"Адрес: {place['properties']['description']['address']}\n"
              f"Координаты: {place['geometry']['coordinates']}")
        print('--------')


if __name__ == '__main__':
    parse_gemotest()
