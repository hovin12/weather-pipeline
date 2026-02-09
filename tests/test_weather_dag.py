import subprocess
import time
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv('.env.test')


def wait_for_container(service_name='airflow', timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        result = subprocess.run(
            ["docker", "compose", "ps", "--status", "running", "--services"],
            capture_output=True,
            text=True
        )
        running_services = result.stdout.splitlines()
        if service_name in running_services:
            return
        time.sleep(1)
    raise TimeoutError(f"Service '{service_name}' did not start within {timeout}s")


def trigger_task(dag_id, task_id):
    subprocess.run(
        [
            "docker", "compose", "-f", "docker-compose.test.yml",
            "exec", "-T", "airflow", "airflow", "tasks", "test",
            dag_id, task_id, datetime.now().strftime('%Y-%m-%d')
        ],
        check=True
    )


def test_weather_pipeline(airflow_env):

    wait_for_container()

    trigger_task("weather_pipeline", "ingest_cities_task")
    time.sleep(5)
    trigger_task("weather_pipeline", "transfer_cities_task")

    engine = create_engine(
        os.getenv('PYTEST_SQL_CONN')
    )

    with engine.begin() as conn:
        cur = conn.execute(text("SELECT temp FROM weather"))

    assert cur.fetchone()
