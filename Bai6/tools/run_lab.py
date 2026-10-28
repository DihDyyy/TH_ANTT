"""Execute the lab commands locally and retain evidence; this is not GitLab Runner."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "lab06-devsecops"
EVIDENCE = ROOT / "evidence"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
NODE = Path(r"C:\Program Files\nodejs\node.exe")
NPM = Path(r"C:\Program Files\nodejs\npm.cmd")
STUDENT = {"name": "Lê Đình Duy", "student_id": "2387700102", "class": "23DATA1"}


def stamp() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="milliseconds")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def execute_job(pipeline_name: str, name: str, stage: str, commands: list[str]) -> dict:
    script_path = EVIDENCE / "job-scripts" / f"{pipeline_name}-{name}.sh"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    # Commands are read from the supplied lab YAML files, not generated outputs.
    script_path.write_text("set -e\nset -x\n" + "\n".join(commands) + "\n", encoding="utf-8", newline="\n")
    if pipeline_name == "docusaurus" and name == "pages" and (PROJECT / "public").exists():
        shutil.rmtree(PROJECT / "public")
    env = os.environ.copy()
    env.update({
        "GITLAB_USER_LOGIN": "local-2387700102",
        "CI_COMMIT_BRANCH": "main",
        "CI_DEFAULT_BRANCH": "main",
        "STUDENT_NAME": STUDENT["name"],
        "STUDENT_ID": STUDENT["student_id"],
        "STUDENT_CLASS": STUDENT["class"],
        "npm_config_update_notifier": "false",
        "NO_COLOR": "1",
    })
    started_at = stamp()
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [str(BASH), "--noprofile", "--norc", script_path.as_posix()],
            cwd=PROJECT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
            timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output, exit_code = result.stdout, result.returncode
    except subprocess.TimeoutExpired as error:
        raw = error.stdout or b""
        output = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
        output += "\nLOCAL EXECUTION TIMEOUT (90 seconds).\n"
        exit_code = 124
    ended_at = stamp()
    job = {
        "name": name,
        "stage": stage,
        "mode": "local-bash-not-gitlab-runner",
        "commands": commands,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "exit_code": exit_code,
        "status": "passed" if exit_code == 0 else "failed",
        "output": output,
    }
    log = (
        "MODE: LOCAL BASH EXECUTION. NOT A REMOTE GITHUB ACTIONS OR GITLAB CI RUN.\n"
        f"STUDENT: {STUDENT['name']} | {STUDENT['student_id']} | {STUDENT['class']}\n"
        f"PIPELINE: {pipeline_name}\nJOB: {name}\nSTAGE: {stage}\n"
        f"START: {started_at}\nEND: {ended_at}\n"
        f"EXIT CODE: {exit_code}\nDURATION: {job['duration_seconds']} s\n"
        "GITLAB_USER_LOGIN=local-2387700102 (local test value)\n"
        "CI_COMMIT_BRANCH=main (local test value)\n\n"
        + output
    )
    (EVIDENCE / f"{pipeline_name}-{name}.log").write_text(log, encoding="utf-8")
    print(f"{pipeline_name}/{name}: {job['status']} ({job['duration_seconds']} s)", flush=True)
    if pipeline_name == "docusaurus" and name == "pages" and (PROJECT / "public").is_dir() and not (PROJECT / "build").exists():
        shutil.copytree(PROJECT / "public", PROJECT / "build")
    return job


def execute_pipeline(name: str, source: Path) -> dict:
    config = yaml.safe_load(source.read_text(encoding="utf-8"))
    stages = config.get("stages", ["build", "test", "deploy"])
    jobs = [(key, value) for key, value in config.items() if isinstance(value, dict) and "script" in value]
    started_at = stamp()
    start = time.perf_counter()
    results = []
    blocked = False
    for stage in stages:
        current = [(key, value) for key, value in jobs if value.get("stage", "test") == stage]
        if blocked:
            results.extend({
                "name": key,
                "stage": stage,
                "status": "skipped",
                "reason": "An earlier stage failed; deployment was not executed.",
                "commands": value["script"],
            } for key, value in current)
            continue
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(current))) as pool:
            futures = [pool.submit(execute_job, name, key, stage, value["script"]) for key, value in current]
            stage_results = [future.result() for future in futures]
        results.extend(stage_results)
        blocked = any(job["exit_code"] != 0 for job in stage_results)
    result = {
        "name": name,
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "mode": "local-bash-not-gitlab-runner",
        "limitations": "No runner registration, container images, remote artifacts or GitLab Pages deployment are performed locally.",
        "started_at": started_at,
        "ended_at": stamp(),
        "duration_seconds": round(time.perf_counter() - start, 3),
        "stages": stages,
        "status": "failed" if blocked else "passed",
        "jobs": results,
    }
    write_json(EVIDENCE / f"{name}.json", result)
    return result


def environment() -> dict:
    commands = {
        "node": [str(NODE), "--version"],
        "npm": [str(NPM), "--version"],
        "git": [r"C:\Program Files\Git\cmd\git.exe", "--version"],
    }
    versions = {"python": platform.python_version()}
    for key, command in commands.items():
        result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        versions[key] = result.stdout.strip()
    data = {
        "captured_at": stamp(),
        "student": STUDENT,
        "os": platform.platform(),
        "workspace": str(ROOT),
        "versions": versions,
        "gitlab_project_url": None,
        "gitlab_pipeline_id": None,
        "gitlab_pages_url": None,
        "note": "Student details were read from LeDinhDuy2387700102.docx. Remote GitLab access has not been established.",
    }
    write_json(EVIDENCE / "environment.json", data)
    return data


def validate_configuration() -> dict:
    checks = []
    for relative in [".gitlab-ci.yml", "examples/gitlab-ci-basic.yml", "examples/gitlab-ci-initial.yml", "examples/gitlab-ci-build-only.yml"]:
        data = yaml.safe_load((PROJECT / relative).read_text(encoding="utf-8"))
        job_names = [key for key, value in data.items() if isinstance(value, dict) and "script" in value]
        for name in job_names:
            script = data[name]["script"]
            if not isinstance(script, list) or not all(isinstance(command, str) for command in script):
                raise ValueError(f"Invalid script array: {relative}/{name}")
        checks.append({"file": relative, "status": "parsed", "jobs": job_names})
    probes = []
    for url in ["https://example.invalid/lab06-devsecops/", "https://sample.gitlab.io/lab06-devsecops/", "https://sample-123.gitlab.io/"]:
        env = os.environ.copy()
        env["CI_PAGES_URL"] = url
        result = subprocess.run(
            [str(NODE), "-e", "const c=require('./docusaurus.config.js');console.log(JSON.stringify({url:c.url,baseUrl:c.baseUrl,title:c.title}));"],
            cwd=PROJECT, env=env, capture_output=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        probes.append({"input_url": url, "result": json.loads(result.stdout)})
    result = {
        "captured_at": stamp(),
        "status": "passed",
        "scope": "Local YAML parsing and Node configuration evaluation; not GitLab CI Lint or a Docusaurus build.",
        "yaml": checks,
        "url_probes": probes,
    }
    write_json(EVIDENCE / "configuration-validation.json", result)
    return result


def main() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    metadata = environment()
    validation = validate_configuration()
    initial = execute_pipeline("initial", PROJECT / "examples/gitlab-ci-initial.yml")
    basic = execute_pipeline("basic", PROJECT / "examples/gitlab-ci-basic.yml")
    complex_pipeline = execute_pipeline("docusaurus", PROJECT / ".gitlab-ci.yml")
    summary = {"environment": metadata, "configuration": validation, "pipelines": [initial, basic, complex_pipeline]}
    write_json(EVIDENCE / "summary.json", summary)
    print("Evidence saved to " + str(EVIDENCE), flush=True)


if __name__ == "__main__":
    main()
