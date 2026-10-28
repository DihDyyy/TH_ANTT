# Bài 6 — Bảo mật với DevSecOps

**Lê Đình Duy — 2387700102 — 23DATA1**

Dự án Docusaurus phục vụ mục 6.2.2 của `lab-06.pdf`. Các cấu hình giai đoạn
trước nằm trong `examples/`. Báo cáo chính và minh chứng nằm ở thư mục cha.

Theo lựa chọn của sinh viên, nền tảng đích là GitHub Actions trên
`DihDyyy/TH_ANTT`. Các cấu hình GitLab được giữ để đối chiếu với tài liệu.

## Chạy trên GitHub Actions

Hai workflow trong `../github-workflows/` cần nằm ở
`.github/workflows/` tại **gốc repo TH_ANTT**. Dự án này nằm tại
`Bai6/lab06-devsecops/` trong repo.

1. Đưa hai workflow và thư mục `Bai6/` lên repo.
2. Mở Settings > Pages > Build and deployment > Source, chọn GitHub Actions.
3. Trên nhánh `main`, chạy `Bai 6 - Pipeline co ban` và
   `Bai 6 - Docusaurus va GitHub Pages` từ thẻ Actions.
4. Kiểm tra bốn job mẫu, log build, artifact `github-pages` và job deploy.
5. Mở URL do job deploy xuất ra để chụp website thực tế.

`bai6-basic.yml` chỉ mô phỏng deploy bằng echo, đúng ví dụ đầu của đề.
`bai6-pages.yml` thực hiện build và triển khai website thật khi chạy thành công.
Chưa có run ID hoặc URL Pages được xác minh trong môi trường hiện tại.

## Chạy trên máy có kết nối npm

```powershell
cd E:\Bai6\lab06-devsecops
npm.cmd install
npm.cmd run build
npm.cmd run serve -- --host 127.0.0.1
```

Khi chưa có `CI_PAGES_URL` hoặc `SITE_URL`, cấu hình dùng tên miền giữ chỗ
`https://example.invalid/lab06-devsecops/`. Đây không phải địa chỉ đã triển khai.
Để xem cục bộ tại đường dẫn gốc, trước khi build có thể đặt:

```powershell
$env:SITE_URL = 'http://localhost:3000/'
npm.cmd run build
npm.cmd run serve -- --host 127.0.0.1
```

## Chạy trên GitLab

1. Tạo dự án dưới tài khoản cá nhân và bảo đảm có runner hoạt động.
2. Đưa **nội dung thư mục này** vào gốc kho GitLab.
3. Để thực hiện 6.2.1, dùng nội dung `examples/gitlab-ci-basic.yml` làm `.gitlab-ci.yml`,
   commit và kiểm tra bốn job.
4. Với 6.2.2, lần lượt dùng cấu hình `gitlab-ci-initial.yml`,
   `gitlab-ci-build-only.yml`, rồi khôi phục `.gitlab-ci.yml` đầy đủ.
5. Commit lên nhánh mặc định. Job `build-job` lưu `build/`; `pages` nhận artifacts
   và xuất bản `public/`. Cấu hình website tự đọc `CI_PAGES_URL` từ GitLab.
6. Kiểm tra Build > Pipelines, log, Browse artifacts và Deploy > Pages. Chụp ảnh
   các kết quả thực tế và bổ sung báo cáo. Không đưa token hoặc mật khẩu vào repo.

Khi có thể tải dependencies, nên commit thêm `package-lock.json` và chuyển
`npm install` sang `npm ci` để tăng tính lặp lại. Hiện chưa tạo lockfile vì lần
cài đặt trong môi trường thực thi bị chặn; không có lockfile giả.

## Ranh giới minh chứng

Script `../tools/run_lab.py` chạy lệnh YAML bằng Bash cục bộ để thu log, có
thực thi song song trong cùng stage và dừng stage sau khi gặp lỗi. Script này
không thay thế GitLab Runner, không chạy image Docker, không tải artifacts
từ GitLab và không tự triển khai GitLab Pages.
