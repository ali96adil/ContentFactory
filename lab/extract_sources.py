"""Smoke test extraction separately from editorial claim verification."""
import hashlib
import json
import pathlib
import urllib.request

import trafilatura

sources = [
    ("https://www.cl.cam.ac.uk/coffee/coffee.html", ["JPEG","coffee"]),
    ("https://www.cl.cam.ac.uk/coffee/qsf/coffee.html", ["1991","coffee"]),
]
results = []
for url, tokens in sources:
    with urllib.request.urlopen(url, timeout=15) as response:
        raw = response.read(2_000_000)
    extraction = trafilatura.extract(raw.decode("utf-8",errors="replace")) or ""
    assert all(token in extraction for token in tokens), url
    results.append(dict(url=url,source_sha256=hashlib.sha256(raw).hexdigest(),
                        extracted_characters=len(extraction),tokens=tokens))
pathlib.Path("evidence/source-extraction.json").write_text(json.dumps(results,indent=2))
