"""
src/utils/db.py
Database connection management using psycopg2.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a new PostgreSQL connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "log_analysis"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def init_database():
    """Run the schema creation script against the database."""
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "sql", "schema", "create_tables.sql"
    )
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()

    print("✅ Database initialised successfully.")


def load_query(query_file: str) -> str:
    """Load a named SQL file from sql/queries/."""
    query_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "sql", "queries", query_file
    )
    with open(query_path, "r") as f:
        return f.read()


def execute_query(sql: str, params: dict = None) -> list[dict]:
    """Execute a SQL query and return results as a list of dicts."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
