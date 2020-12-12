from fake_useragent import UserAgent
import json
import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(retries: int = 3,
                           backoff_factor: float = 0.3,
                           status_forcelist: tuple = (429, 500, 502, 503, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session


def get_from_response(response, field: str) -> Optional[str]:
    response_dist = json.loads(response.text)
    status = response_dist.get(field)
    return status


def get_useragent() -> str:
    ua = UserAgent()
    random_user_agent = ua.random
    return random_user_agent


def send_request(url: str, payload: dict) -> json:
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    session.headers.update({'User-Agent': get_useragent()})
    response = requests_retry_session(session=session).get(url=url, data=json.dumps(payload))

    if response.status_code != 200:
        logging.error(f'paykassma response: {response.status_code} msg: {response.text}')
        return None
    else:
        return response.json()
