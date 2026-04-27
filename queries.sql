-- queries.sql

-- Q1: Top Inventors
-- Who has the most patents?
SELECT 
    i.name as inventor_name, 
    COUNT(r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id
ORDER BY total_patents DESC
LIMIT 10;

-- Q2: Top Companies
-- Which companies own the most patents?
SELECT 
    c.name as company_name, 
    COUNT(r.patent_id) as total_patents
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id
ORDER BY total_patents DESC
LIMIT 10;

-- Q3: Countries
-- Which countries produce the most patents?
SELECT 
    i.country, 
    COUNT(DISTINCT r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.country
ORDER BY total_patents DESC
LIMIT 10;

-- Q4: Trends Over Time
-- How many patents are created each year?
SELECT 
    year, 
    COUNT(patent_id) as total_patents
FROM patents
WHERE year > 1900 -- Filter out bad data
GROUP BY year
ORDER BY year DESC;

-- Q5: JOIN Query
-- Combine patents with inventors and companies
SELECT 
    p.title as patent_title, 
    i.name as inventor_name, 
    c.name as company_name, 
    p.year
FROM patents p
JOIN relationships r ON p.patent_id = r.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
JOIN companies c ON r.company_id = c.company_id
LIMIT 20;

-- Q6: CTE Query (WITH statement)
-- Break a complex query into steps: Find companies with more than 5 patents, then get their patent titles.
WITH TopCompanies AS (
    SELECT c.company_id, c.name
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id
    HAVING COUNT(r.patent_id) > 5
)
SELECT tc.name as company_name, p.title as patent_title
FROM TopCompanies tc
JOIN relationships r ON tc.company_id = r.company_id
JOIN patents p ON r.patent_id = p.patent_id
LIMIT 20;

-- Q7: Ranking Query
-- Rank inventors using window functions
SELECT 
    i.name as inventor_name,
    COUNT(r.patent_id) as total_patents,
    RANK() OVER(ORDER BY COUNT(r.patent_id) DESC) as rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id
LIMIT 20;
