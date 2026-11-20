#!/usr/bin/env python3
"""Collect Met Open Access identifiers and publish run-level evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(timezone.utc)
source_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds=11"
request = Request(source_url, headers={"Accept": "application/json", "User-Agent": "LetsArt observability"})
with urlopen(request, timeout=30) as response:
    source = json.loads(response.read().decode("utf-8"))
object_ids = [int(value) for value in source.get("objectIDs", []) if isinstance(value, int)]
if not object_ids or len(object_ids) != len(set(object_ids)):
    raise RuntimeError("Met response has no unique object identifiers")
raw = {"source": "The Metropolitan Museum of Art Collection API", "source_url": source_url, "observed_at": now.isoformat(), "department_id": 11, "object_ids": object_ids}
raw_bytes = json.dumps(raw, ensure_ascii=False, sort_keys=True).encode("utf-8")
raw_path = ROOT / "data" / "raw" / "met_department_11.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_bytes(raw_bytes + b"\n")
payload = {
    "schema": "lets_observability_v1",
    "run_id": f"art-unimplemented-{now.strftime('%Y%m%dT%H%M%SZ')}",
    "observed_at": now.isoformat(),
    "service_id": "art",
    "source": "met_open_access",
    "stages": {
        "collect": {"status": "success", "ok": len(object_ids), "artifact": True},
        "analyze": {"status": "not_started", "ok": None},
        "quality": {"status": "success", "quality_issue_count": 0, "detail": "unique object identifiers"},
        "publish": {"status": "success", "artifact": True},
    },
    "counts": {"records": len(object_ids)},
    "artifacts": {"raw": hashlib.sha256(raw_bytes).hexdigest()},
    "note": "Met Open Access department 11 identifier snapshot.",
}
out = ROOT / "data" / "observability" / "latest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Met objects observed: {len(object_ids)}")
