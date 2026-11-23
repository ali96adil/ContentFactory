#!/usr/bin/env python3
"""Compare a local post against recent comparable metrics; never publishes or calls APIs."""

from __future__ import annotations

import argparse
import csv
import json
import math
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
        missing = FIELDS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    for index, row in enumerate(rows, start=2):
        row["platform"] = row["platform"].strip().lower()
        row["role"] = row["role"].strip().lower()
        if row["platform"] not in PLATFORMS:
            raise ValueError(f"row {index}: unsupported platform {row['platform']!r}")
        if row["role"] not in {"baseline", "candidate"}:
            raise ValueError(f"row {index}: role must be baseline or candidate")
        datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00"))
        for field in ("age_hours", "impressions", "views", "avg_watch_seconds",
                      "duration_seconds", "saves", "shares", "external_cost_usd"):
            number(row, field)
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
    parser.add_argument("input", type=Path, help="local CSV export; no network access is used")
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args()
    try:
        result = compare(load_rows(args.input))
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
