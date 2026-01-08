-- Query to get only jobs from the last 30 days
-- Use this in your website/API queries

SELECT *
FROM jobs
WHERE posted_at >= NOW() - INTERVAL '30 days'
  AND status = 'approved'
ORDER BY posted_at DESC;

-- Or if you want to be more strict (exactly 30 days):
SELECT *
FROM jobs
WHERE posted_at >= CURRENT_DATE - INTERVAL '30 days'
  AND status = 'approved'
ORDER BY posted_at DESC;

-- Count jobs by age
SELECT 
    CASE 
        WHEN posted_at >= NOW() - INTERVAL '7 days' THEN 'Last 7 days'
        WHEN posted_at >= NOW() - INTERVAL '30 days' THEN 'Last 30 days'
        WHEN posted_at >= NOW() - INTERVAL '90 days' THEN 'Last 90 days'
        ELSE 'Older than 90 days'
    END AS age_group,
    COUNT(*) as job_count
FROM jobs
WHERE status = 'approved'
GROUP BY age_group
ORDER BY 
    CASE age_group
        WHEN 'Last 7 days' THEN 1
        WHEN 'Last 30 days' THEN 2
        WHEN 'Last 90 days' THEN 3
        ELSE 4
    END;

