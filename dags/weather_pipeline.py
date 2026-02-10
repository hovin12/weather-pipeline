from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from src.db.bronze import ingest_rows
from src.db.silver import unpack_and_transfer


def ingest(*args, **kwargs):
    dag_run = get_current_context()["dag_run"]
    if dag_run.run_type == "manual":
        run_ts = dag_run.execution_date
    else:
        run_ts = dag_run.data_interval_end
    ingest_rows(run_ts, *args, **kwargs)


@dag(
    schedule="@hourly",
    start_date=datetime(2026, 1, 18, 19, 00, 00),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=1)},
)
def weather_pipeline():

    @task
    def ingest_cities_task():
        columns = {"run_ts": "timestamp", "city": "text", "payload": "jsonb"}
        ingest(source="cities", target="raw_results", columns=columns)

    @task
    def transfer_cities_task():
        unpack_and_transfer(
            source="raw_results", target="weather", pk=["run_ts", "city"]
        )

    @task
    def ingest_stations_task():
        columns = {
            "run_ts": "timestamp",
            "city": "text",
            "direction": "text",
            "payload": "jsonb",
        }
        ingest(source="stations", target="raw_stations", columns=columns)

    @task
    def transfer_stations_task():
        unpack_and_transfer(
            source="raw_stations",
            target="weather_stations",
            pk=["run_ts", "city", "direction"],
        )

    (
        ingest_cities_task()
        >> transfer_cities_task()
        >> ingest_stations_task()
        >> transfer_stations_task()
    )


dag = weather_pipeline()
