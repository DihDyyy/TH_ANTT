"""Check report links, image hashes and the recorded execution order."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import struct


ROOT = Path(__file__).resolve().parents[1]
report = ROOT / "REPORT_Bai6_LeDinhDuy_2387700102.md"
content = report.read_text(encoding="utf-8")
assert all(value in content for value in ["Lê Đình Duy", "2387700102", "23DATA1"])

local_links = []
for destination in re.findall(r"\]\(([^)]+)\)", content):
    if not destination.startswith(("https://", "http://", "#")):
        path = ROOT / destination
        assert path.is_file(), f"Broken report link: {destination}"
        local_links.append(destination)

manifest = json.loads((ROOT / "evidence" / "screenshot-manifest.json").read_text(encoding="utf-8"))
assert len(manifest) == 11
images = []
for item in manifest:
    path = ROOT / item["file"]
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}"
    width, height = struct.unpack(">II", raw[16:24])
    assert width == 1440 and height >= 400
    assert hashlib.sha256(raw).hexdigest() == item["sha256"]
    assert item["file"] in local_links
    images.append({"file": item["file"], "width": width, "height": height})

for name in ["basic", "github-basic"]:
    data = json.loads((ROOT / "evidence" / f"{name}.json").read_text(encoding="utf-8"))
    assert data["status"] == "passed"
    jobs = {job["name"]: job for job in data["jobs"]}
    assert len(jobs) == 4 and all(job["exit_code"] == 0 for job in jobs.values())
    assert jobs["test-job2"]["duration_seconds"] >= 20
    assert datetime.fromisoformat(jobs["test-job1"]["started_at"]) >= datetime.fromisoformat(jobs["build-job"]["ended_at"])
    assert datetime.fromisoformat(jobs["test-job2"]["started_at"]) < datetime.fromisoformat(jobs["test-job1"]["ended_at"])
    assert datetime.fromisoformat(jobs["deploy-prod"]["started_at"]) >= max(datetime.fromisoformat(jobs[job]["ended_at"]) for job in ["test-job1", "test-job2"])
    assert hashlib.sha256((ROOT / data["source"]).read_bytes()).hexdigest() == data["source_sha256"]

build = json.loads((ROOT / "evidence" / "docusaurus.json").read_text(encoding="utf-8"))
assert build["status"] == "passed"
assert build["jobs"][0]["exit_code"] == 0
assert build["jobs"][1]["exit_code"] == 0
assert (ROOT / "lab06-devsecops" / "build" / "index.html").exists()
assert (ROOT / "lab06-devsecops" / "public" / "index.html").exists()

result = {
    "status": "passed",
    "report": report.name,
    "local_link_count": len(local_links),
    "image_count": len(images),
    "images": images,
    "execution_assertions": "Basic configurations passed locally, slept at least 20 seconds, ran tests concurrently and waited before deploy; Docusaurus build, artifact generation, and local website serve succeeded.",
    "remote_verification": "Not performed: no GitHub Actions run ID or verified Pages URL.",
}
(ROOT / "evidence" / "artifact-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
