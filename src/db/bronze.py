import requests
import json
from datetime import datetime
import logging
from src.db.connections import postgres_conn, api_credentials
from src.db.city_params import iter_table
from src.api.api import get_current_weather
from src.api.validation import Validator

logger = logging.getLogger(__name__)


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "airflow/1.0",
        "Accept": "application/json"
    })
    return session


def save_result(engine, table: str, columns: dict, values: list):
    placeholders = ", ".join(f"%s::{dtype}" for dtype in columns.values())
    sql = f"""
    INSERT INTO {table} ({', '.join(columns)})
    VALUES ({placeholders})
    """
    assert all(len(sub) == len(columns) for sub in values)
    with engine.begin() as conn:
        conn.execute(sql, values)


def batched(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def response_generator(session, engine, creds, table, run_ts):
    for *pk, lat, lon in iter_table(engine, table):
        record = get_current_weather(session, creds, lat, lon)
        Validator(record).validate()
        json_record = json.dumps(record)
        yield [run_ts] + pk + [json_record]


def ingest_rows(run_ts: datetime, source: str, target: str, columns: dict):
    session = create_session()
    creds = api_credentials()
    engine = postgres_conn()

    logger.info('start ingesting rows')
    response_iterable = response_generator(session, engine, creds, source, run_ts)
    for batch in batched(response_iterable, size=100):
        logger.info(f"batch: {batch}")
        save_result(engine=engine, table=target, columns=columns, values=batch)
