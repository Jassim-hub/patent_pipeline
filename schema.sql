-- schema.sql
-- Database schema for Patent Pipeline

-- 1. DROP EXISTING TABLES
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

DROP TABLE IF EXISTS stg_patent;
DROP TABLE IF EXISTS stg_abstract;
DROP TABLE IF EXISTS stg_application;
DROP TABLE IF EXISTS stg_inventor;
DROP TABLE IF EXISTS stg_assignee;
DROP TABLE IF EXISTS stg_location;

-- 2. STAGING TABLES (For Chunked Loading)
CREATE TABLE stg_patent (
    patent_id TEXT,
    title TEXT
);

CREATE TABLE stg_abstract (
    patent_id TEXT,
    abstract TEXT
);

CREATE TABLE stg_application (
    patent_id TEXT,
    filing_date DATE,
    year INTEGER
);

CREATE TABLE stg_inventor (
    patent_id TEXT,
    inventor_id TEXT,
    name TEXT,
    location_id TEXT
);

CREATE TABLE stg_assignee (
    patent_id TEXT,
    assignee_id TEXT,
    company_name TEXT
);

CREATE TABLE stg_location (
    location_id TEXT,
    country TEXT
);

-- 3. FINAL TABLES
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date DATE,
    year INTEGER
);

CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);

CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
