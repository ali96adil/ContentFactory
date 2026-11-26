#!/usr/bin/env python3
"""Compare a local post against recent comparable metrics; never publishes or calls APIs."""

from __future__ import annotations

import argparse
import csv
import json
import math
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from statistics import median

FIELDS = {
    "platform", "account_id", "topic_id", "post_id", "language", "format",
    "role", "observed_at", "age_hours", "impressions", "views",
    "avg_watch_seconds", "duration_seconds", "saves", "shares",
    "rights_status", "quality_status", "external_cost_usd", "data_origin",
}
PLATFORMS = {"youtube", "tiktok", "instagram", "facebook"}
ROOT = Path(__file__).resolve().parents[1]
ALLOWED_LEDGER_ROOTS = (ROOT / "lab" / "imports", ROOT / "lab" / "evidence")
LEDGER_SCHEMA_VERSION = "1"


def number(row: dict[str, str], field: str) -> float:
    try:
        value = float(row[field])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")
    if value < 0:
        raise ValueError(f"{field} cannot be negative")
    return value


def rate(row: dict[str, str]) -> dict[str, float] | None:
    impressions, views, duration = (number(row, field) for field in
                                    ("impressions", "views", "duration_seconds"))
    if impressions == 0 or views == 0 or duration == 0:
        return None
    return {
        "view_rate": views / impressions,
        "retention": number(row, "avg_watch_seconds") / duration,
        "save_share_rate": (number(row, "saves") + number(row, "shares")) / views,
    }


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError("CSV contains duplicate column names")
        missing = FIELDS - set(headers)
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    for index, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"row {index}: contains more values than the CSV header")
        if any(value is None for value in row.values()):
            raise ValueError(f"row {index}: has fewer values than the CSV header")
        row["platform"] = row["platform"].strip().lower()
        row["role"] = row["role"].strip().lower()
        if row["platform"] not in PLATFORMS:
            raise ValueError(f"row {index}: unsupported platform {row['platform']!r}")
        if row["role"] not in {"baseline", "candidate"}:
            raise ValueError(f"row {index}: role must be baseline or candidate")
        origin = row["data_origin"].strip().lower()
        is_synthetic = "synthetic" in origin or "test_only" in origin
        if not is_synthetic and origin not in {"manual_export", "manual_entry"}:
            raise ValueError(f"row {index}: data_origin must be manual_export, manual_entry, or TEST_ONLY")
        try:
            datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"row {index}: observed_at must be an ISO 8601 date/time") from exc
        for field in ("age_hours", "impressions", "views", "avg_watch_seconds",
                      "duration_seconds", "saves", "shares", "external_cost_usd"):
            number(row, field)
    return rows


def load_ledger_rows(path: Path) -> list[dict[str, str]]:
    if path.is_symlink():
        raise ValueError("ledger must not be a symbolic link")
    resolved = path.resolve()
    if not any(resolved.is_relative_to(root.resolve()) for root in ALLOWED_LEDGER_ROOTS):
        raise ValueError("ledger must be under lab/imports/ or lab/evidence/")
    if not resolved.is_file():
        raise FileNotFoundError(f"metrics ledger not found: {resolved}")
    try:
        with sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True) as connection:
            version = connection.execute(
                "SELECT value FROM ledger_meta WHERE name='schema_version'"
            ).fetchone()
            if version is None or version[0] != LEDGER_SCHEMA_VERSION:
                raise ValueError("unsupported or missing metrics ledger schema version")
            records = connection.execute(
                "SELECT row_key,content_sha256,row_json FROM metric_snapshots ORDER BY row_key"
            ).fetchall()
    except sqlite3.Error as exc:
        raise ValueError(f"cannot read metrics ledger: {exc}") from exc

    rows: list[dict[str, str]] = []
    for row_key, expected_digest, row_json in records:
        if not all(isinstance(value, str) for value in (row_key, expected_digest, row_json)):
            raise ValueError("metrics ledger contains invalid row types")
        digest = hashlib.sha256(row_json.encode("utf-8")).hexdigest()
        if digest != expected_digest:
            raise ValueError("metrics ledger row integrity check failed")
        row = json.loads(row_json)
        if not isinstance(row, dict) or set(row) != FIELDS or any(not isinstance(value, str) for value in row.values()):
            raise ValueError("metrics ledger row does not match the current CSV contract")
        identity = json.dumps(
            [row[field] for field in ("platform", "account_id", "post_id", "observed_at")],
            ensure_ascii=False, separators=(",", ":"),
        )
        if hashlib.sha256(identity.encode("utf-8")).hexdigest() != row_key:
            raise ValueError("metrics ledger identity check failed")
        rows.append(row)
    return rows


