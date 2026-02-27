# Weather Pipeline

A Python-based weather data pipeline that fetches current weather data from an external API, processes it, 
and stores it in a PostgreSQL database. It uses Airflow as the orchestration tool.

---

## Features

* Fetches weather data from an external HTTP API
* Stores structured weather data in PostgreSQL
* Configurable via environment variables
* Ready for local development and testing

### Features in development

* ML model to forecast 24h weather
* Golden layer of aggregated data ready to use for weather report
* UI to show weather report

---

## Architecture (High Level)

```text
External Weather API
        ↓
Data Fetch Layer
        ↓
Validation
        ↓
PostgreSQL Database
```

The pipeline is intentionally modular so individual components (API client, processing logic, database layer) 
can be tested and replaced independently.

---

## Requirements

* Python 3.12+
* Docker & Docker Compose

---

## Project Structure

```text
dags/                   # Dag definitions
src/
  api/
    mocks/              # API mock for testing purposes
    api.py              # External API clients
    validation.py       # Response schema validation
  db/                   # Database connections and queries
    connections.py      # Creates connections using Airflow Hooks
    bronze.py           # Reads raw data and stores in Postgres DB
    silver.py           # Transforms raw data and stores in Postgres DB
  templates/
    builders.py         # Creates html for the webpage

tests/
  conftest.py           # Sets up docker-compose for tests
  test_weather_dag.py   # Interation test: Airflow + Docker + mocked API

init.sql                # SQL query to create tables in Postgres
.env.example
.env.test
requirements.txt
pyproject.toml
docker-compose.yml
docker-compose.test.yml
README.md
```

---

## Configuration

This project uses environment variables for configuration.

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Update values in `.env` (API keys, database connection, etc.).

---

## Running the Project

```bash
docker-compose up -d
```

---

## Database

PostgreSQL is used as the primary data store.

---

## Code Quality

This project uses automated tools to ensure consistent code quality:

* **Black** – code formatting
* **Pylint** – linter
