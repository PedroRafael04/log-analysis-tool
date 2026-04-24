"""
generate_logs.py
Generates realistic simulated log files for demo and testing.

Usage:
    python generate_logs.py --lines 5000 --output data/sample_logs/app.log
"""

import argparse
import random
from datetime import datetime, timedelta


SERVICES = [
    "auth-service", "api-gateway", "user-service",
    "payment-service", "notification-service", "search-service",
]

ENDPOINTS = [
    "/api/login", "/api/logout", "/api/users", "/api/users/{id}",
    "/api/products", "/api/orders", "/api/search", "/api/payments",
    "/api/notifications", "/api/health",
]

LEVELS = ["DEBUG", "INFO", "INFO", "INFO", "WARNING", "ERROR", "ERROR", "CRITICAL"]

ERROR_MESSAGES = [
    "Connection timed out",
    "NullPointerException in handler",
    "Authentication failed: invalid token",
    "Database query exceeded timeout",
    "Failed to acquire connection from pool",
    "Unhandled exception in request pipeline",
    "Rate limit exceeded",
    "Disk I/O error",
]

INFO_MESSAGES = [
    "Request processed successfully",
    "User session started",
    "Cache hit for key",
    "Scheduled job completed",
    "Health check passed",
    "Configuration reloaded",
]

WARNING_MESSAGES = [
    "Retrying request (attempt 2/3)",
    "High memory usage detected",
    "Slow query detected",
    "Deprecated API version used",
    "JWT token near expiry",
]

DEBUG_MESSAGES = [
    "Entering request handler",
    "Cache miss, fetching from DB",
    "Serialising response object",
    "Routing to service",
]

STATUS_CODES = {
    "DEBUG":    None,
    "INFO":     random.choice([200, 200, 200, 201, 204]),
    "WARNING":  random.choice([301, 400, 403, 429]),
    "ERROR":    random.choice([500, 502, 503]),
    "CRITICAL": 500,
}


def random_response_time(level: str) -> int | None:
    if level == "DEBUG":
        return None
    if level == "CRITICAL":
        return random.randint(3000, 8000)
    if level == "ERROR":
        return random.randint(1000, 5000)
    if level == "WARNING":
        return random.randint(500, 2000)
    return random.randint(20, 800)


def random_message(level: str) -> str:
    mapping = {
        "DEBUG":    DEBUG_MESSAGES,
        "INFO":     INFO_MESSAGES,
        "WARNING":  WARNING_MESSAGES,
        "ERROR":    ERROR_MESSAGES,
        "CRITICAL": ERROR_MESSAGES,
    }
    return random.choice(mapping[level])


def generate_line(timestamp: datetime) -> str:
    level = random.choice(LEVELS)
    service = random.choice(SERVICES)
    message = random_message(level)
    rt = random_response_time(level)
    endpoint = random.choice(ENDPOINTS) if level != "DEBUG" else None
    user_id = f"u_{random.randint(1000, 9999)}" if random.random() > 0.3 else None
    status = STATUS_CODES.get(level)
    if callable(status):
        status = status()

    parts = [
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        level,
        service,
        message,
    ]

    extras = []
    if rt is not None:
        extras.append(f"rt={rt}")
    if endpoint:
        extras.append(f"endpoint={endpoint}")
    if user_id:
        extras.append(f"user={user_id}")
    if status:
        extras.append(f"status={status}")

    if extras:
        parts.append("| " + " ".join(extras))

    return " ".join(parts)


def generate_logs(lines: int, output: str):
    start = datetime.now() - timedelta(days=30)

    with open(output, "w", encoding="utf-8") as f:
        for i in range(lines):
            # Slightly non-uniform time distribution for realism
            offset = timedelta(
                minutes=random.randint(0, 30 * 24 * 60),
                seconds=random.randint(0, 59),
            )
            ts = start + offset
            f.write(generate_line(ts) + "\n")

    print(f"✅ Generated {lines:,} log lines → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample log files.")
    parser.add_argument("--lines", type=int, default=3000, help="Number of log lines to generate")
    parser.add_argument("--output", type=str, default="data/sample_logs/app.log", help="Output file path")
    args = parser.parse_args()

    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    generate_logs(args.lines, args.output)
