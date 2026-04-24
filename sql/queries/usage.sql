-- =============================================================
-- Usage Pattern Queries
-- =============================================================

-- Total requests and unique users in range
SELECT
    COUNT(*)                        AS total_requests,
    COUNT(DISTINCT user_id)         AS unique_users,
    COUNT(DISTINCT endpoint)        AS unique_endpoints,
    COUNT(DISTINCT service)         AS active_services
FROM log_entries
WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s;


-- Most accessed endpoints
SELECT
    endpoint,
    COUNT(*)                             AS request_count,
    COUNT(DISTINCT user_id)             AS unique_users,
    ROUND(AVG(response_time_ms))         AS avg_response_ms
FROM log_entries
WHERE endpoint IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY endpoint
ORDER BY request_count DESC
LIMIT 10;


-- Most active users
SELECT
    user_id,
    COUNT(*)                   AS request_count,
    COUNT(DISTINCT endpoint)   AS endpoints_used,
    MIN(logged_at)             AS first_seen,
    MAX(logged_at)             AS last_seen
FROM log_entries
WHERE user_id IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY user_id
ORDER BY request_count DESC
LIMIT 10;


-- Requests per hour of day (traffic patterns)
SELECT
    EXTRACT(HOUR FROM logged_at) AS hour_of_day,
    COUNT(*)                     AS request_count
FROM log_entries
WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY hour_of_day
ORDER BY hour_of_day;


-- HTTP status code distribution
SELECT
    status_code,
    COUNT(*)                                              AS occurrences,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)   AS percentage
FROM log_entries
WHERE status_code IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY status_code
ORDER BY occurrences DESC;


-- Daily request volume
SELECT
    DATE(logged_at)   AS day,
    COUNT(*)          AS total_requests,
    COUNT(DISTINCT user_id) AS unique_users
FROM log_entries
WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY day
ORDER BY day;
