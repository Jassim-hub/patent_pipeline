-- schema.sql
-- Defines the database tables for the Patent Intelligence System

DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

-- Table for Patents
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date DATE,
    year INTEGER
);

-- Table for Inventors
CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);

-- Table for Companies (Assignees)
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);

-- Table for Relationships (Linking patents to inventors and companies)
CREATE TABLE relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
