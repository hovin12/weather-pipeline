import logging
import requests
import time


logger = logging.getLogger(__name__)


def api_call(session, url, params, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=30)
        except requests.exceptions.ConnectionError:
            logger.warning("Connection error, retrying")
            time.sleep(5)
            continue

        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            logger.warning("Too many requests, retrying")
            time.sleep(5)
        else:
            logger.warning(f"{response.status_code}, retrying")
            time.sleep(2 ** attempt)
    raise RuntimeError


def get_current_weather(session: requests.Session, creds, lat, lon, retries=3):
    api_token = creds.password
    base_url = creds.host
    params = {
        'lat': lat,
        'lon': lon,
        'units': 'metric',
        'appid': api_token
    }
    return api_call(session, base_url, params, retries=retries)
