-- =============================================================
-- Performance Analysis Queries
-- =============================================================

-- Overall response time statistics
SELECT
    COUNT(*)                                    AS total_requests,
    ROUND(AVG(response_time_ms))                AS avg_response_ms,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_ms) AS p50_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) AS p99_ms,
    MAX(response_time_ms)                       AS max_response_ms
FROM log_entries
WHERE response_time_ms IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s;


-- Slowest endpoints (avg response time)
SELECT
    endpoint,
    COUNT(*)                         AS request_count,
    ROUND(AVG(response_time_ms))     AS avg_ms,
    MAX(response_time_ms)            AS max_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms
FROM log_entries
WHERE response_time_ms IS NOT NULL
  AND endpoint IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY endpoint
ORDER BY avg_ms DESC
LIMIT 10;


-- Requests exceeding SLA threshold (default: 1000ms)
SELECT
    endpoint,
    service,
    logged_at,
    response_time_ms
FROM log_entries
WHERE response_time_ms > %(sla_threshold_ms)s
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
ORDER BY response_time_ms DESC
LIMIT 50;


-- Hourly average response time (identify slow periods)
SELECT
    DATE_TRUNC('hour', logged_at)    AS hour,
    ROUND(AVG(response_time_ms))     AS avg_ms,
    COUNT(*)                         AS request_count
FROM log_entries
WHERE response_time_ms IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY hour
ORDER BY hour;


-- Response time distribution buckets
SELECT
    CASE
        WHEN response_time_ms < 100   THEN '< 100ms'
        WHEN response_time_ms < 500   THEN '100–499ms'
        WHEN response_time_ms < 1000  THEN '500–999ms'
        WHEN response_time_ms < 3000  THEN '1s–2.9s'
        ELSE '3s+'
    END AS bucket,
    COUNT(*) AS request_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM log_entries
WHERE response_time_ms IS NOT NULL
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY bucket
ORDER BY MIN(response_time_ms);
