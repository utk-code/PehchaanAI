"""Smoke test for the real face model + search stack.

Uploads one FG-NET reference image to the running backend and verifies the
full path end to end: auth -> InsightFace embedding extraction on the server
-> cosine search over the populated corpus -> correctly ranked same-person
result.

Usage (backend must be running on :8000):

    python scripts/smoke_search.py

Environment overrides:
    PEHCHAANAI_BASE   backend base URL (default http://localhost:8000)
    PEHCHAANAI_IMAGE  path to a face image (default FGNET/images/001A08.JPG)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = os.environ.get("PEHCHAANAI_BASE", "http://localhost:8000")
IMG = os.environ.get(
    "PEHCHAANAI_IMAGE", r"D:\Projects\Project Ace\FGNET\images\001A08.JPG"
)
DB_PATH = os.environ.get("PEHCHAANAI_DB", r"D:\Projects\Project Ace\pehchaanai.db")


def api(method, path, token=None, data=None, files=None, form=None):
    url = BASE + path
    headers = {}
    body = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if files is not None:
        boundary = "----smoke" + uuid.uuid4().hex
        buf = []
        with open(files, "rb") as f:
            fdata = f.read()
        buf.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="img.jpg"\r\n'
                f"Content-Type: image/jpeg\r\n\r\n"
            ).encode()
        )
        buf.append(fdata)
        buf.append(b"\r\n")
        for k, v in (form or {}).items():
            buf.append(
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{k}"\r\n'
                    f"\r\n{v}\r\n"
                ).encode()
            )
        buf.append(f"--{boundary}--\r\n".encode())
        body = b"".join(buf)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif isinstance(data, dict):
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _expected_person(image_path: str) -> str:
    """FG-NET filenames look like 001A08.JPG -> person '001' (as stored)."""
    name = os.path.splitext(os.path.basename(image_path))[0]
    return name.split("A")[0]


def main() -> int:
    persona = _expected_person(IMG)

    status, reg = api(
        "POST",
        "/auth/register",
        data={
            "email": f"smoke_{uuid.uuid4().hex[:8]}@test.dev",
            "full_name": "Smoke Test",
            "password": "TestPass123!",
        },
    )
    if status not in (200, 201):
        print(f"[FAIL] register/login: HTTP {status} {reg}")
        return 1
    token = reg.get("access_token")
    print(f"[ OK ] register/login (token len {len(token)})")

    if not os.path.exists(IMG):
        print(f"[FAIL] image missing: {IMG}")
        return 1

    status, ph = api("POST", "/search/photo", token=token, files=IMG)
    if status != 200:
        print(f"[FAIL] /search/photo: HTTP {status} {ph}")
        return 1

    scanned = ph.get("total_records")
    results = ph.get("results", [])
    print(f"[ OK ] model + search: scanned {scanned} records, {len(results)} results")

    top = results[0] if results else None
    if not top:
        print("[FAIL] search returned 0 results")
        return 1
    print(
        f"[ OK ] top candidate: person {top['person_id']} "
        f"sim={top['face_similarity']:.3f}"
    )
    for r in results[:5]:
        print(
            f"        person {r['person_id']:>8} age={r['age']:>3} "
            f"sim={r['face_similarity']:.3f}"
        )

    if top["person_id"] == persona:
        print(f"[ OK ] expected query person {persona} ranked first")
    else:
        print(f"[FAIL] expected person {persona} rank 1, got {top['person_id']}")
        return 1

    if not scanned:
        print("[FAIL] corpus appears empty (no face_records to search)")
        return 1

    try:
        import sqlite3

        c = sqlite3.connect(DB_PATH)
        n = c.execute("SELECT COUNT(*) FROM face_records").fetchone()[0]
        print(f"[ OK ] DB corpus: {n} face records indexed")
    except Exception as e:  # noqa: BLE001
        print(f"[warn] db corpus check skipped: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
