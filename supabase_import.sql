-- Run this with psql against your Supabase Postgres connection.
-- The \copy commands read files from your local machine, so they will not work in the Supabase SQL editor.

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

\copy stg_patent(patent_id, title) from 'D:/patent_pipeline/data/stg_patent.csv' csv header
\copy stg_abstract(patent_id, abstract) from 'D:/patent_pipeline/data/stg_abstract.csv' csv header
\copy stg_application(patent_id, filing_date, year) from 'D:/patent_pipeline/data/stg_application.csv' csv header
\copy stg_inventor(patent_id, inventor_id, name, location_id) from 'D:/patent_pipeline/data/stg_inventor.csv' csv header
\copy stg_assignee(patent_id, assignee_id, company_name) from 'D:/patent_pipeline/data/stg_assignee.csv' csv header
\copy stg_location(location_id, country) from 'D:/patent_pipeline/data/stg_location.csv' csv header

insert into patents (patent_id, title, abstract, filing_date, year)
select
    p.patent_id,
    p.title,
    a.abstract,
    app.filing_date,
    app.year
from stg_patent p
left join stg_abstract a on p.patent_id = a.patent_id
left join stg_application app on p.patent_id = app.patent_id
group by p.patent_id, p.title, a.abstract, app.filing_date, app.year;

insert into inventors (inventor_id, name, country)
select
    i.inventor_id,
    max(i.name) as name,
    max(l.country) as country
from stg_inventor i
left join stg_location l on i.location_id = l.location_id
group by i.inventor_id;

insert into companies (company_id, name)
select
    assignee_id,
    max(company_name)
from stg_assignee
group by assignee_id;

insert into relationships (patent_id, inventor_id, company_id)
select distinct
    i.patent_id,
    i.inventor_id,
    a.assignee_id
from stg_inventor i
inner join stg_assignee a on i.patent_id = a.patent_id;

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