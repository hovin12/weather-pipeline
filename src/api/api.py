import time
import logging
import requests
from src.api.mocks.mock_api import mock_weather_if_enabled

logger = logging.getLogger(__name__)


def api_call(session, url, params, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, params=params, timeout=30)
        except requests.exceptions.Timeout:
            logger.warning("Timeout error, retrying")
            time.sleep(1)
            continue
        except requests.exceptions.RequestException as e:
            logger.warning("Request error %s, retrying", e)
            time.sleep(5)
            continue

        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            logger.warning("Too many requests, retrying")
            time.sleep(60)
        else:
            logger.warning("%s, retrying", response.status_code)
            time.sleep(2**attempt)
    raise RuntimeError


@mock_weather_if_enabled
def get_current_weather(session: requests.Session, conn, lat, lon, retries=3):

    api_token = conn.password
    url = f"{conn.conn_type}://{conn.host}/weather"
    params = {"lat": lat, "lon": lon, "units": "metric", "appid": api_token}
    logger.info("Calling %s with %s", url, params)
    return api_call(session, url, params, retries=retries)
