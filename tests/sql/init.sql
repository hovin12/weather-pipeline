
CREATE TABLE IF NOT EXISTS raw_results (
    run_ts TIMESTAMP,
    city VARCHAR,
    payload JSONB
);

ALTER TABLE raw_results ADD PRIMARY KEY (run_ts, city);

CREATE TABLE IF NOT EXISTS weather (
    run_ts TIMESTAMP,
    city VARCHAR,
    timestamp TIMESTAMP,
    sunset TIMESTAMP,
    sunrise TIMESTAMP,
    temp DECIMAL,
    temp_max DECIMAL,
    temp_min DECIMAL,
    perceived_temp DECIMAL,
    humidity INT,
    pressure INT,
    pressure_ground INT,
    wind_deg INT,
    wind_speed DECIMAL,
    wind_gust DECIMAL,
    clouds INT,
    rain DECIMAL,
    snow DECIMAL,
    label VARCHAR,
    description VARCHAR,
    visibility INT
);

ALTER TABLE weather ADD PRIMARY KEY (run_ts, city);

CREATE TABLE cities (
    city VARCHAR,
    lat DECIMAL,
    lon DECIMAL
);

COPY cities
FROM '/data/cities.csv'
WITH (FORMAT csv, HEADER true);
