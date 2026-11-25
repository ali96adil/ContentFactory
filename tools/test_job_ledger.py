#!/usr/bin/env python3
"""Regression tests for local job identity, retries, and fenced worker leases."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import tempfile
import unittest

from job_ledger import ARTIFACT_ROOT, JobLedger, JobLedgerError


T0 = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)
DIGEST = "a" * 64
ARTIFACT_CONTENT = b"TEST_ONLY rendered artifact"
ARTIFACT_DIGEST = hashlib.sha256(ARTIFACT_CONTENT).hexdigest()


def sample_job(**changes: object) -> dict[str, object]:
    job: dict[str, object] = {
        "topic_id": "topic-01", "revision": 1, "stage": "render",
        "locale": "ar", "format": "short_video", "destination": "local",
        "inputs_sha256": DIGEST,
    }
    job.update(changes)
    return job


def complete(ledger: JobLedger, job: dict[str, object], *, now: datetime = T0,
             artifact_type: str = "short_video") -> dict[str, object]:
    path = ledger.database.parent / "artifacts" / "short-ar-TEST_ONLY.mp4"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ARTIFACT_CONTENT)
    return ledger.complete(
        job["job_id"], job["lease_id"], artifact_type=artifact_type,
        artifact_path=path.relative_to(ARTIFACT_ROOT).as_posix(), artifact_sha256=ARTIFACT_DIGEST,
        artifact_bytes=len(ARTIFACT_CONTENT), tool_version="renderer-test", qa_result="PENDING_HUMAN_REVIEW",
        now=now,
    )


class JobLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        evidence = Path(__file__).resolve().parents[1] / "lab" / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="job-ledger-TEST_ONLY-", dir=evidence)
        self.ledger = JobLedger(Path(self.temp.name) / "state.sqlite3")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_enqueue_is_idempotent_under_concurrency(self) -> None:
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(lambda _: self.ledger.enqueue(sample_job(), now=T0), range(16)))
        self.assertEqual(len({row["job_id"] for row in rows}), 1)
        self.assertEqual({row["status"] for row in rows}, {"queued"})

    def test_concurrent_claims_never_double_lease_a_job(self) -> None:
        for number in range(8):
            self.ledger.enqueue(sample_job(topic_id=f"topic-{number}"), now=T0)
        with ThreadPoolExecutor(max_workers=12) as pool:
            claimed = list(pool.map(lambda worker: self.ledger.claim(f"worker-{worker}", now=T0), range(12)))
        jobs = [job for job in claimed if job]
        self.assertEqual(len(jobs), 8)
        self.assertEqual(len({job["job_id"] for job in jobs}), 8)
        self.assertEqual(len({job["lease_id"] for job in jobs}), 8)

    def test_retry_backoff_and_attempt_ceiling(self) -> None:
        queued = self.ledger.enqueue(sample_job(), now=T0)
        first = self.ledger.claim("worker-a", lease_seconds=60, now=T0)
        waiting = self.ledger.retry(first["job_id"], first["lease_id"], "temporary renderer error", delay_seconds=30, now=T0)
        self.assertEqual(waiting["status"], "retry_wait")
        self.assertIsNone(self.ledger.claim("worker-b", now=T0 + timedelta(seconds=29)))
        second = self.ledger.claim("worker-b", now=T0 + timedelta(seconds=30))
        self.assertEqual(second["attempt"], 2)
        again = self.ledger.retry(second["job_id"], second["lease_id"], "temporary renderer error", delay_seconds=0, now=T0 + timedelta(seconds=30))
        third = self.ledger.claim("worker-c", now=T0 + timedelta(seconds=30))
        self.assertEqual(third["attempt"], 3)
        failed = self.ledger.retry(third["job_id"], third["lease_id"], "last attempt failed", now=T0 + timedelta(seconds=30))
        self.assertEqual(failed["status"], "failed")
        self.assertIsNone(self.ledger.claim("worker-d", now=T0 + timedelta(days=1)))
        self.assertEqual(self.ledger.get(queued["job_id"])["attempt"], 3)

    def test_expired_lease_is_fenced_and_completion_is_idempotent(self) -> None:
        self.ledger.enqueue(sample_job(), now=T0)
        first = self.ledger.claim("worker-a", lease_seconds=10, now=T0)
        self.assertTrue(self.ledger.heartbeat(first["job_id"], first["lease_id"], lease_seconds=10, now=T0 + timedelta(seconds=5)))
        self.assertIsNone(self.ledger.claim("worker-b", now=T0 + timedelta(seconds=14)))
        second = self.ledger.claim("worker-b", now=T0 + timedelta(seconds=15))
        self.assertEqual(second["attempt"], 2)
        self.assertFalse(self.ledger.heartbeat(first["job_id"], first["lease_id"], now=T0 + timedelta(seconds=16)))
        with self.assertRaisesRegex(JobLedgerError, "stale"):
            complete(self.ledger, first, now=T0 + timedelta(seconds=16))
        done = complete(self.ledger, second, now=T0 + timedelta(seconds=16))
        self.assertEqual(done["status"], "review_required")
        self.assertEqual(complete(self.ledger, second, now=T0 + timedelta(seconds=17)), done)
        with self.assertRaisesRegex(JobLedgerError, "conflicts"):
            complete(self.ledger, second, now=T0 + timedelta(seconds=17), artifact_type="different")

    def test_expired_final_lease_is_marked_failed(self) -> None:
        queued = self.ledger.enqueue(sample_job(), now=T0)
        for attempt in range(1, 4):
            claimed = self.ledger.claim("worker", lease_seconds=1, now=T0 + timedelta(seconds=attempt * 3))
            self.assertEqual(claimed["attempt"], attempt)
        self.assertIsNone(self.ledger.claim("sweeper", now=T0 + timedelta(seconds=10)))
        failed = self.ledger.get(queued["job_id"])
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(failed["last_error"], "lease expired after final attempt")

    def test_block_and_cancel_revoke_current_lease(self) -> None:
        self.ledger.enqueue(sample_job(), now=T0)
        claimed = self.ledger.claim("worker", now=T0)
        blocked = self.ledger.block(claimed["job_id"], claimed["lease_id"], "rights missing", now=T0)
        self.assertEqual(blocked["status"], "blocked")
        self.assertTrue(self.ledger.cancel(claimed["job_id"], now=T0))
        self.assertEqual(self.ledger.get(claimed["job_id"])["status"], "cancelled")
        with self.assertRaisesRegex(JobLedgerError, "stale"):
            complete(self.ledger, claimed, now=T0)
        self.assertFalse(self.ledger.cancel(claimed["job_id"], now=T0))

    def test_invalid_destinations_digests_and_artifact_paths_reject(self) -> None:
        with self.assertRaisesRegex(JobLedgerError, "local destination"):
            self.ledger.enqueue(sample_job(destination="public"), now=T0)
        with self.assertRaisesRegex(JobLedgerError, "inputs_sha256"):
            self.ledger.enqueue(sample_job(inputs_sha256="not-a-digest"), now=T0)
        queued = self.ledger.enqueue(sample_job(), now=T0)
        claimed = self.ledger.claim("worker", now=T0)
        for path in ("/tmp/file.mp4", "../file.mp4", "artifacts/../../private", r"artifacts\file.mp4"):
            with self.subTest(path=path), self.assertRaises(JobLedgerError):
                self.ledger.complete(
                    queued["job_id"], claimed["lease_id"], artifact_type="short_video",
                    artifact_path=path, artifact_sha256=ARTIFACT_DIGEST, artifact_bytes=100,
                    tool_version="test", now=T0,
                )

    def test_naive_timestamps_and_wrong_schema_reject(self) -> None:
        with self.assertRaisesRegex(JobLedgerError, "UTC offset"):
            self.ledger.enqueue(sample_job(), now=datetime(2026, 11, 25, 12))
        with self.ledger._connect() as db:
            db.execute("UPDATE job_meta SET value='999' WHERE name='schema_version'")
        with self.assertRaisesRegex(JobLedgerError, "schema version"):
            self.ledger.get("missing")

    def test_database_paths_must_be_ignored_local_storage(self) -> None:
        outside = JobLedger(Path(__file__).resolve().parents[1] / "tools" / "tracked-state.sqlite3")
        with self.assertRaisesRegex(JobLedgerError, "lab/imports/ or lab/evidence/"):
            outside.get("missing")
        target = Path(self.temp.name) / "target.sqlite3"
        target.touch()
        link = Path(self.temp.name) / "linked.sqlite3"
        link.symlink_to(target)
        with self.assertRaisesRegex(JobLedgerError, "symbolic link"):
            JobLedger(link).get("missing")

    def test_malformed_public_arguments_fail_with_contract_errors(self) -> None:
        with self.assertRaisesRegex(JobLedgerError, "job must be an object"):
            self.ledger.enqueue([], now=T0)
        with self.assertRaisesRegex(JobLedgerError, "revision"):
            self.ledger.enqueue(sample_job(revision=True), now=T0)
        with self.assertRaisesRegex(JobLedgerError, "artifact_sha256"):
            self.ledger.complete(
                "job", "lease", artifact_type="short_video", artifact_path="artifacts/out.mp4",
                artifact_sha256=None, artifact_bytes=1, tool_version="test", now=T0,
            )
        with self.assertRaisesRegex(JobLedgerError, "qa_result"):
            self.ledger.complete(
                "job", "lease", artifact_type="short_video", artifact_path="artifacts/out.mp4",
                artifact_sha256=ARTIFACT_DIGEST, artifact_bytes=1, tool_version="test",
                qa_result=[], now=T0,
            )
        with self.assertRaisesRegex(JobLedgerError, "relative"):
            self.ledger.complete(
                "job", "lease", artifact_type="short_video", artifact_path=".",
                artifact_sha256=ARTIFACT_DIGEST, artifact_bytes=1, tool_version="test", now=T0,
            )
        with self.assertRaisesRegex(JobLedgerError, "job_id"):
            self.ledger.get([])

    def test_complete_verifies_artifact_presence_size_digest_and_symlinks(self) -> None:
        queued = self.ledger.enqueue(sample_job(), now=T0)
        claimed = self.ledger.claim("worker", now=T0)
        artifact_dir = self.ledger.database.parent / "artifacts"
        artifact_dir.mkdir(parents=True)
        artifact = artifact_dir / "real-TEST_ONLY.mp4"
        artifact.write_bytes(ARTIFACT_CONTENT)
        reference = artifact.relative_to(ARTIFACT_ROOT).as_posix()
        args = dict(
            artifact_type="short_video", artifact_path=reference,
            artifact_sha256=ARTIFACT_DIGEST, artifact_bytes=len(ARTIFACT_CONTENT),
            tool_version="test", now=T0,
        )
        with self.assertRaisesRegex(JobLedgerError, "regular file"):
            self.ledger.complete(claimed["job_id"], claimed["lease_id"],
                                 **{**args, "artifact_path": reference + ".missing"})
        with self.assertRaisesRegex(JobLedgerError, "artifact_bytes"):
            self.ledger.complete(claimed["job_id"], claimed["lease_id"],
                                 **{**args, "artifact_bytes": len(ARTIFACT_CONTENT) + 1})
        with self.assertRaisesRegex(JobLedgerError, "artifact_sha256"):
            self.ledger.complete(claimed["job_id"], claimed["lease_id"],
                                 **{**args, "artifact_sha256": "c" * 64})
        link = artifact_dir / "linked-TEST_ONLY.mp4"
        link.symlink_to(artifact)
        with self.assertRaisesRegex(JobLedgerError, "symbolic links"):
            self.ledger.complete(claimed["job_id"], claimed["lease_id"],
                                 **{**args, "artifact_path": link.relative_to(ARTIFACT_ROOT).as_posix()})
        done = self.ledger.complete(claimed["job_id"], claimed["lease_id"], **args)
        self.assertEqual(done["status"], "review_required")
        self.assertEqual(done["artifact_sha256"], ARTIFACT_DIGEST)


if __name__ == "__main__":
    unittest.main(verbosity=2)
