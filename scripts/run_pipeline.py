import os
import sys
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from clean_data import clean

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"

PG_HOST = os.getenv("PG_HOST", "localhost")
RAW_TABLE = os.getenv("RAW_TABLE", "public.chicago_crimes")   # غيّره لنفس --target-table

(ROOT / "logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(ROOT / "logs" / "pipeline.log", encoding="utf-8")],
)
log = logging.getLogger("pipeline")


class DataQualityError(Exception):
    pass


def get_engine():
    return create_engine(f"postgresql+psycopg://root:root@{PG_HOST}:5432/chicago_crimes")


def run_sql_file(engine, filename):
    sql = (SQL_DIR / filename).read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            conn.exec_driver_sql(stmt)


def run_quality_checks(engine):
    sql = (SQL_DIR / "quality_checks.sql").read_text(encoding="utf-8")
    sql = sql.replace("{RAW_TABLE}", RAW_TABLE).strip().rstrip(";")
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(sql).fetchall()

    failed = []
    for name, bad_count in rows:
        if bad_count > 0:
            log.error(f"FAIL | {name} | bad_count={bad_count}")
            failed.append(name)
        else:
            log.info(f"PASS | {name}")
    if failed:
        raise DataQualityError(f"Data quality checks failed: {failed}")
    log.info("All data quality checks passed")


def main():
    engine = get_engine()
    try:
        raw = pd.read_sql(f"SELECT * FROM {RAW_TABLE}", engine)
        df, stats = clean(raw)

        run_sql_file(engine, "01_create_tables.sql")
        df.to_sql("stg_crimes", engine, schema="clean", if_exists="replace",
                  index=False, chunksize=10000)
        run_sql_file(engine, "02_load_from_staging.sql")
        run_sql_file(engine, "03_analytical_views.sql")
        log.info(f"Loaded {len(df)} rows into clean schema")

        run_quality_checks(engine)
        log.info(f"PIPELINE SUCCESS | raw={stats['raw_rows']} clean={stats['clean_rows']}")
    except Exception as e:
        log.error(f"PIPELINE FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()