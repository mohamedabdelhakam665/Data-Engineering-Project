# Data Quality Rules

## Python pre-load checks (scripts/clean_data.py)
| Rule | On failure |
|---|---|
| Raw table not empty | Exception, exit 1 |
| All required columns exist | Exception, exit 1 |

## SQL post-load checks (sql/quality_checks.sql)
| Check | Threshold | On failure |
|---|---|---|
| pk_duplicates | 0 | log ERROR, exit 1 |
| fk_orphan_iucr / fk_orphan_location | 0 | log ERROR, exit 1 |
| null_crime_date | 0 | log ERROR, exit 1 |
| null_latitude_over_5pct | <= 5% null | log ERROR, exit 1 |
| ward_out_of_range | ward 1..50 | log ERROR, exit 1 |
| lat_lon_out_of_range | lat 41-43, lon -89..-87 | log ERROR, exit 1 |
| future_dates | 0 | log ERROR, exit 1 |
| clean_table_empty | > 0 rows | log ERROR, exit 1 |
| clean_more_than_raw | clean <= raw | log ERROR, exit 1 |
| clean_lost_over_20pct | clean >= 80% of raw | log ERROR, exit 1 |

## Test results
- Clean run: all checks PASS (الصق من logs/pipeline.log)
- Bad-data run (test_bad_data.py): ward_out_of_range, lat_lon_out_of_range, future_dates FAIL, exit code 1 (الصق اللوج)