def compare(rows: list[dict[str, str]]) -> dict[str, object]:
    baselines = [row for row in rows if row["role"] == "baseline"]
    candidates = [row for row in rows if row["role"] == "candidate"]
    if not candidates:
        raise ValueError("CSV must include at least one candidate row")
    is_synthetic = any(
        "synthetic" in row["data_origin"].strip().lower()
        or "test_only" in row["data_origin"].strip().lower()
        for row in rows
    )

    decisions = []
    positive_topics: set[str] = set()
    all_quality_approved = True
    all_rights_verified = True
    all_costs_within_cap = True
    for candidate in candidates:
        key = (candidate["platform"], candidate["account_id"],
               candidate["language"], candidate["format"])
        age = number(candidate, "age_hours")
        comparable = [
            row for row in baselines
            if (row["platform"], row["account_id"], row["language"], row["format"]) == key
            and abs(number(row, "age_hours") - age) <= 1
        ]
        comparable.sort(key=lambda row: row["observed_at"], reverse=True)
        comparable = comparable[:10]
        candidate_metrics = rate(candidate)
        baseline_metrics = [rate(row) for row in comparable]
        baseline_metrics = [item for item in baseline_metrics if item is not None]
        quality_ok = candidate["quality_status"].strip().lower() == "human_approved"
        rights_ok = candidate["rights_status"].strip().lower() == "verified"
        cost_ok = number(candidate, "external_cost_usd") <= 0
        all_quality_approved &= quality_ok
        all_rights_verified &= rights_ok
        all_costs_within_cap &= cost_ok

        decision: dict[str, object] = {
            "platform": candidate["platform"], "topic_id": candidate["topic_id"],
            "post_id": candidate["post_id"], "comparable_baselines": len(baseline_metrics),
            "quality_status": candidate["quality_status"],
            "rights_status": candidate["rights_status"],
            "recommendation": "exploratory",
            "reason": "fewer than five valid comparable baseline posts",
            "next_variable": "collect another comparable measurement; do not scale",
            "quality_gate": "PASS" if quality_ok else "HOLD_FOR_HUMAN_REVIEW",
            "rights_gate": "PASS" if rights_ok else "BLOCKED_UNVERIFIED_RIGHTS",
            "external_cost_usd": number(candidate, "external_cost_usd"),
        }
        if is_synthetic:
            decision.update(
                recommendation="test_only_no_action",
                reason="synthetic TEST_ONLY input is for tool validation only",
                next_variable="do not use this output for publication, scaling, or production decisions",
            )
        elif len(baseline_metrics) >= 5 and candidate_metrics:
            base = {name: median(item[name] for item in baseline_metrics)
                    for name in ("view_rate", "retention", "save_share_rate")}
            decision["candidate_metrics"] = candidate_metrics
            decision["baseline_medians"] = base
            if (candidate_metrics["view_rate"] >= base["view_rate"] * 1.15
                    and candidate_metrics["retention"] <= base["retention"] * 0.85):
                decision.update(
                    recommendation="hook_experiment",
                    reason="view rate is at least 15% above baseline while retention is at least 15% below it",
                    next_variable="change only the opening hook in the next comparable episode",
                )
                positive_topics.add(candidate["topic_id"])
            elif (candidate["platform"] in {"instagram", "facebook"}
                    and candidate_metrics["save_share_rate"] >= base["save_share_rate"] * 1.20):
                decision.update(
                    recommendation="carousel_experiment",
                    reason="save/share rate is at least 20% above baseline",
                    next_variable="test one carousel version of the same information",
                )
                positive_topics.add(candidate["topic_id"])
            else:
                decision.update(
                    recommendation="repeat_one_variable",
                    reason="no rule threshold was met against the comparable baseline",
                    next_variable="repeat once while changing only one editorial variable",
                )
        elif not candidate_metrics:
            decision["reason"] = "candidate has zero denominator data; keep it exploratory"
        decisions.append(decision)

    scale_reasons = []
    if len(positive_topics) < 2:
        scale_reasons.append("positive signal has not repeated across two distinct topics")
    if not all_quality_approved:
        scale_reasons.append("human quality approval is incomplete")
    if not all_rights_verified:
        scale_reasons.append("rights verification is incomplete")
    if not all_costs_within_cap:
        scale_reasons.append("one or more candidate rows exceed the zero external-spend cap")
    if is_synthetic:
        scale_reasons.append("synthetic TEST_ONLY data cannot authorize a production decision")
    return {
        "mode": "TEST_ONLY_SYNTHETIC" if is_synthetic else "LOCAL_IMPORT_REVIEW",
        "source_rows": len(rows), "candidate_count": len(candidates),
        "decisions": decisions, "scale_eligible": not scale_reasons,
        "scale_blockers": scale_reasons, "export_allowed": False, "publish_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", help="local CSV export; no network access is used")
    parser.add_argument("--ledger", type=Path, help="read previously imported local snapshots from SQLite")
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()
    if (args.input is None) == (args.ledger is None):
        parser.error("provide exactly one of an input CSV or --ledger")
    try:
        result = compare(load_ledger_rows(args.ledger) if args.ledger else load_rows(args.input))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            parser.error(f"output already exists; choose a new path to avoid overwriting: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
