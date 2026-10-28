"""Take browser screenshots of pages showing the real local execution records."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import subprocess
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "report-assets"
EVIDENCE = ROOT / "evidence"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

CSS = """
*{box-sizing:border-box}body{margin:0;background:#f3f5f8;color:#182536;font:18px 'Segoe UI',sans-serif}
header{background:#143e3b;color:white;padding:30px 48px}header h1{margin:8px 0;font-size:32px}
header p{margin:6px 0}.tag{display:inline-block;background:#e6b85b;color:#292410;padding:6px 12px;border-radius:5px;font-weight:700;font-size:14px;letter-spacing:.03em}
main{padding:24px 48px}h2{margin:0 0 16px;font-size:24px}.card{padding:22px 24px;background:white;border:1px solid #d9e1e8;border-radius:10px;margin-bottom:18px}
table{width:100%;border-collapse:collapse;font-size:17px}th,td{padding:12px 14px;text-align:left;border-bottom:1px solid #e2e7ed}th{background:#f4f7fa}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#172431;color:#e7edf5;padding:20px;border-radius:7px;line-height:1.5;font:16px Consolas,'Courier New',monospace;margin:8px 0}
.passed{color:#176247;font-weight:700}.failed{color:#ae2431;font-weight:700}.skipped{color:#7c6143;font-weight:700}
.notice{border-left:5px solid #d7a43e;background:#fff9e9;padding:14px 18px;font-size:17px;line-height:1.5}
.muted{color:#5c6b7b;font-size:15px}.flow{display:flex;gap:16px}.stage{flex:1;background:#edf4f1;padding:18px;border-radius:8px}.stage h3{margin-top:0}.job{background:white;padding:12px;margin-top:12px;border:1px solid #d8e3dd;border-radius:6px}
footer{padding:12px 48px 24px;color:#5c6b7b;font-size:14px}
"""


def esc(text: object) -> str:
    return html.escape(str(text))


def page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="vi"><meta charset="utf-8"><title>{esc(title)}</title>
<style>{CSS}</style><header><span class="tag">MINH CHỨNG CỤC BỘ · CHƯA CHẠY TRÊN CI ĐÁM MÂY</span>
<h1>{esc(title)}</h1><p>Lê Đình Duy · MSSV 2387700102 · Lớp 23DATA1</p></header>
<main>{body}</main><footer>Nguồn: tệp JSON / log thực thi trong thư mục evidence. Ảnh chụp bằng Microsoft Edge headless từ trang xem minh chứng cục bộ.</footer></html>"""


def job_rows(pipeline: dict) -> str:
    rows = "".join(
        f"<tr><td>{esc(job['name'])}</td><td>{esc(job['stage'])}</td><td class='{job['status']}'>{job['status'].upper()}</td>"
        f"<td>{esc(job.get('duration_seconds', '—'))}</td><td>{esc(job.get('exit_code', '—'))}</td></tr>"
        for job in pipeline["jobs"]
    )
    return "<table><tr><th>Job</th><th>Stage</th><th>Kết quả tại máy</th><th>Thời gian (giây)</th><th>Exit code</th></tr>" + rows + "</table>"


def screenshot(name: str, title: str, body: str, height: int = 1080) -> dict:
    path = ASSETS / f"{name}.html"
    output = ASSETS / f"{name}.png"
    path.write_text(page(title, body), encoding="utf-8")
    profile = Path(tempfile.mkdtemp(prefix="lab06-edge-"))
    args = [
        str(EDGE), "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-software-rasterizer", "--disable-extensions", "--no-first-run",
        "--hide-scrollbars", "--force-device-scale-factor=1", "--user-data-dir=" + str(profile),
        f"--window-size=1440,{height}", "--screenshot=" + str(output), path.as_uri(),
    ]
    result = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace", timeout=40, creationflags=subprocess.CREATE_NO_WINDOW)
    (EVIDENCE / f"capture-{name}.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"Screenshot failed: {name}\n{result.stderr[-1500:]}")
    print(str(output), flush=True)
    return {"file": output.relative_to(ROOT).as_posix(), "source_html": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "method": "Microsoft Edge headless screenshot of local evidence viewer"}


def screenshot_url(name: str, url: str, height: int = 1080) -> dict:
    output = ASSETS / f"{name}.png"
    profile = Path(tempfile.mkdtemp(prefix="lab06-edge-"))
    args = [
        str(EDGE), "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-software-rasterizer", "--disable-extensions", "--no-first-run",
        "--hide-scrollbars", "--force-device-scale-factor=1", "--user-data-dir=" + str(profile),
        f"--window-size=1440,{height}", "--screenshot=" + str(output), url,
    ]
    result = subprocess.run(args, capture_output=True, encoding="utf-8", errors="replace", timeout=40, creationflags=subprocess.CREATE_NO_WINDOW)
    (EVIDENCE / f"capture-{name}.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(f"Screenshot failed: {name}\n{result.stderr[-1500:]}")
    print(str(output), flush=True)
    return {"file": output.relative_to(ROOT).as_posix(), "source_html": url, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "method": "Microsoft Edge headless screenshot of local running Docusaurus"}


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    summary = json.loads((EVIDENCE / "summary.json").read_text(encoding="utf-8"))
    env = summary["environment"]
    initial, basic, complex_pipeline = summary["pipelines"]
    images = []
    env_rows = "".join(f"<tr><td>{esc(key)}</td><td>{esc(value)}</td></tr>" for key, value in env["versions"].items())
    images.append(screenshot("01-moi-truong", "Môi trường và thông tin sinh viên", f"""
<section class="card"><h2>Thông tin từ file Word</h2><table><tr><th>Họ tên</th><th>MSSV</th><th>Lớp</th></tr>
<tr><td>Lê Đình Duy</td><td>2387700102</td><td>23DATA1</td></tr></table><p class="muted">Nguồn: LeDinhDuy2387700102.docx</p></section>
<section class="card"><h2>Phiên bản đã kiểm tra bằng lệnh</h2><table>{env_rows}</table><p>{esc(env['os'])}</p><p class="muted">Ghi nhận: {esc(env['captured_at'])}</p></section>
<div class="notice">Chưa có dự án, pipeline ID hoặc URL GitLab Pages được xác minh. Các lần chạy dưới đây thực thi bằng Bash trên máy cục bộ.</div>""", 1000))

    initial_job = initial["jobs"][0]
    images.append(screenshot("02-job-dau-tien", "Job đầu tiên: echo và date", f"""
<section class="card"><h2>Kết quả thực thi</h2>{job_rows(initial)}
<p class="muted">Bắt đầu: {esc(initial_job['started_at'])} · Kết thúc: {esc(initial_job['ended_at'])}</p>
<pre>{esc(initial_job['output'])}</pre></section>
<div class="notice">Đã chạy các lệnh trong examples/gitlab-ci-initial.yml tại máy. Kết quả này chưa xác nhận GitLab Runner hoạt động.</div>""", 900))

    stages = ""
    for stage in basic["stages"]:
        jobs = "".join(f"<div class='job'><strong>{esc(job['name'])}</strong><p class='passed'>{job['status'].upper()} · {job['duration_seconds']} s</p></div>" for job in basic["jobs"] if job["stage"] == stage)
        stages += f"<div class='stage'><h3>{esc(stage)}</h3>{jobs}</div>"
    images.append(screenshot("03-pipeline-co-ban", "Pipeline mẫu: build → test → deploy", f"""
<section class="card"><h2>Thứ tự stage của lần chạy cục bộ</h2><div class="flow">{stages}</div></section>
<section class="card">{job_rows(basic)}<p class="muted">Tổng thời gian: {basic['duration_seconds']} giây · {esc(basic['started_at'])}</p></section>
<div class="notice">Hai job test được khởi chạy song song. test-job2 giữ nguyên sleep 20 theo đề. deploy-prod chỉ in thông báo mô phỏng theo mã mẫu.</div>""", 1150))

    logs = "".join(f"<section class='card'><h2>{esc(job['name'])}</h2><p class='muted'>{esc(job['started_at'])} → {esc(job['ended_at'])} · exit {job['exit_code']}</p><pre>{esc(job['output'])}</pre></section>" for job in basic["jobs"])
    images.append(screenshot("04-log-cac-job", "Log thật của bốn job mẫu", logs, 1450))

    config = (ROOT / "lab06-devsecops" / ".gitlab-ci.yml").read_text(encoding="utf-8")
    images.append(screenshot("05-cau-hinh-docusaurus", "Cấu hình build Docusaurus và GitLab Pages", f"""
<section class="card"><p class="muted">Tệp: lab06-devsecops/.gitlab-ci.yml</p><pre>{esc(config)}</pre></section>
<div class="notice">YAML đã được phân tích cú pháp tại máy. Chưa chạy GitLab CI Lint. Khai báo pages.publish phục vụ GitLab hiện hành; chưa xác nhận triển khai thành công.</div>""", 1150))

    build_job = complex_pipeline["jobs"][0]
    pages_job = complex_pipeline["jobs"][1] if len(complex_pipeline["jobs"]) > 1 else None
    pages_log = f"<section class='card'><h2>Log của job pages</h2><pre>{esc(pages_job['output'])}</pre></section>" if pages_job else ""
    images.append(screenshot("06-build-thanh-cong", "Kết quả build Docusaurus và job pages thành công", f"""
<section class="card">{job_rows(complex_pipeline)}<p class="muted">{esc(build_job['started_at'])} · {esc(complex_pipeline['duration_seconds'])} giây</p></section>
<section class="card"><h2>Log của build-job</h2><pre>{esc(build_job['output'])}</pre></section>
{pages_log}
<div class="notice">Job build hoàn thành cài dependencies và build Docusaurus thành công (exit code 0). Job pages chuyển thư mục build/ sang public/ để sẵn sàng xuất bản.</div>""", 1350))

    validation = summary["configuration"]
    validation_rows = "".join(f"<tr><td>{esc(item['file'])}</td><td>{esc(', '.join(item['jobs']))}</td><td>Đã đọc YAML</td></tr>" for item in validation["yaml"])
    url_rows = "".join(f"<tr><td>{esc(item['input_url'])}</td><td>{esc(item['result']['url'])}</td><td>{esc(item['result']['baseUrl'])}</td></tr>" for item in validation["url_probes"])
    images.append(screenshot("07-kiem-tra-cau-hinh", "Kiểm tra cấu hình cục bộ", f"""
<section class="card"><h2>Bốn cấu hình YAML</h2><table><tr><th>Tệp</th><th>Jobs</th><th>Kết quả</th></tr>{validation_rows}</table></section>
<section class="card"><h2>Thử cách tách url và baseUrl bằng Node.js</h2><table><tr><th>URL đầu vào thử nghiệm</th><th>url</th><th>baseUrl</th></tr>{url_rows}</table></section>
<div class="notice">Các tên miền sample và example.invalid là dữ liệu kiểm tra cấu hình, không phải URL đã triển khai. Kiểm tra này không thay thế build Docusaurus hoặc CI Lint.</div>""", 1060))
    github_path = EVIDENCE / "github-basic.json"
    if github_path.is_file():
        github = json.loads(github_path.read_text(encoding="utf-8"))
        output = "".join(f"<h3>{esc(job['name'])}</h3><pre>{esc(job['output'])}</pre>" for job in github["jobs"])
        images.append(screenshot("08-github-workflow-co-ban", "Chạy cục bộ lệnh trong workflow GitHub Actions", f"""
<section class="card"><h2>{esc(github['workflow_name'])}</h2>{job_rows(github)}
<p class="muted">Nguồn: github-workflows/bai6-basic.yml · Tổng: {github['duration_seconds']} giây</p></section>
<section class="card">{output}</section>
<div class="notice">Đã chạy các bước run và thứ tự needs bằng Bash cục bộ. Chưa dispatch workflow trên GitHub; chưa có Actions run ID.</div>""", 1640))
        workflow = (ROOT / "github-workflows" / "bai6-pages.yml").read_text(encoding="utf-8")
        images.append(screenshot("09-github-pages-workflow", "Workflow build và triển khai GitHub Pages", f"""
<section class="card"><p class="muted">Repo đích: DihDyyy/TH_ANTT · Vị trí: .github/workflows/bai6-pages.yml</p>
<pre style="font-size:14px;line-height:1.35">{esc(workflow)}</pre></section>
<div class="notice">Workflow đã được chuẩn bị và đọc YAML tại máy. Cần bật Pages với Source = GitHub Actions và chạy workflow trên GitHub để xác minh build, artifacts và deployment.</div>""", 1890))
    
    # Real live screenshots of the running Docusaurus website
    images.append(screenshot_url("10-docusaurus-trang-chu", "http://localhost:3000/lab06-devsecops/", 960))
    images.append(screenshot_url("11-docusaurus-tai-lieu", "http://localhost:3000/lab06-devsecops/docs/lab06/", 1100))
    (EVIDENCE / "screenshot-manifest.json").write_text(json.dumps(images, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
