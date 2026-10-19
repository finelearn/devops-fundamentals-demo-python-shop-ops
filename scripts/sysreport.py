#!/usr/bin/env python3
"""Daily system report for the shop server: API health and disk space."""
import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = os.environ.get("API_URL", "http://127.0.0.1:3000")
TIMEOUT_S = 3
log = logging.getLogger("sysreport")


def check_api(base: str) -> dict:
    try:
        resp = requests.get(f"{base}/health", timeout=TIMEOUT_S)
        resp.raise_for_status()
        return {"ok": True, "version": resp.json()["version"]}
    except requests.RequestException as err:
        log.error("shop API check failed: %s", err)
        return {"ok": False, "error": type(err).__name__}


def check_disk(path: str, limit: int) -> dict:
    usage = shutil.disk_usage(path)
    percent = round(usage.used / usage.total * 100)
    return {"ok": percent < limit, "used_percent": percent}


def evaluate(checks: dict) -> int:
    return 0 if all(c["ok"] for c in checks.values()) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the daily system report.")
    parser.add_argument("--out", default="reports/sysreport.json")
    parser.add_argument("--disk-limit", type=int, default=80)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    checks = {"api": check_api(API_URL), "disk": check_disk("/", args.disk_limit)}
    code = evaluate(checks)
    report = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "checks": checks, "exit_code": code}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    log.info("report written to %s, exit code %d", out, code)
    return code


if __name__ == "__main__":
    sys.exit(main())
