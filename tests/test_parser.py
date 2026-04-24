"""
tests/test_parser.py
Unit tests for the log line parser.
"""

import pytest
from datetime import datetime
from src.ingestion.parser import parse_line, parse_file


# ──────────────────────────────────────────────
# parse_line tests
# ──────────────────────────────────────────────

class TestParseLine:

    def test_parses_error_line_with_all_fields(self):
        line = "2024-01-15 03:42:11 ERROR auth-service Connection timed out | rt=342 endpoint=/api/login user=u_8821 status=500"
        result = parse_line(line)

        assert result is not None
        assert result["logged_at"] == datetime(2024, 1, 15, 3, 42, 11)
        assert result["level"] == "ERROR"
        assert result["service"] == "auth-service"
        assert result["message"] == "Connection timed out"
        assert result["response_time_ms"] == 342
        assert result["endpoint"] == "/api/login"
        assert result["user_id"] == "u_8821"
        assert result["status_code"] == 500

    def test_parses_info_line_minimal(self):
        line = "2024-03-01 10:00:00 INFO api-gateway Health check passed"
        result = parse_line(line)

        assert result is not None
        assert result["level"] == "INFO"
        assert result["service"] == "api-gateway"
        assert result["response_time_ms"] is None
        assert result["endpoint"] is None
        assert result["user_id"] is None
        assert result["status_code"] is None

    def test_parses_critical_line(self):
        line = "2024-06-20 23:59:59 CRITICAL payment-service Unhandled exception | rt=5200 endpoint=/api/payments status=500"
        result = parse_line(line)

        assert result["level"] == "CRITICAL"
        assert result["response_time_ms"] == 5200
        assert result["status_code"] == 500

    def test_returns_none_for_empty_line(self):
        assert parse_line("") is None
        assert parse_line("   ") is None

    def test_returns_none_for_malformed_line(self):
        assert parse_line("this is not a log line at all") is None
        assert parse_line("2024-01-01 BROKEN") is None

    def test_all_log_levels_are_accepted(self):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            line = f"2024-01-01 00:00:00 {level} some-service Some message"
            result = parse_line(line)
            assert result is not None, f"Failed to parse level: {level}"
            assert result["level"] == level

    def test_message_is_stripped(self):
        line = "2024-01-01 00:00:00 INFO svc   Padded message   | rt=100"
        result = parse_line(line)
        assert result["message"] == "Padded message"


# ──────────────────────────────────────────────
# parse_file tests
# ──────────────────────────────────────────────

class TestParseFile:

    def test_parse_file_counts_correctly(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "2024-01-01 00:00:00 INFO svc-a All good\n"
            "2024-01-01 00:01:00 ERROR svc-b Something failed\n"
            "this line is garbage and should be skipped\n"
            "\n"
        )

        entries, total_lines, parsed_count = parse_file(str(log_file))

        assert total_lines == 4
        assert parsed_count == 2
        assert len(entries) == 2

    def test_parse_file_returns_correct_levels(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "2024-02-10 08:00:00 WARNING auth-service Token near expiry\n"
            "2024-02-10 08:01:00 CRITICAL db-service Disk full\n"
        )

        entries, _, _ = parse_file(str(log_file))

        assert entries[0]["level"] == "WARNING"
        assert entries[1]["level"] == "CRITICAL"

    def test_parse_empty_file(self, tmp_path):
        log_file = tmp_path / "empty.log"
        log_file.write_text("")

        entries, total_lines, parsed_count = parse_file(str(log_file))

        assert total_lines == 0
        assert parsed_count == 0
        assert entries == []
