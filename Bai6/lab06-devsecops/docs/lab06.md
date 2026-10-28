---
id: lab06
title: Bài 6 — Bảo mật với DevSecOps
sidebar_position: 1
---

## Thông tin sinh viên

| Nội dung | Thông tin |
| --- | --- |
| Họ và tên | Lê Đình Duy |
| MSSV | 2387700102 |
| Lớp | 23DATA1 |

## 6.1. Tích hợp bảo mật trong CI/CD

Pipeline cần phân quyền theo nguyên tắc ít quyền nhất, bảo vệ secrets,
kiểm tra tính toàn vẹn, tích hợp security gates, ghi nhật ký và cô lập runner.
SAST kiểm tra mã nguồn; DAST kiểm tra ứng dụng đang chạy; SCA kiểm tra
thành phần bên thứ ba. Cấu hình IaC cũng cần được kiểm tra trước khi triển khai.

## 6.2.1. Pipeline cơ bản

Pipeline mẫu có ba stage `build`, `test`, `deploy`. Hai job kiểm thử ở cùng
stage có thể chạy song song. `test-job2` thực hiện `sleep 20` theo bài hướng dẫn.
Job `deploy-prod` trong ví dụ chỉ in thông báo mô phỏng triển khai.

## 6.2.2. Build và triển khai Docusaurus

Job `build-job` chạy `npm install`, sau đó `npm run build` và lưu `build/`
làm artifacts. Job `pages` nhận artifacts, chuyển `build/` thành `public/`,
rồi khai báo thư mục xuất bản cho GitLab Pages.

URL của website được lấy từ biến `CI_PAGES_URL` khi chạy trên GitLab.
Các kết quả đã thực hiện và các giới hạn của môi trường được ghi trong
báo cáo Markdown đi kèm; mã nguồn này không tự xác nhận trạng thái triển khai.
