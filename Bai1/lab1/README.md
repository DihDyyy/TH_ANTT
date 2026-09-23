# Lab 1 - Secure Validator

## Mục tiêu

Lab này kiểm tra các chức năng bảo vệ đầu vào của ứng dụng Flask:
- validate email
- validate URL và chặn SSRF cơ bản
- validate tên file và chặn path traversal
- sanitize SQL input
- escape HTML input để chống XSS

## Cấu trúc thư mục

- app.py: ứng dụng Flask
- securevalidator/core.py: các hàm validation
- templates/index.html: giao diện web
- tests/test_validators.py: bộ test tự động

## Bước 1: cài đặt phụ thuộc

Mở PowerShell trong thư mục lab:

```powershell
cd E:\Bai1\Lab1\secure-validator-lab
python -m pip install -r requirements.txt
```

## Bước 2: chạy test tự động

### Chạy toàn bộ test

```powershell
python -m pytest -q
```

### Chạy test chi tiết hơn

```powershell
python -m pytest -vv
```

### Chạy bằng unittest

```powershell
python -m unittest tests/test_validators.py -v
```

## Bước 3: chạy ứng dụng

```powershell
python app.py
```

Mở trình duyệt tại:

```text
http://localhost:5000
```

Nhập các dữ liệu mẫu:
- Email: `user@example.com`
- URL: `https://github.com`
- Filename: `report.pdf`
- SQL: `SELECT * FROM users WHERE id = 1`
- HTML: `<b>hello</b>`

## Bước 4: test API trực tiếp

Mở PowerShell khác rồi chạy:

```powershell
curl -X POST http://localhost:5000/validate -H "Content-Type: application/json" -d "{\"email\":\"user@example.com\",\"url\":\"https://example.com\",\"filename\":\"report.pdf\",\"sql\":\"SELECT * FROM users\",\"html\":\"<script>alert(1)</script>\"}"
```

Kết quả mong đợi:
- email: `True`
- url: `True`
- filename: `True`
- sql: chuỗi đã được lọc
- html: đã escape HTML

## Bước 5: kiểm tra debug nhanh

Nếu muốn kiểm tra từng hàm riêng lẻ trong Python:

```powershell
python
from securevalidator.core import validate_email, validate_url
print(validate_email("user@example.com"))
print(validate_url("https://github.com"))
```

## Kết luận

Nếu tất cả test đều pass, bạn đã hoàn thành lab về input validation và bảo mật web app cơ bản.
