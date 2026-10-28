"""Run the basic GitHub workflow's shell steps locally, following its needs DAG."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
from pathlib import Path
import time

import yaml

from run_lab import EVIDENCE, ROOT, execute_job, stamp, write_json


def main() -> None:
    source = ROOT / "github-workflows" / "bai6-basic.yml"
    config = yaml.load(source.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    definitions = config["jobs"]
    done = {}
    order = []
    started_at = stamp()
    started = time.perf_counter()
    pending = list(definitions)
    while pending:
        ready = []
        for name in pending:
            needs = definitions[name].get("needs", [])
            needs = [needs] if isinstance(needs, str) else needs
            if all(dependency in done for dependency in needs):
                ready.append((name, needs))
        if not ready:
            raise ValueError("Unresolved GitHub job dependencies")
        wave = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(ready)) as pool:
            futures = []
            for name, needs in ready:
                if any(done[dependency]["status"] != "passed" for dependency in needs):
                    done[name] = {"name": name, "status": "skipped", "needs": needs}
                    continue
                commands = [step["run"] for step in definitions[name]["steps"] if "run" in step]
                stage = "build" if name == "build-job" else "deploy" if name == "deploy-prod" else "test"
                futures.append((name, needs, pool.submit(execute_job, "github-basic", name, stage, commands)))
            for name, needs, future in futures:
                job = future.result()
                job["needs"] = needs
                done[name] = job
                wave.append(name)
        order.append(wave)
        pending = [name for name in pending if name not in done]
    results = [done[name] for name in definitions]
    data = {
        "name": "github-basic",
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "mode": "local-shell-execution-not-github-actions",
        "workflow_name": config["name"],
        "started_at": started_at,
        "ended_at": stamp(),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "status": "passed" if all(job["status"] == "passed" for job in results) else "failed",
        "dependency_waves": order,
        "jobs": results,
        "remote_run_id": None,
    }
    write_json(EVIDENCE / "github-basic.json", data)
    validation = []
    for name in ["bai6-basic.yml", "bai6-pages.yml"]:
        workflow = yaml.load((ROOT / "github-workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if "on" not in workflow or "workflow_dispatch" not in workflow["on"]:
            raise ValueError(f"Missing dispatch trigger: {name}")
        for job_name, job in workflow["jobs"].items():
            needs = job.get("needs", [])
            needs = [needs] if isinstance(needs, str) else needs
            if not all(dependency in workflow["jobs"] for dependency in needs):
                raise ValueError(f"Invalid dependency: {name}/{job_name}")
        validation.append({"file": name, "jobs": list(workflow["jobs"]), "status": "parsed locally"})
    write_json(EVIDENCE / "github-workflow-validation.json", validation)
    print("Local GitHub workflow commands completed. No remote Actions run was dispatched.", flush=True)


if __name__ == "__main__":
    main()
