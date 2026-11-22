CREATE SCHEMA IF NOT EXISTS clean;

DROP TABLE IF EXISTS clean.fact_crimes CASCADE;
DROP TABLE IF EXISTS clean.dim_iucr CASCADE;
DROP TABLE IF EXISTS clean.dim_location CASCADE;

CREATE TABLE clean.dim_iucr (
    iucr                  TEXT PRIMARY KEY,
    primary_description   TEXT NOT NULL,
    secondary_description TEXT
);

CREATE TABLE clean.dim_location (
    location_id          SERIAL PRIMARY KEY,
    location_description TEXT NOT NULL UNIQUE
);

CREATE TABLE clean.fact_crimes (
    crime_id    SERIAL PRIMARY KEY,
    case_number TEXT NOT NULL,
    crime_date  TIMESTAMP NOT NULL,
    block       TEXT,
    iucr        TEXT NOT NULL REFERENCES clean.dim_iucr(iucr),
    location_id INT  NOT NULL REFERENCES clean.dim_location(location_id),
    arrest      BOOLEAN,
    domestic    BOOLEAN,
    beat        INT,
    ward        INT,
    fbi_cd      TEXT,
    latitude    DOUBLE PRECISION,
    longitude   DOUBLE PRECISION,
    CONSTRAINT uq_crime_natural_key UNIQUE (case_number, crime_date, iucr)
);