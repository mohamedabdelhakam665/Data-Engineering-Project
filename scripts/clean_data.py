import re
import logging
from datetime import datetime
import pandas as pd

log = logging.getLogger("clean")

REQUIRED = ["case_number", "date_of_occurrence", "block", "iucr", "primary_description",
            "secondary_description", "location_description", "arrest", "domestic",
            "beat", "ward", "fbi_cd", "latitude", "longitude"]

BOOL_MAP = {"y": True, "n": False}


def clean(raw):
    stats = {"raw_rows": len(raw)}
    df = raw.copy()

    # normalize column names: " PRIMARY DESCRIPTION" -> primary_description, "CASE#" -> case_number
    df.columns = [re.sub(r"\W+", "_", c.replace("#", "_number").strip().lower()).strip("_")
                  for c in df.columns]

    # pre-load checks
    if df.empty:
        raise ValueError("Raw table is empty")
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = df[REQUIRED].copy()

    # strings: trim, empty -> NULL, uppercase
    for c in ["case_number", "block", "iucr", "primary_description", "secondary_description",
              "location_description", "fbi_cd"]:
        df[c] = df[c].astype("string").str.strip().replace("", pd.NA).str.upper()
    df["location_description"] = df["location_description"].fillna("UNKNOWN")

    # data types
    df["crime_date"] = pd.to_datetime(df.pop("date_of_occurrence"),
                                      format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    for c in ["beat", "ward"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    for c in ["latitude", "longitude"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["arrest", "domestic"]:
        df[c] = df[c].astype("string").str.strip().str.lower().map(BOOL_MAP).astype("boolean")

    # missing key values -> drop row
    before = len(df)
    df = df.dropna(subset=["case_number", "crime_date", "iucr", "primary_description"])
    stats["dropped_missing_key"] = before - len(df)

    # future dates -> drop row
    before = len(df)
    df = df[df["crime_date"] <= datetime.now()]
    stats["dropped_future_dates"] = before - len(df)

    # duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["case_number", "crime_date", "iucr"], keep="first")
    stats["dropped_duplicates"] = before - len(df)

    # invalid ward (valid is 1-50) -> NULL, row kept
    bad_ward = df["ward"].notna() & ~df["ward"].between(1, 50)
    df.loc[bad_ward, "ward"] = pd.NA
    stats["ward_set_null"] = int(bad_ward.sum())

    stats["clean_rows"] = len(df)
    log.info(f"Cleaning stats (before/after): {stats}")
    return df, stats