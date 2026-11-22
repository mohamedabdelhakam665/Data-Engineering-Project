INSERT INTO clean.dim_iucr (iucr, primary_description, secondary_description)
SELECT DISTINCT ON (iucr) iucr, primary_description, secondary_description
FROM clean.stg_crimes
ORDER BY iucr;

INSERT INTO clean.dim_location (location_description)
SELECT DISTINCT location_description FROM clean.stg_crimes ORDER BY 1;

INSERT INTO clean.fact_crimes
    (case_number, crime_date, block, iucr, location_id, arrest, domestic,
     beat, ward, fbi_cd, latitude, longitude)
SELECT s.case_number, s.crime_date, s.block, s.iucr, l.location_id, s.arrest, s.domestic,
       s.beat, s.ward, s.fbi_cd, s.latitude, s.longitude
FROM clean.stg_crimes s
JOIN clean.dim_location l ON l.location_description = s.location_description;

DROP TABLE clean.stg_crimes;