from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from src.db.bronze import ingest_raw

@dag(
    schedule="@hourly",
    start_date=datetime(2026, 1, 18, 19, 00, 00),
    catchup=False,
)
def weather_pipeline():

    @task
    def ingest_task():
        dag_run = get_current_context()["dag_run"]
        if dag_run.run_type == 'manual':
            run_ts = dag_run.execution_date
        else:
            run_ts = dag_run.data_interval_end
        ingest_raw(run_ts)

    ingest_task()

dag = weather_pipeline()
