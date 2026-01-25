from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def postgres_conn():
    hook = PostgresHook(postgres_conn_id="postgres-conn")
    return hook.get_sqlalchemy_engine()

def api_credentials():
    conn = BaseHook.get_connection("current-weather-api")
    return conn
