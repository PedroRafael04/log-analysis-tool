# Log Analysis SQL Reporting Tool

A Python-based tool for ingesting, storing, and analysing system logs using PostgreSQL. Generates structured reports on **errors**, **performance**, and **usage patterns** through optimised SQL queries.

---

## Features

- Automated ingestion of raw log files into a PostgreSQL database
- Optimised SQL queries for error tracking, performance metrics, and usage analysis
- CLI interface for running targeted reports
- Export reports to **CSV** and **HTML**
- Log generator for demo and testing purposes
- Clean modular architecture, easy to extend

---

## Project Structure

```
log-analysis-tool/
├── src/
│   ├── ingestion/        # Log parsing and database loading
│   ├── analysis/         # Report generation logic
│   ├── reports/          # CSV and HTML export
│   └── utils/            # Config, logging helpers
├── sql/
│   ├── schema/           # Database schema definitions
│   └── queries/          # Named SQL query files
├── data/
│   └── sample_logs/      # Sample and generated log files
├── tests/                # Unit tests
├── main.py               # CLI entry point
├── generate_logs.py      # Sample log generator
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer        | Technology         |
|--------------|--------------------|
| Language     | Python 3.11+       |
| Database     | PostgreSQL 15+     |
| DB Driver    | psycopg2           |
| CLI          | argparse           |
| Export       | csv, jinja2        |
| Testing      | pytest             |
| Config       | python-dotenv      |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/log-analysis-tool.git
cd log-analysis-tool
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 5. Initialise the database

Create the database in Postgres using:

```bash
CREATE DATABASE log_analysis;
```

Back into the terminal, run:

```bash
python main.py --init-db
```

---

## Usage

### Generate sample logs

```bash
python generate_logs.py --lines 5000 --output data/sample_logs/app.log
```

### Ingest logs into the database

```bash
python main.py --ingest data/sample_logs/app.log
```

### Run reports

```bash
# Error report
python main.py --report errors

# Performance report
python main.py --report performance

# Usage patterns report
python main.py --report usage

# Full report (all)
python main.py --report all --export csv
python main.py --report all --export html
```

### Filter by date range

```bash
python main.py --report errors --from 2024-01-01 --to 2024-01-31
```

---

## Running Tests

```bash
pytest tests/ -v
```

---