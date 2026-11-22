CREATE OR REPLACE VIEW clean.v_crimes_by_type AS
SELECT d.primary_description, COUNT(*) AS total_crimes
FROM clean.fact_crimes f
JOIN clean.dim_iucr d ON d.iucr = f.iucr
GROUP BY d.primary_description;

CREATE OR REPLACE VIEW clean.v_arrest_rate_by_type AS
SELECT d.primary_description,
       COUNT(*) AS total_crimes,
       ROUND(100.0 * SUM(CASE WHEN f.arrest THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_pct
FROM clean.fact_crimes f
JOIN clean.dim_iucr d ON d.iucr = f.iucr
GROUP BY d.primary_description;

CREATE OR REPLACE VIEW clean.v_crimes_by_location AS
SELECT l.location_description, COUNT(*) AS total_crimes
FROM clean.fact_crimes f
JOIN clean.dim_location l ON l.location_id = f.location_id
GROUP BY l.location_description;