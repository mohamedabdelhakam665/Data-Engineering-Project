
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import argparse


def extract_data():

    csv_path = Path("data/chicago_crimes.csv")

    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    print("Starting data extraction...")

    df = pd.read_csv(csv_path)

    print("Extraction completed successfully!")
    print(f"Total records: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")

    return df


def load_data(df, pg_host, target_table):

    print("Starting data loading...")

    engine = create_engine(
        f"postgresql+psycopg://root:root@{pg_host}:5432/chicago_crimes"
    )

    df.to_sql(
        name=target_table,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=10000
    )

    print("Data loading completed successfully!")

    engine.dispose()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--pg-host", required=True)
    parser.add_argument("--target-table", required=True)

    args = parser.parse_args()

    df = extract_data()

    load_data(
        df,
        pg_host=args.pg_host,
        target_table=args.target_table
    )
