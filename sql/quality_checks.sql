SELECT 'pk_duplicates' AS check_name, COUNT(*) - COUNT(DISTINCT crime_id) AS bad_count
FROM clean.fact_crimes
UNION ALL
SELECT 'fk_orphan_iucr', COUNT(*)
FROM clean.fact_crimes f LEFT JOIN clean.dim_iucr d ON d.iucr = f.iucr
WHERE d.iucr IS NULL
UNION ALL
SELECT 'fk_orphan_location', COUNT(*)
FROM clean.fact_crimes f LEFT JOIN clean.dim_location l ON l.location_id = f.location_id
WHERE l.location_id IS NULL
UNION ALL
SELECT 'null_crime_date', COUNT(*) FROM clean.fact_crimes WHERE crime_date IS NULL
UNION ALL
SELECT 'null_latitude_over_5pct',
       CASE WHEN COUNT(*) = 0 THEN 1
            WHEN 100.0 * COUNT(*) FILTER (WHERE latitude IS NULL) / COUNT(*) > 5 THEN 1
            ELSE 0 END
FROM clean.fact_crimes
UNION ALL
SELECT 'ward_out_of_range', COUNT(*) FROM clean.fact_crimes
WHERE ward IS NOT NULL AND ward NOT BETWEEN 1 AND 50
UNION ALL
SELECT 'lat_lon_out_of_range', COUNT(*) FROM clean.fact_crimes
WHERE latitude NOT BETWEEN 41 AND 43 OR longitude NOT BETWEEN -89 AND -87
UNION ALL
SELECT 'future_dates', COUNT(*) FROM clean.fact_crimes WHERE crime_date > NOW()
UNION ALL
SELECT 'clean_table_empty', CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END FROM clean.fact_crimes
UNION ALL
SELECT 'clean_more_than_raw',
       CASE WHEN (SELECT COUNT(*) FROM clean.fact_crimes) > (SELECT COUNT(*) FROM {RAW_TABLE}) THEN 1 ELSE 0 END
UNION ALL
SELECT 'clean_lost_over_20pct',
       CASE WHEN (SELECT COUNT(*) FROM clean.fact_crimes) < 0.8 * (SELECT COUNT(*) FROM {RAW_TABLE}) THEN 1 ELSE 0 END;