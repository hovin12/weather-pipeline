from sqlalchemy import text


def iter_cities(engine):

    with engine.connect().execution_options(stream_results=True) as conn:
        result = conn.execute(text("SELECT * FROM cities"))

        for row in result:
            yield row.city, row.lat, row.lon
