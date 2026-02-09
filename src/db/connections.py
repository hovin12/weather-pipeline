from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def postgres_conn():
    hook = PostgresHook(postgres_conn_id="POSTGRES_CONN")
    return hook.get_sqlalchemy_engine()

def api_credentials():
    conn = BaseHook.get_connection("CURRENT_WEATHER_API")
    return conn
