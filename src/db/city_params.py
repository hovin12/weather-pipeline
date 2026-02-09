from sqlalchemy import text
import logging


logger = logging.getLogger(__name__)


def iter_table(engine, table):
    logger.info(f"iterating table {table}")

    with engine.connect().execution_options(stream_results=True) as conn:
        result = conn.execute(text(f"SELECT * FROM {table}"))

        for row in result:
            yield row
