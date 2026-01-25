import requests
import time
import json
from datetime import datetime
from sqlalchemy import text
from src.db.connections import postgres_conn, api_credentials
from src.db.city_params import iter_cities
from src.api.api import get_current_weather
from src.api.validation import Validator


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "airflow/1.0",
        "Accept": "application/json"
    })
    return session


def save_result(engine, run_ts, city, record):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO raw_results (run_ts, city, payload)
                VALUES (:run_ts, :city, CAST(:payload AS jsonb))
                ON CONFLICT (run_ts, city) DO NOTHING
            """),
            {
                "run_ts": run_ts,
                "city": city,
                "payload": json.dumps(record)
            }
        )


def ingest_raw(run_ts: datetime):
    session = create_session()
    creds = api_credentials()
    engine = postgres_conn()
    for city, lat, lon in iter_cities(engine):
        record = get_current_weather(session, creds, lat, lon)
        Validator(record).validate()
        save_result(engine, run_ts, city, record)
        time.sleep(1.1)
