from src.db.connections import postgres_conn


def unpack_and_transfer(source, target, pk):
    conn = postgres_conn()
    conn.run(f"""
        INSERT INTO {target}
        SELECT
            {', '.join(pk)},
            to_timestamp((payload->>'dt')::bigint) AS timestamp,
            to_timestamp((payload->'sys'->>'sunset')::bigint) AS sunset,
            to_timestamp((payload->'sys'->>'sunrise')::bigint) AS sunrise,
            (payload->'main'->>'temp')::decimal AS temp,
            (payload->'main'->>'temp_max')::decimal AS temp_max,
            (payload->'main'->>'temp_min')::decimal AS temp_min,
            (payload->'main'->>'feels_like')::decimal AS perceived_temp,
            (payload->'main'->>'humidity')::int AS humidity,
            (payload->'main'->>'pressure')::int AS pressure,
            (payload->'main'->>'grnd_level')::int AS pressure_ground,
            (payload->'wind'->>'deg')::int AS wind_deg,
            (payload->'wind'->>'speed')::decimal AS wind_speed,
            (payload->'wind'->>'gust')::decimal AS wind_gust,
            (payload->'clouds'->>'all')::int AS clouds,
            (payload->'rain'->>'1h')::decimal AS rain,
            (payload->'snow'->>'1h')::decimal AS snow,
            (payload->'weather'->0->>'main')::varchar AS label,
            (payload->'weather'->0->>'description')::varchar AS description,
            (payload->>'visibility')::int AS visibility
        FROM {source};
        
        DELETE FROM {source};
        """)
