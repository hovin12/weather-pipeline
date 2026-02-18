from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def postgres_hook():
    hook = PostgresHook(postgres_conn_id="POSTGRES_CONN")
    return hook


def api_credentials():
    conn = BaseHook.get_connection("CURRENT_WEATHER_API")
    return conn
