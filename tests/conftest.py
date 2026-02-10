import pytest
import subprocess


@pytest.fixture(scope="session", autouse=True)
def airflow_env():
    subprocess.run(
        ["docker", "compose", "-f", "docker-compose.test.yml", "up", "-d"],
        check=True,
    )

    yield

    subprocess.run(
        ["docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"], check=True
    )
