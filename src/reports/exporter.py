"""
src/reports/exporter.py
Formats report data for console output, CSV, and HTML export.
"""

import csv
import os
from datetime import datetime
from tabulate import tabulate


OUTPUT_DIR = "output"


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _fmt_date(d) -> str:
    if hasattr(d, "strftime"):
        return d.strftime("%Y-%m-%d")
    return str(d)


# ──────────────────────────────────────────────
# Console Printer
# ──────────────────────────────────────────────

def print_report(report: dict):
    title = report.get("title", "Report")
    start, end = report["range"]
    sep = "=" * 52

    print(f"\n{sep}")
    print(f"  {title.upper()}")
    print(f"  {_fmt_date(start)}  →  {_fmt_date(end)}")
    print(sep)

    summary = report.get("summary", {})
    if summary:
        print("\n📌 Summary")
        for k, v in summary.items():
            label = k.replace("_", " ").title()
            print(f"   {label:<28} {v}")

    sections = {
        "by_service":       "Errors by Service",
        "top_errors":       "Top Error Messages",
        "by_hour":          "Errors by Hour",
        "slowest_endpoints":"Slowest Endpoints",
        "sla_breaches":     f"SLA Breaches (>{report.get('sla_threshold_ms', 1000)}ms)",
        "distribution":     "Response Time Distribution",
        "top_endpoints":    "Most Accessed Endpoints",
        "top_users":        "Most Active Users",
        "status_distribution": "HTTP Status Code Distribution",
        "hourly_traffic":   "Traffic by Hour",
    }

    for key, heading in sections.items():
        rows = report.get(key)
        if rows:
            print(f"\n📊 {heading}")
            print(tabulate(rows, headers="keys", tablefmt="rounded_outline"))

    print()


# ──────────────────────────────────────────────
# CSV Export
# ──────────────────────────────────────────────

def export_csv(report: dict):
    _ensure_output_dir()
    title_slug = report["title"].lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    exported = []

    section_keys = [
        "by_service", "top_errors", "by_hour",
        "slowest_endpoints", "sla_breaches", "distribution",
        "top_endpoints", "top_users", "status_distribution", "hourly_traffic",
    ]

    for key in section_keys:
        rows = report.get(key)
        if not rows:
            continue

        filename = f"{title_slug}_{key}_{timestamp}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        exported.append(filepath)
        print(f"   📄 Saved: {filepath}")

    return exported


# ──────────────────────────────────────────────
# HTML Export
# ──────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 2rem; }}
  h1   {{ color: #38bdf8; border-bottom: 2px solid #1e40af; padding-bottom: .5rem; }}
  h2   {{ color: #7dd3fc; margin-top: 2rem; }}
  p    {{ color: #94a3b8; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: .5rem; }}
  th   {{ background: #1e3a5f; color: #bae6fd; padding: .5rem 1rem; text-align: left; }}
  td   {{ padding: .45rem 1rem; border-bottom: 1px solid #1e293b; }}
  tr:hover td {{ background: #1e2d45; }}
  .meta {{ font-size: .85rem; color: #64748b; margin-bottom: 1rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">Period: {start} → {end} &nbsp;|&nbsp; Generated: {generated}</p>
{sections}
</body>
</html>
"""

def _table_html(rows: list[dict], heading: str) -> str:
    if not rows:
        return ""
    headers = rows[0].keys()
    ths = "".join(f"<th>{h.replace('_', ' ').title()}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = "".join(f"<td>{v}</td>" for v in row.values())
        trs += f"<tr>{tds}</tr>"
    return f"<h2>{heading}</h2><table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>"


def export_html(report: dict):
    _ensure_output_dir()
    title = report["title"]
    start, end = report["range"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    section_map = {
        "by_service":           "Errors by Service",
        "top_errors":           "Top Error Messages",
        "by_hour":              "Errors by Hour of Day",
        "slowest_endpoints":    "Slowest Endpoints",
        "sla_breaches":         "SLA Breaches",
        "distribution":         "Response Time Distribution",
        "top_endpoints":        "Most Accessed Endpoints",
        "top_users":            "Most Active Users",
        "status_distribution":  "HTTP Status Codes",
        "hourly_traffic":       "Hourly Traffic",
    }

    sections_html = ""
    # Summary table
    summary = report.get("summary")
    if summary:
        rows = [{"Metric": k.replace("_", " ").title(), "Value": v} for k, v in summary.items()]
        sections_html += _table_html(rows, "Summary")

    for key, heading in section_map.items():
        rows = report.get(key)
        if rows:
            sections_html += _table_html(rows, heading)

    html = HTML_TEMPLATE.format(
        title=title,
        start=_fmt_date(start),
        end=_fmt_date(end),
        generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sections=sections_html,
    )

    filename = f"{title.lower().replace(' ', '_')}_{timestamp}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"   🌐 Saved: {filepath}")
    return filepath
