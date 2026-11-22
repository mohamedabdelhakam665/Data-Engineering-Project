import sys
from run_pipeline import get_engine, run_quality_checks, DataQualityError

engine = get_engine()
with engine.begin() as conn:
    conn.exec_driver_sql("""
        INSERT INTO clean.fact_crimes
            (case_number, crime_date, iucr, location_id, ward, latitude, longitude)
        VALUES ('TEST_BAD', NOW() + INTERVAL '10 days',
                (SELECT MIN(iucr) FROM clean.dim_iucr),
                (SELECT MIN(location_id) FROM clean.dim_location),
                99, 10.0, -87.6)
    """)
try:
    run_quality_checks(engine)
    print("UNEXPECTED: bad data was not detected")
    code = 0
except DataQualityError as e:
    print(f"EXPECTED FAILURE: {e}")
    code = 1
finally:
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM clean.fact_crimes WHERE case_number = 'TEST_BAD'")
sys.exit(code)