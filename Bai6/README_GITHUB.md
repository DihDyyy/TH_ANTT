# Chạy Bài 6 trên repo TH_ANTT

Sinh viên: **Lê Đình Duy — 2387700102 — 23DATA1**.

Bản báo cáo chính là `REPORT_Bai6_LeDinhDuy_2387700102.md`.
Giữ nguyên `report-assets/` bên cạnh tệp Markdown để ảnh hiển thị đúng.

## Bố trí trong repo

```text
TH_ANTT/
├── .github/workflows/
│   ├── bai6-basic.yml
│   └── bai6-pages.yml
└── Bai6/
    ├── REPORT_Bai6_LeDinhDuy_2387700102.md
    ├── report-assets/
    ├── evidence/
    ├── github-workflows/       # Bản đối chiếu dùng để chạy cục bộ
    ├── lab06-devsecops/        # Dự án Docusaurus và cấu hình GitLab theo đề
    └── tools/
```

Hai workflow phải ở gốc repo, không phải trong `Bai6/.github/`.

## Chạy trên GitHub

1. Đưa các thay đổi lên repo `https://github.com/DihDyyy/TH_ANTT`.
2. Chọn Settings > Pages > Build and deployment > Source > GitHub Actions.
3. Trên nhánh `main`, vào Actions và chạy lần lượt hai workflow:
   `Bai 6 - Pipeline co ban`, `Bai 6 - Docusaurus va GitHub Pages`.
4. Kiểm tra bốn job của workflow cơ bản. Ở workflow website, kiểm tra job
   build, artifact `github-pages` và job deploy.
5. Mở URL do bước `actions/deploy-pages` xuất ra. URL này mới là bằng chứng
   địa chỉ website đã triển khai; không xem một URL dự đoán là kết quả thành công.

Chưa có run ID hoặc URL Pages được xác minh ở lần thực hiện hiện tại.
Việc chọn GitHub Actions thay cho GitLab đã được sinh viên xác nhận.

## Tái hiện minh chứng cục bộ

Trên Windows có Python, PyYAML, Git Bash, Node.js và Microsoft Edge:

```powershell
python -m pip install -r requirements.txt
python -X utf8 tools\run_lab.py
python -X utf8 tools\run_github_basic.py
python -X utf8 tools\capture_evidence.py
```

Các script lưu stdout, stderr, exit code, thời gian, SHA-256 và ảnh chụp trang
xem log. Đây là thực thi lệnh tại máy; không phải GitHub-hosted runner.
Script `run_lab.py` có thử tải npm nên cần mạng để build Docusaurus.

## Mức độ hoàn thành

Toàn bộ các lệnh pipeline và dự án Docusaurus đã chạy thành công trên máy cục bộ.
Dependencies đã được cài đặt hoàn tất, website đã build tĩnh thành công và được
khởi chạy thực tế trên cổng 3000 để kiểm tra giao diện. Hai workflow GitHub Actions
đã được chuẩn bị sẵn sàng để đưa lên repo `TH_ANTT` phục vụ kiểm tra và triển khai
lên GitHub Pages.
