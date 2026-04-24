"""
src/analysis/reporter.py
Runs SQL queries and returns structured report data.
"""

from datetime import datetime, date
from src.utils.db import execute_query


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _default_dates(start_date, end_date):
    """Fall back to a sensible range when dates are not provided."""
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = datetime(end_date.year, end_date.month, 1)  # start of month
    return start_date, end_date


# ──────────────────────────────────────────────
# Error Report
# ──────────────────────────────────────────────

ERROR_SUMMARY_SQL = """
    SELECT
        COUNT(*) FILTER (WHERE level IN ('ERROR', 'CRITICAL')) AS total_errors,
        COUNT(*) FILTER (WHERE level = 'CRITICAL')             AS critical_errors,
        COUNT(*) FILTER (WHERE level = 'ERROR')                AS errors_only
    FROM log_entries
    WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s;
"""

ERROR_BY_SERVICE_SQL = """
    SELECT service, COUNT(*) AS error_count,
           COUNT(*) FILTER (WHERE level = 'CRITICAL') AS critical_count
    FROM log_entries
    WHERE level IN ('ERROR', 'CRITICAL')
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY service ORDER BY error_count DESC LIMIT 10;
"""

TOP_ERRORS_SQL = """
    SELECT message, level, COUNT(*) AS occurrences
    FROM log_entries
    WHERE level IN ('ERROR', 'CRITICAL')
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY message, level ORDER BY occurrences DESC LIMIT 10;
"""

ERROR_BY_HOUR_SQL = """
    SELECT EXTRACT(HOUR FROM logged_at)::int AS hour_of_day, COUNT(*) AS error_count
    FROM log_entries
    WHERE level IN ('ERROR', 'CRITICAL')
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY hour_of_day ORDER BY hour_of_day;
"""


def error_report(start_date=None, end_date=None) -> dict:
    start_date, end_date = _default_dates(start_date, end_date)
    params = {"start_date": start_date, "end_date": end_date}
    return {
        "title": "Error Report",
        "range": (start_date, end_date),
        "summary": execute_query(ERROR_SUMMARY_SQL, params)[0],
        "by_service": execute_query(ERROR_BY_SERVICE_SQL, params),
        "top_errors": execute_query(TOP_ERRORS_SQL, params),
        "by_hour": execute_query(ERROR_BY_HOUR_SQL, params),
    }


# ──────────────────────────────────────────────
# Performance Report
# ──────────────────────────────────────────────

PERF_SUMMARY_SQL = """
    SELECT
        COUNT(*) AS total_requests,
        ROUND(AVG(response_time_ms)) AS avg_response_ms,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_ms) AS p50_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_ms,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) AS p99_ms,
        MAX(response_time_ms) AS max_response_ms
    FROM log_entries
    WHERE response_time_ms IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s;
"""

SLOWEST_ENDPOINTS_SQL = """
    SELECT endpoint, COUNT(*) AS request_count,
           ROUND(AVG(response_time_ms)) AS avg_ms,
           MAX(response_time_ms) AS max_ms
    FROM log_entries
    WHERE response_time_ms IS NOT NULL AND endpoint IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY endpoint ORDER BY avg_ms DESC LIMIT 10;
"""

SLA_BREACHES_SQL = """
    SELECT endpoint, service, logged_at, response_time_ms
    FROM log_entries
    WHERE response_time_ms > %(threshold)s
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    ORDER BY response_time_ms DESC LIMIT 20;
"""

RESPONSE_DIST_SQL = """
    SELECT
        CASE
            WHEN response_time_ms < 100  THEN '< 100ms'
            WHEN response_time_ms < 500  THEN '100–499ms'
            WHEN response_time_ms < 1000 THEN '500–999ms'
            WHEN response_time_ms < 3000 THEN '1s–2.9s'
            ELSE '3s+'
        END AS bucket,
        COUNT(*) AS request_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM log_entries
    WHERE response_time_ms IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY bucket ORDER BY MIN(response_time_ms);
"""


def performance_report(start_date=None, end_date=None, sla_threshold_ms: int = 1000) -> dict:
    start_date, end_date = _default_dates(start_date, end_date)
    params = {"start_date": start_date, "end_date": end_date}
    return {
        "title": "Performance Report",
        "range": (start_date, end_date),
        "sla_threshold_ms": sla_threshold_ms,
        "summary": execute_query(PERF_SUMMARY_SQL, params)[0],
        "slowest_endpoints": execute_query(SLOWEST_ENDPOINTS_SQL, params),
        "sla_breaches": execute_query(SLA_BREACHES_SQL, {**params, "threshold": sla_threshold_ms}),
        "distribution": execute_query(RESPONSE_DIST_SQL, params),
    }


# ──────────────────────────────────────────────
# Usage Report
# ──────────────────────────────────────────────

USAGE_SUMMARY_SQL = """
    SELECT
        COUNT(*) AS total_requests,
        COUNT(DISTINCT user_id) AS unique_users,
        COUNT(DISTINCT endpoint) AS unique_endpoints,
        COUNT(DISTINCT service) AS active_services
    FROM log_entries
    WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s;
"""

TOP_ENDPOINTS_SQL = """
    SELECT endpoint, COUNT(*) AS request_count,
           COUNT(DISTINCT user_id) AS unique_users,
           ROUND(AVG(response_time_ms)) AS avg_response_ms
    FROM log_entries
    WHERE endpoint IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY endpoint ORDER BY request_count DESC LIMIT 10;
"""

TOP_USERS_SQL = """
    SELECT user_id, COUNT(*) AS request_count,
           COUNT(DISTINCT endpoint) AS endpoints_used
    FROM log_entries
    WHERE user_id IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY user_id ORDER BY request_count DESC LIMIT 10;
"""

STATUS_DIST_SQL = """
    SELECT status_code, COUNT(*) AS occurrences,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM log_entries
    WHERE status_code IS NOT NULL
      AND logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY status_code ORDER BY occurrences DESC;
"""

HOURLY_TRAFFIC_SQL = """
    SELECT EXTRACT(HOUR FROM logged_at)::int AS hour_of_day,
           COUNT(*) AS request_count
    FROM log_entries
    WHERE logged_at BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY hour_of_day ORDER BY hour_of_day;
"""


def usage_report(start_date=None, end_date=None) -> dict:
    start_date, end_date = _default_dates(start_date, end_date)
    params = {"start_date": start_date, "end_date": end_date}
    return {
        "title": "Usage Report",
        "range": (start_date, end_date),
        "summary": execute_query(USAGE_SUMMARY_SQL, params)[0],
        "top_endpoints": execute_query(TOP_ENDPOINTS_SQL, params),
        "top_users": execute_query(TOP_USERS_SQL, params),
        "status_distribution": execute_query(STATUS_DIST_SQL, params),
        "hourly_traffic": execute_query(HOURLY_TRAFFIC_SQL, params),
    }
