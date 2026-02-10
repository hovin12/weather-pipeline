import json
import math
import os
from pathlib import Path
from functools import wraps


BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / 'responses.json', 'r', encoding='utf-8') as f:
    mocked_responses = json.load(f)


def find_response(lat, lon):
    g = (
        (k, v) for k, v in mocked_responses.items() if
        math.isclose(lat, v['coord']['lat'], abs_tol=0.01) and
        math.isclose(lon, v['coord']['lon'], abs_tol=0.01)
    )
    try:
        return next(iter(g))
    except StopIteration:
        return None, {}


def mocked_weather(session, creds, lat, lon):
    _, response = find_response(lat, lon)
    return response


def mock_weather_if_enabled(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.getenv('MOCK_EXTERNAL_APIS', '').lower() in {'true', 'yes', '1'}:
            return mocked_weather(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


if __name__ == '__main__':
    import pandas as pd
    cities = pd.read_csv(BASE_DIR / '.cities.csv')
    for _, row in cities.iterrows():
        city, result = find_response(row['lat'], row['lon'])
        assert row['city'] == city
