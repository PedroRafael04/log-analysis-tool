"""
tests/test_reporter.py
Unit tests for report generation logic (mocking DB calls).
"""

import pytest
from datetime import datetime
from unittest.mock import patch
from src.analysis.reporter import error_report, performance_report, usage_report


MOCK_SUMMARY = {"total_errors": 120, "critical_errors": 12, "errors_only": 108}
MOCK_ROWS    = [{"service": "auth-service", "error_count": 50, "critical_count": 5}]

START = datetime(2024, 1, 1)
END   = datetime(2024, 1, 31)


class TestErrorReport:

    @patch("src.analysis.reporter.execute_query")
    def test_returns_expected_keys(self, mock_query):
        mock_query.side_effect = [
            [MOCK_SUMMARY],
            MOCK_ROWS,
            MOCK_ROWS,
            MOCK_ROWS,
        ]
        result = error_report(start_date=START, end_date=END)

        assert result["title"] == "Error Report"
        assert "summary" in result
        assert "by_service" in result
        assert "top_errors" in result
        assert "by_hour" in result

    @patch("src.analysis.reporter.execute_query")
    def test_summary_values_match_mock(self, mock_query):
        mock_query.side_effect = [
            [MOCK_SUMMARY], [], [], [],
        ]
        result = error_report(start_date=START, end_date=END)

        assert result["summary"]["total_errors"] == 120
        assert result["summary"]["critical_errors"] == 12

    @patch("src.analysis.reporter.execute_query")
    def test_range_is_preserved(self, mock_query):
        mock_query.side_effect = [[MOCK_SUMMARY], [], [], []]
        result = error_report(start_date=START, end_date=END)

        assert result["range"] == (START, END)


class TestPerformanceReport:

    @patch("src.analysis.reporter.execute_query")
    def test_returns_expected_keys(self, mock_query):
        mock_perf = {"total_requests": 500, "avg_response_ms": 320,
                     "p50_ms": 250.0, "p95_ms": 900.0, "p99_ms": 1500.0, "max_response_ms": 7000}
        mock_query.side_effect = [[mock_perf], MOCK_ROWS, MOCK_ROWS, MOCK_ROWS]

        result = performance_report(start_date=START, end_date=END)

        assert "summary" in result
        assert "slowest_endpoints" in result
        assert "sla_breaches" in result
        assert "distribution" in result

    @patch("src.analysis.reporter.execute_query")
    def test_custom_sla_threshold_is_stored(self, mock_query):
        mock_query.side_effect = [[{}], [], [], []]
        result = performance_report(start_date=START, end_date=END, sla_threshold_ms=2000)

        assert result["sla_threshold_ms"] == 2000


class TestUsageReport:

    @patch("src.analysis.reporter.execute_query")
    def test_returns_expected_keys(self, mock_query):
        mock_usage = {"total_requests": 1000, "unique_users": 80,
                      "unique_endpoints": 10, "active_services": 5}
        mock_query.side_effect = [[mock_usage], MOCK_ROWS, MOCK_ROWS, MOCK_ROWS, MOCK_ROWS]

        result = usage_report(start_date=START, end_date=END)

        assert "summary" in result
        assert "top_endpoints" in result
        assert "top_users" in result
        assert "status_distribution" in result
        assert "hourly_traffic" in result
