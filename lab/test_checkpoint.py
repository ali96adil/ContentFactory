import json
import pathlib
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from checkpoint import process

def verify():
    with tempfile.TemporaryDirectory() as directory:
        state = pathlib.Path(directory) / "state.db"
        backup = pathlib.Path(directory) / "backup.db"
        item = {"topic":"coffee-camera","revision":1,"rights":"verified","destination":"local"}
        calls = []
        lock = Lock()
        def inspect():
            with lock:
                calls.append("inspect")
        def timeout():
            raise TimeoutError
        assert process(state, item, timeout) == ("retry",1)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: process(state,item,inspect),range(4)))
        assert results == [("awaiting_review",2)] * 4 and len(calls)==1
        assert process(state,{**item,"rights":"unverified"},inspect) == ("blocked",1)
        assert process(state,{**item,"destination":"public"},inspect) == ("blocked",1)
        other = {**item,"revision":2}
        assert process(state,other,timeout) == ("retry",1)
        assert process(state,other,timeout) == ("retry",2)
        assert process(state,other,inspect) == ("retry",2)
        with sqlite3.connect(state) as source, sqlite3.connect(backup) as restored:
            source.backup(restored)
            assert restored.execute("pragma integrity_check").fetchone() == ("ok",)
        state.unlink()
        assert process(backup,item,inspect) == ("awaiting_review",2) and len(calls)==1
    return ["timeout/retry","concurrent deduplication","unverified rights","public destination",
            "retry ceiling","SQLite snapshot restore"]

if __name__ == "__main__":
    print(json.dumps({"passed":verify()},indent=2))
