"""
main.py
CLI entry point for the Log Analysis SQL Reporting Tool.

Examples:
    python main.py --init-db
    python main.py --ingest data/sample_logs/app.log
    python main.py --report errors
    python main.py --report performance --export html
    python main.py --report all --from 2024-01-01 --to 2024-01-31
"""

import argparse
import sys
from datetime import datetime

from src.utils.db import init_database
from src.ingestion.loader import ingest_file
from src.analysis.reporter import error_report, performance_report, usage_report
from src.reports.exporter import print_report, export_csv, export_html


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: '{value}'. Expected YYYY-MM-DD.")


def run_report(report_data: dict, export: str | None):
    print_report(report_data)
    if export == "csv":
        print("📁 Exporting CSV...")
        export_csv(report_data)
    elif export == "html":
        print("📁 Exporting HTML...")
        export_html(report_data)


def main():
    parser = argparse.ArgumentParser(
        description="Log Analysis SQL Reporting Tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialise the PostgreSQL database schema",
    )
    parser.add_argument(
        "--ingest",
        metavar="FILE",
        help="Path to a log file to ingest into the database",
    )
    parser.add_argument(
        "--report",
        choices=["errors", "performance", "usage", "all"],
        help="Report type to generate",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "html"],
        help="Export format for the report",
    )
    parser.add_argument(
        "--from",
        dest="start_date",
        type=parse_date,
        metavar="YYYY-MM-DD",
        help="Report start date (default: first day of current month)",
    )
    parser.add_argument(
        "--to",
        dest="end_date",
        type=parse_date,
        metavar="YYYY-MM-DD",
        help="Report end date (default: now)",
    )
    parser.add_argument(
        "--sla",
        dest="sla_threshold",
        type=int,
        default=1000,
        metavar="MS",
        help="SLA threshold in milliseconds for performance report (default: 1000)",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # ── Init DB ──────────────────────────────────────────
    if args.init_db:
        init_database()
        return

    # ── Ingest ───────────────────────────────────────────
    if args.ingest:
        ingest_file(args.ingest)
        return

    # ── Reports ──────────────────────────────────────────
    if args.report:
        kwargs = {"start_date": args.start_date, "end_date": args.end_date}

        if args.report in ("errors", "all"):
            run_report(error_report(**kwargs), args.export)

        if args.report in ("performance", "all"):
            run_report(
                performance_report(**kwargs, sla_threshold_ms=args.sla_threshold),
                args.export,
            )

        if args.report in ("usage", "all"):
            run_report(usage_report(**kwargs), args.export)


if __name__ == "__main__":
    main()
