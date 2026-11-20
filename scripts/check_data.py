"""Validate data/journey-data.js before building or publishing.

    python scripts/check_data.py

Exits non-zero with a list of problems, so CI blocks a broken deploy.
The rules mirror docs/data-schema.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "journey-data.js"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DRIVE = re.compile(r"^https://drive\.google\.com/(file/d/[\w-]+/view|drive/folders/[\w-]+)$")


def load() -> dict:
    src = DATA.read_text(encoding="utf-8")
    start = src.index("{", src.index("AFM_DATA"))
    return json.loads(src[start: src.rindex("}") + 1])


def main() -> int:
    d = load()
    errs: list[str] = []
    err = errs.append
    topics = set(d["topicFrequency"])

    for key in ("start", "exam", "updated"):
        if not DATE.match(str(d["meta"].get(key, ""))):
            err(f"meta.{key} must be YYYY-MM-DD")

    days = d["days"]
    if [x["day"] for x in days] != list(range(1, len(days) + 1)):
        err("days must be numbered 1..N in order")
    for x in days:
        if x.get("status") not in (None, "Done"):
            err(f"day {x['day']}: status must be null or 'Done'")

    ids = set()
    for q in d["questions"]:
        tag = f"{q.get('id')} {q.get('name')}"
        if q["id"] in ids:
            err(f"{tag}: duplicate id")
        ids.add(q["id"])
        if q["tier"] not in (1, 2, 3):
            err(f"{tag}: tier must be 1, 2 or 3")
        if q["topic"] not in topics:
            err(f"{tag}: topic '{q['topic']}' is not a topicFrequency key")
        if q["day"] is not None and not 1 <= q["day"] <= len(days):
            err(f"{tag}: day out of range")
        year = re.search(r"(\d{4})", q["sitting"])
        if q["tier"] in (1, 2) and year and int(year.group(1)) < 2023 and not q.get("why"):
            err(f"{tag}: core question before 2023 needs a 'why'")
        links = q.get("links") or {}
        for k in ("q", "a", "notes", "xlsx", "folder", "paperFolder"):
            v = links.get(k)
            if v is not None and not DRIVE.match(v):
                err(f"{tag}: links.{k} is not a Google Drive file/folder URL")
        if links.get("notesKind") not in (None, "summary"):
            err(f"{tag}: links.notesKind must be 'summary' or absent")
        for a in q.get("attempts", []):
            if not DATE.match(a.get("date", "")):
                err(f"{tag}: attempt date must be YYYY-MM-DD")
            if q.get("marks") and not 0 <= a.get("marks", -1) <= q["marks"]:
                err(f"{tag}: attempt marks must be between 0 and {q['marks']}")

    for m in d["mocks"]:
        for part, cap in (("q1", 50), ("q2", 25), ("q3", 25), ("prof", 20)):
            v = m.get(part)
            if v is not None and not 0 <= v <= cap:
                err(f"mock {m['id']}: {part} must be 0-{cap}")

    for s in d["skills"]:
        for k in ("communication", "analysis", "scepticism", "commercial"):
            if s.get(k) not in (None, 0, 1, 2, 3):
                err(f"skills {s.get('source')}: {k} must be 0-3 or null")

    for e in d["errors"]:
        if e.get("topic") not in topics:
            err(f"error on {e.get('question')}: unknown topic '{e.get('topic')}'")

    if errs:
        print(f"{len(errs)} problem(s) in {DATA.name}:")
        print("\n".join("  - " + e for e in errs))
        return 1
    core = sum(1 for q in d["questions"] if q["tier"] in (1, 2))
    print(f"OK: {len(d['questions'])} questions ({core} core), {len(days)} days, "
          f"{len(d['mocks'])} mocks, {len(d['errors'])} logged mistakes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
