import json
import re
from typing import NoReturn

from bs4 import BeautifulSoup

from back.services.core.parsers.response_handler import send_request


def get_cites() -> dict:
    response = send_request(url=f'https://citilab.ru/local/components/reaspekt/reaspekt.geoip/'
                                f'templates/my01/ajax_popup_city.php', payload={}, return_json=False)
    city_names = re.findall(r'(?<=title=\").*?(?=\")', response.text)
    city_codes = re.findall(r'(?<=data-code=").*?(?=\")', response.text)
    cites = dict(zip(city_codes, city_names))
    return cites


def parse_citilab() -> NoReturn:
    cites = get_cites()
    for code, city in cites.items():
        response = send_request(url=f'https://citilab.ru/{code}/medcentres/', payload={}, return_json=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            data = soup.find_all('script')[42].string
        except IndexError:
            data = soup.find_all('script')[40].string

        json_data_raw = re.findall('(?<=var jsonData = ).*$', data)[0][:-1].replace('\'', '"')
        json_data = json.loads(json_data_raw)
        for place in json_data.get('mark'):
            print(f"Город : {city}\n"
                  f"Корона : {place['covid']}\n"
                  f"Адрес: {place['adr']}\n"
                  f"Координаты: {place['lat']} : {place['lng']}")
            print('--------')


if __name__ == '__main__':
    parse_citilab()
