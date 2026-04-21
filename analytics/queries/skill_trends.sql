-- Top 10 most in-demand technical skills overall
SELECT 
    skill,
    COUNT(*) as demand_count
FROM (
    SELECT json_array_elements_text(technical_skills::json) as skill
    FROM job_skills
) skills
GROUP BY skill
ORDER BY demand_count DESC
LIMIT 10;

-- Top skills by role
SELECT 
    role,
    skill,
    COUNT(*) as demand_count
FROM (
    SELECT js.job_id, j.role, json_array_elements_text(js.technical_skills::json) as skill
    FROM job_skills js
    JOIN jobs j ON js.job_id = j.job_id
) skills
GROUP BY role, skill
ORDER BY role, demand_count DESC;