"""
src/ingestion/parser.py
Parses raw log lines into structured dictionaries.

Expected log format:
2024-01-15 03:42:11 ERROR auth-service Connection timed out | rt=342 endpoint=/api/login user=u_8821 status=500
"""

import re
from datetime import datetime
from typing import Optional


# Regex pattern matching the log line format produced by generate_logs.py
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    r"\s+(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)"
    r"\s+(?P<service>\S+)"
    r"\s+(?P<message>[^|]+)"
    r"(?:\|\s*rt=(?P<response_time>\d+))?"
    r"(?:\s+endpoint=(?P<endpoint>\S+))?"
    r"(?:\s+user=(?P<user_id>\S+))?"
    r"(?:\s+status=(?P<status_code>\d+))?"
)


def parse_line(line: str) -> Optional[dict]:
    """
    Parse a single log line.
    Returns a dict of extracted fields, or None if the line doesn't match.
    """
    line = line.strip()
    if not line:
        return None

    match = LOG_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()

    return {
        "logged_at": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
        "level": data["level"],
        "service": data["service"],
        "message": data["message"].strip(),
        "response_time_ms": int(data["response_time"]) if data["response_time"] else None,
        "endpoint": data["endpoint"],
        "user_id": data["user_id"],
        "status_code": int(data["status_code"]) if data["status_code"] else None,
    }


def parse_file(filepath: str) -> tuple[list[dict], int, int]:
    """
    Parse an entire log file.
    Returns (parsed_entries, total_lines, parsed_count).
    """
    entries = []
    total_lines = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            entry = parse_line(line)
            if entry:
                entries.append(entry)

    return entries, total_lines, len(entries)
