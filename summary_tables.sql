-- Run this in the Supabase SQL editor.

create table if not exists top_inventors (
    inventor_name text,
    total_patents integer
);

create table if not exists top_companies (
    company_name text,
    total_patents integer
);

create table if not exists country_trends (
    country text,
    total_patents integer
);
