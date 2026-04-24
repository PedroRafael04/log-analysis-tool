"""
src/ingestion/loader.py
Loads parsed log entries into the PostgreSQL database.
"""

import os
import psycopg2.extras
from src.ingestion.parser import parse_file
from src.utils.db import get_connection


INSERT_RUN_SQL = """
    INSERT INTO ingestion_runs (file_name, total_lines, total_parsed, status)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
"""

INSERT_ENTRY_SQL = """
    INSERT INTO log_entries
        (ingestion_id, logged_at, level, service, message,
         response_time_ms, endpoint, user_id, status_code)
    VALUES
        (%(ingestion_id)s, %(logged_at)s, %(level)s, %(service)s, %(message)s,
         %(response_time_ms)s, %(endpoint)s, %(user_id)s, %(status_code)s);
"""


def ingest_file(filepath: str) -> dict:
    """
    Parse and load a log file into the database.
    Returns a summary dict with ingestion metadata.
    """
    print(f"📂 Parsing: {filepath}")
    entries, total_lines, parsed_count = parse_file(filepath)

    if not entries:
        print("⚠️  No valid log entries found in file.")
        return {"total_lines": total_lines, "parsed": 0}

    file_name = os.path.basename(filepath)

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Register this ingestion run
            cur.execute(INSERT_RUN_SQL, (file_name, total_lines, parsed_count, "completed"))
            ingestion_id = cur.fetchone()[0]

            # Attach ingestion_id to each entry and bulk insert
            for entry in entries:
                entry["ingestion_id"] = ingestion_id

            psycopg2.extras.execute_batch(cur, INSERT_ENTRY_SQL, entries, page_size=500)

        conn.commit()

    print(f"✅ Ingested {parsed_count:,} entries from {total_lines:,} lines  (run_id={ingestion_id})")

    return {
        "ingestion_id": ingestion_id,
        "file": file_name,
        "total_lines": total_lines,
        "parsed": parsed_count,
        "skipped": total_lines - parsed_count,
    }
