"""Local qualification harness. No provider calls or publishing entry point."""
import hashlib
import json
import sqlite3


def process(state, item, inspect):
    payload = json.dumps(item, sort_keys=True)
    key = hashlib.sha256(payload.encode()).hexdigest()
    with sqlite3.connect(state, timeout=10) as db:
        db.execute("CREATE TABLE IF NOT EXISTS attempts (key TEXT PRIMARY KEY, status TEXT, count INTEGER)")
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT status,count FROM attempts WHERE key=?", (key,)).fetchone()
        if previous and (previous[0] != "retry" or previous[1] >= 2):
            return previous
        count = (previous[1] if previous else 0) + 1
        if item.get("rights") != "verified" or item.get("destination") != "local":
            status = "blocked"
        else:
            try:
                inspect()
            except TimeoutError:
                status = "retry"
            else:
                status = "awaiting_review"
        db.execute("INSERT OR REPLACE INTO attempts VALUES (?,?,?)", (key,status,count))
        return status,count
