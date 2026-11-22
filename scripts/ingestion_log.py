from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def log_ingestion(source, status, records, started_at, pg_host, error=None):
    finished_at = datetime.now()
    msg = (f"source={source} | status={status} | records_fetched={records} | "
           f"started={started_at:%Y-%m-%d %H:%M:%S} | finished={finished_at:%Y-%m-%d %H:%M:%S} | error={error}")
    print(msg)

    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "ingestion.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

    try:
        engine = create_engine(f"postgresql+psycopg://root:root@{pg_host}:5432/chicago_crimes")
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ingestion_log (
                    id SERIAL PRIMARY KEY, source TEXT, status TEXT, records_fetched BIGINT,
                    started_at TIMESTAMP, finished_at TIMESTAMP, error TEXT)
            """))
            conn.execute(text("""
                INSERT INTO ingestion_log (source, status, records_fetched, started_at, finished_at, error)
                VALUES (:s, :st, :r, :a, :f, :e)
            """), {"s": source, "st": status, "r": records, "a": started_at, "f": finished_at, "e": error})
        engine.dispose()
    except Exception as e:
        print(f"WARNING: could not write ingestion_log table: {e}")