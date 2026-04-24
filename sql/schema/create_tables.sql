-- =============================================================
-- Log Analysis Tool — Database Schema
-- =============================================================

-- Drop tables if re-initialising
DROP TABLE IF EXISTS log_entries CASCADE;
DROP TABLE IF EXISTS ingestion_runs CASCADE;

-- -------------------------------------------------------------
-- Tracks each file ingestion run
-- -------------------------------------------------------------
CREATE TABLE ingestion_runs (
    id            SERIAL PRIMARY KEY,
    file_name     TEXT NOT NULL,
    ingested_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    total_lines   INTEGER,
    total_parsed  INTEGER,
    status        TEXT NOT NULL DEFAULT 'completed'
);

-- -------------------------------------------------------------
-- Core log entries table
-- -------------------------------------------------------------
CREATE TABLE log_entries (
    id              SERIAL PRIMARY KEY,
    ingestion_id    INTEGER REFERENCES ingestion_runs(id) ON DELETE CASCADE,

    -- Timestamp from the log line itself
    logged_at       TIMESTAMP NOT NULL,

    -- Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    level           TEXT NOT NULL,

    -- Source service or module
    service         TEXT NOT NULL,

    -- Full log message
    message         TEXT NOT NULL,

    -- Optional structured fields
    response_time_ms INTEGER,       -- For performance logs
    endpoint        TEXT,           -- HTTP endpoint hit
    user_id         TEXT,           -- Authenticated user, if present
    status_code     INTEGER         -- HTTP status code, if present
);

-- -------------------------------------------------------------
-- Indexes for query performance
-- -------------------------------------------------------------
CREATE INDEX idx_log_level       ON log_entries (level);
CREATE INDEX idx_log_service     ON log_entries (service);
CREATE INDEX idx_log_logged_at   ON log_entries (logged_at);
CREATE INDEX idx_log_status_code ON log_entries (status_code);
CREATE INDEX idx_log_user_id     ON log_entries (user_id);
