-- =============================================================
-- Error Analysis Queries
-- =============================================================

-- Total errors and critical errors in range
SELECT
    COUNT(*) FILTER (WHERE level IN ('ERROR', 'CRITICAL'))   AS total_errors,
    COUNT(*) FILTER (WHERE level = 'CRITICAL')               AS critical_errors,
    COUNT(*) FILTER (WHERE level = 'ERROR')                  AS errors_only
FROM log_entries
WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s;


-- Error count grouped by service
SELECT
    service,
    COUNT(*) AS error_count,
    COUNT(*) FILTER (WHERE level = 'CRITICAL') AS critical_count
FROM log_entries
WHERE level IN ('ERROR', 'CRITICAL')
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY service
ORDER BY error_count DESC
LIMIT 10;


-- Top recurring error messages
SELECT
    message,
    level,
    COUNT(*) AS occurrences
FROM log_entries
WHERE level IN ('ERROR', 'CRITICAL')
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY message, level
ORDER BY occurrences DESC
LIMIT 10;


-- Errors grouped by hour of day (peak error windows)
SELECT
    EXTRACT(HOUR FROM logged_at) AS hour_of_day,
    COUNT(*) AS error_count
FROM log_entries
WHERE level IN ('ERROR', 'CRITICAL')
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY hour_of_day
ORDER BY hour_of_day;


-- Daily error trend
SELECT
    DATE(logged_at) AS day,
    COUNT(*) AS total_errors,
    COUNT(*) FILTER (WHERE level = 'CRITICAL') AS critical_count
FROM log_entries
WHERE level IN ('ERROR', 'CRITICAL')
  AND logged_at BETWEEN %(start_date)s AND %(end_date)s
GROUP BY day
ORDER BY day;
