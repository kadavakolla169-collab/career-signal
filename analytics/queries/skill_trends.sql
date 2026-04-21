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

-- Experience level distribution by role
SELECT 
    j.role,
    js.experience_level,
    COUNT(*) as count
FROM job_skills js
JOIN jobs j ON js.job_id = j.job_id
WHERE js.experience_level IS NOT NULL
GROUP BY j.role, js.experience_level
ORDER BY j.role, count DESC;

-- Visa sponsorship availability
SELECT 
    visa_sponsorship,
    COUNT(*) as count
FROM job_skills
WHERE visa_sponsorship IS NOT NULL
GROUP BY visa_sponsorship;

-- Top cloud platforms in demand
SELECT 
    platform,
    COUNT(*) as demand_count
FROM (
    SELECT json_array_elements_text(cloud_platforms::json) as platform
    FROM job_skills
    WHERE cloud_platforms != '[]'
) platforms
GROUP BY platform
ORDER BY demand_count DESC;