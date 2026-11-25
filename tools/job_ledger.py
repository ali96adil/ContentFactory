#!/usr/bin/env python3
"""Local SQLite job lifecycle store; no network, approval, or publishing entry point."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import secrets
import sqlite3
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DATABASE_ROOTS = (ROOT / "lab" / "imports", ROOT / "lab" / "evidence")
SCHEMA_VERSION = "1"
MAX_ATTEMPTS = 3  # One initial attempt plus two retries.
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
JOB_FIELDS = (
    "topic_id", "revision", "stage", "locale", "format", "destination", "inputs_sha256"
)


class JobLedgerError(ValueError):
    """Raised when a job operation violates the local lifecycle contract."""


def utc_timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise JobLedgerError("timestamps must include a UTC offset")
    return current.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise JobLedgerError("timestamp must be ISO 8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise JobLedgerError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _validate_job(job: dict[str, Any]) -> dict[str, str]:
    if not isinstance(job, dict):
        raise JobLedgerError("job must be an object")
    if set(job) != set(JOB_FIELDS):
        raise JobLedgerError(f"job must contain exactly: {', '.join(JOB_FIELDS)}")
    result: dict[str, str] = {}
    for field in JOB_FIELDS:
        value = job[field]
        if not isinstance(value, (str, int)) or isinstance(value, bool) or not str(value).strip():
            raise JobLedgerError(f"{field} must be a non-empty string or integer")
        result[field] = str(value).strip()
    if result["destination"] != "local":
        raise JobLedgerError("only the local destination is allowed")
    if not SHA256_RE.fullmatch(result["inputs_sha256"]):
        raise JobLedgerError("inputs_sha256 must be a lowercase SHA-256 digest")
    return result


def _safe_artifact_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise JobLedgerError("artifact path must be a non-empty relative POSIX path")
    path = PurePosixPath(value)
    if not path.parts or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise JobLedgerError("artifact path must stay relative to the job workspace")
    if path.as_posix() != value:
        raise JobLedgerError("artifact path must be normalized")
    return value


def _validate_lease_identity(job_id: str, lease_id: str) -> None:
    if not isinstance(job_id, str) or not job_id.strip():
        raise JobLedgerError("job_id must be non-empty")
    if not isinstance(lease_id, str) or not lease_id.strip():
        raise JobLedgerError("lease_id must be non-empty")


class JobLedger:
    """Transactional SQLite job state with lease fencing and local-only completion."""

    def __init__(self, database: Path):
        self.database = Path(database)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        if self.database.suffix.lower() != ".sqlite3" or self.database.is_symlink():
            raise JobLedgerError("database must be a .sqlite3 file and must not be a symbolic link")
        resolved = self.database.resolve()
        if not any(resolved.is_relative_to(root.resolve()) for root in ALLOWED_DATABASE_ROOTS):
            raise JobLedgerError("database must be under lab/imports/ or lab/evidence/")
        self.database = resolved
        self.database.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.database, timeout=10, isolation_level=None)
        try:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=10000")
            db.execute("""CREATE TABLE IF NOT EXISTS job_meta (
                name TEXT PRIMARY KEY, value TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                identity_json TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN (
                    'queued','running','retry_wait','review_required','blocked','failed','cancelled'
                )),
                attempt INTEGER NOT NULL DEFAULT 0 CHECK(attempt >= 0),
                worker_id TEXT,
                lease_id TEXT,
                lease_expires_at TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                available_at TEXT NOT NULL,
                last_error TEXT,
                completion_lease_id TEXT,
                artifact_type TEXT,
                artifact_path TEXT,
                artifact_sha256 TEXT,
                artifact_bytes INTEGER,
                tool_version TEXT,
                qa_result TEXT
            )""")
            row = db.execute("SELECT value FROM job_meta WHERE name='schema_version'").fetchone()
            if row is None:
                db.execute("INSERT INTO job_meta(name,value) VALUES('schema_version',?)", (SCHEMA_VERSION,))
            elif row["value"] != SCHEMA_VERSION:
                raise JobLedgerError(f"unsupported job ledger schema version: {row['value']}")
            yield db
        finally:
            db.close()

    @staticmethod
    def _record(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}

    def enqueue(self, job: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
        identity = _validate_job(job)
        identity_json = json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        key = hashlib.sha256(identity_json.encode("utf-8")).hexdigest()
        stamp = utc_timestamp(now)
        job_id = secrets.token_hex(16)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""INSERT INTO jobs(
                job_id,idempotency_key,identity_json,status,created_at,available_at
            ) VALUES(?,?,?,'queued',?,?) ON CONFLICT(idempotency_key) DO NOTHING""",
                       (job_id, key, identity_json, stamp, stamp))
            row = db.execute("SELECT * FROM jobs WHERE idempotency_key=?", (key,)).fetchone()
            db.execute("COMMIT")
            return self._record(row) or {}

    def claim(self, worker_id: str, *, lease_seconds: int = 60,
              now: datetime | None = None) -> dict[str, Any] | None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise JobLedgerError("worker_id must be non-empty")
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) or not 1 <= lease_seconds <= 3600:
            raise JobLedgerError("lease_seconds must be an integer from 1 through 3600")
        current = _parse_time(utc_timestamp(now))
        stamp = utc_timestamp(current)
        expires = utc_timestamp(current + timedelta(seconds=lease_seconds))
        lease_id = secrets.token_urlsafe(24)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""UPDATE jobs SET status='failed', finished_at=?, lease_id=NULL,
                lease_expires_at=NULL, worker_id=NULL, last_error=COALESCE(last_error,'lease expired after final attempt')
                WHERE status='running' AND lease_expires_at<=? AND attempt>=?""",
                       (stamp, stamp, MAX_ATTEMPTS))
            row = db.execute("""SELECT * FROM jobs WHERE
                (status IN ('queued','retry_wait') AND available_at<=?) OR
                (status='running' AND lease_expires_at<=? AND attempt<?)
                ORDER BY created_at,job_id LIMIT 1""",
                       (stamp, stamp, MAX_ATTEMPTS)).fetchone()
            if row is None:
                db.execute("COMMIT")
                return None
            attempt = row["attempt"] + 1
            db.execute("""UPDATE jobs SET status='running',attempt=?,worker_id=?,lease_id=?,
                lease_expires_at=?,started_at=COALESCE(started_at,?),finished_at=NULL
                WHERE job_id=?""",
                       (attempt, worker_id.strip(), lease_id, expires, stamp, row["job_id"]))
            claimed = db.execute("SELECT * FROM jobs WHERE job_id=?", (row["job_id"],)).fetchone()
            db.execute("COMMIT")
            return self._record(claimed)

    def heartbeat(self, job_id: str, lease_id: str, *, lease_seconds: int = 60,
                  now: datetime | None = None) -> bool:
        _validate_lease_identity(job_id, lease_id)
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) or not 1 <= lease_seconds <= 3600:
            raise JobLedgerError("lease_seconds must be an integer from 1 through 3600")
        current = _parse_time(utc_timestamp(now))
        stamp = utc_timestamp(current)
        expires = utc_timestamp(current + timedelta(seconds=lease_seconds))
        with self._connect() as db:
            result = db.execute("""UPDATE jobs SET lease_expires_at=? WHERE job_id=?
                AND status='running' AND lease_id=? AND lease_expires_at>?""",
                                (expires, job_id, lease_id, stamp))
            return result.rowcount == 1

    def complete(self, job_id: str, lease_id: str, *, artifact_type: str,
                 artifact_path: str, artifact_sha256: str, artifact_bytes: int,
                 tool_version: str, qa_result: str = "PASS",
                 now: datetime | None = None) -> dict[str, Any]:
        _validate_lease_identity(job_id, lease_id)
        if not isinstance(artifact_type, str) or not artifact_type.strip():
            raise JobLedgerError("artifact_type must be non-empty")
        if not isinstance(tool_version, str) or not tool_version.strip():
            raise JobLedgerError("tool_version must be non-empty")
        if not isinstance(artifact_sha256, str) or not SHA256_RE.fullmatch(artifact_sha256):
            raise JobLedgerError("artifact_sha256 must be a lowercase SHA-256 digest")
        if not isinstance(artifact_bytes, int) or isinstance(artifact_bytes, bool) or artifact_bytes < 0:
            raise JobLedgerError("artifact_bytes must be a non-negative integer")
        if not isinstance(qa_result, str) or qa_result not in {"PASS", "PENDING_HUMAN_REVIEW"}:
            raise JobLedgerError("qa_result must be PASS or PENDING_HUMAN_REVIEW")
        safe_path = _safe_artifact_path(artifact_path)
        stamp = utc_timestamp(now)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None:
                db.execute("ROLLBACK")
                raise JobLedgerError("job not found")
            supplied = (artifact_type.strip(), safe_path, artifact_sha256, artifact_bytes, tool_version.strip(), qa_result)
            previous = (row["artifact_type"], row["artifact_path"], row["artifact_sha256"], row["artifact_bytes"], row["tool_version"], row["qa_result"])
            if row["status"] == "review_required" and row["completion_lease_id"] == lease_id:
                if supplied != previous:
                    db.execute("ROLLBACK")
                    raise JobLedgerError("idempotent completion conflicts with the recorded artifact")
                db.execute("COMMIT")
                return self._record(row) or {}
            if (row["status"] != "running" or row["lease_id"] != lease_id
                    or row["lease_expires_at"] is None or row["lease_expires_at"] <= stamp):
                db.execute("ROLLBACK")
                raise JobLedgerError("job lease is stale, expired, or no longer owned by this worker")
            db.execute("""UPDATE jobs SET status='review_required',finished_at=?,worker_id=NULL,
                lease_id=NULL,lease_expires_at=NULL,completion_lease_id=?,artifact_type=?,artifact_path=?,
                artifact_sha256=?,artifact_bytes=?,tool_version=?,qa_result=? WHERE job_id=?""",
                       (stamp, lease_id, *supplied, job_id))
            completed = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            db.execute("COMMIT")
            return self._record(completed) or {}

    def retry(self, job_id: str, lease_id: str, reason: str, *, delay_seconds: int | None = None,
              now: datetime | None = None) -> dict[str, Any]:
        _validate_lease_identity(job_id, lease_id)
        if not isinstance(reason, str) or not reason.strip():
            raise JobLedgerError("retry reason must be non-empty and scrubbed of credentials")
        current = _parse_time(utc_timestamp(now))
        stamp = utc_timestamp(current)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None or row["status"] != "running" or row["lease_id"] != lease_id:
                db.execute("ROLLBACK")
                raise JobLedgerError("job lease is stale or no longer owned by this worker")
            if row["lease_expires_at"] <= stamp:
                db.execute("ROLLBACK")
                raise JobLedgerError("expired lease cannot schedule a retry")
            if row["attempt"] >= MAX_ATTEMPTS:
                status = "failed"
                available_at = stamp
            else:
                delay = delay_seconds if delay_seconds is not None else 30 * (2 ** (row["attempt"] - 1))
                if not isinstance(delay, int) or isinstance(delay, bool) or not 0 <= delay <= 86400:
                    db.execute("ROLLBACK")
                    raise JobLedgerError("delay_seconds must be from 0 through 86400")
                status = "retry_wait"
                available_at = utc_timestamp(current + timedelta(seconds=delay))
            db.execute("""UPDATE jobs SET status=?,available_at=?,last_error=?,finished_at=?,
                worker_id=NULL,lease_id=NULL,lease_expires_at=NULL WHERE job_id=?""",
                       (status, available_at, reason.strip()[:1000], stamp if status == "failed" else None, job_id))
            updated = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            db.execute("COMMIT")
            return self._record(updated) or {}

    def block(self, job_id: str, lease_id: str, reason: str, *, now: datetime | None = None) -> dict[str, Any]:
        _validate_lease_identity(job_id, lease_id)
        if not isinstance(reason, str) or not reason.strip():
            raise JobLedgerError("block reason must be non-empty and scrubbed of credentials")
        stamp = utc_timestamp(now)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if (row is None or row["status"] != "running" or row["lease_id"] != lease_id
                    or row["lease_expires_at"] <= stamp):
                db.execute("ROLLBACK")
                raise JobLedgerError("job lease is stale, expired, or no longer owned by this worker")
            db.execute("""UPDATE jobs SET status='blocked',last_error=?,finished_at=?,worker_id=NULL,
                lease_id=NULL,lease_expires_at=NULL WHERE job_id=?""",
                       (reason.strip()[:1000], stamp, job_id))
            updated = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            db.execute("COMMIT")
            return self._record(updated) or {}

    def cancel(self, job_id: str, *, now: datetime | None = None) -> bool:
        if not isinstance(job_id, str) or not job_id.strip():
            raise JobLedgerError("job_id must be non-empty")
        stamp = utc_timestamp(now)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            result = db.execute("""UPDATE jobs SET status='cancelled',finished_at=?,worker_id=NULL,
                lease_id=NULL,lease_expires_at=NULL WHERE job_id=?
                AND status IN ('queued','running','retry_wait','blocked')""", (stamp, job_id))
            db.execute("COMMIT")
            return result.rowcount == 1

    def get(self, job_id: str) -> dict[str, Any] | None:
        if not isinstance(job_id, str) or not job_id.strip():
            raise JobLedgerError("job_id must be non-empty")
        with self._connect() as db:
            return self._record(db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone())
