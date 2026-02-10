from sqlalchemy import text


def iter_table(engine, table):

    with engine.connect().execution_options(stream_results=True) as conn:
        result = conn.execute(text(f"SELECT * FROM {table}"))

        for row in result:
            yield row
