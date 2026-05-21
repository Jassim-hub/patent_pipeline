-- Run this in the Supabase SQL editor to create the tables and indexes.
-- Use the separate load_supabase_data.psql file with psql from your machine to import CSVs.

drop table if exists relationships cascade;
drop table if exists patents cascade;
drop table if exists inventors cascade;
drop table if exists companies cascade;

drop table if exists stg_patent cascade;
drop table if exists stg_abstract cascade;
drop table if exists stg_application cascade;
drop table if exists stg_inventor cascade;
drop table if exists stg_assignee cascade;
drop table if exists stg_location cascade;

create table stg_patent (
    patent_id text,
    title text
);

create table stg_abstract (
    patent_id text,
    abstract text
);

create table stg_application (
    patent_id text,
    filing_date date,
    year integer
);

create table stg_inventor (
    patent_id text,
    inventor_id text,
    name text,
    location_id text
);

create table stg_assignee (
    patent_id text,
    assignee_id text,
    company_name text
);

create table stg_location (
    location_id text,
    country text
);

create table patents (
    patent_id text primary key,
    title text,
    abstract text,
    filing_date date,
    year integer
);

create table inventors (
    inventor_id text primary key,
    name text,
    country text
);

create table companies (
    company_id text primary key,
    name text
);

create table relationships (
    patent_id text,
    inventor_id text,
    company_id text,
    constraint fk_relationship_patent foreign key (patent_id) references patents(patent_id),
    constraint fk_relationship_inventor foreign key (inventor_id) references inventors(inventor_id),
    constraint fk_relationship_company foreign key (company_id) references companies(company_id)
);

create index if not exists idx_relationships_patent_id on relationships(patent_id);
create index if not exists idx_relationships_inventor_id on relationships(inventor_id);
create index if not exists idx_relationships_company_id on relationships(company_id);
create index if not exists idx_patents_year on patents(year);

-- Optional cleanup if you do not want to keep the staging tables:
-- drop table stg_patent cascade;
-- drop table stg_abstract cascade;
-- drop table stg_application cascade;
-- drop table stg_inventor cascade;
-- drop table stg_assignee cascade;
-- drop table stg_location cascade;