# Lab 3 - Secure Logger

## Mục tiêu

Lab này kiểm tra hệ thống logging an toàn, bao gồm:
- che giấu dữ liệu nhạy cảm như email, token, API key, password
- ghi log theo định dạng JSON
- xoay log khi lớn quá kích thước
- tạo chữ ký hash cho từng dòng log

## Cấu trúc thư mục

- app.py: Flask API validate dữ liệu đầu vào
- securelogger/logger.py: logger an toàn
- securevalidator/core.py: validation sanitize đầu vào
- secure.log: file log sinh ra khi chạy ứng dụng
- secure.log.sig: file hash chữ ký của từng dòng log
- tests/test_secure_lab.py: bộ test tự động

## Bước 1: cài đặt phụ thuộc

Mở PowerShell trong thư mục lab:

```powershell
cd E:\Bai1\Lab3\secure_logger_lab
python -m pip install -r requirements.txt
```

## Bước 2: chạy test tự động

### Chạy toàn bộ test

```powershell
python -m pytest -q
```

### Chạy test chi tiết

```powershell
python -m pytest -vv
```

### Kiểm tra syntax nhanh

```powershell
python -m py_compile app.py
```

## Bước 3: chạy ứng dụng

```powershell
python app.py
```

Mở trình duyệt hoặc dùng curl để gọi API:

```text
http://localhost:5000
```

## Bước 4: test API validate

Dùng curl:

```powershell
curl -X POST http://localhost:5000/validate -H "Content-Type: application/json" -d "{\"email\":\"student@example.com\",\"url\":\"https://example.com\",\"filename\":\"report.pdf\",\"sql\":\"SELECT * FROM users WHERE email='student@example.com'\",\"html\":\"<script>alert(1)</script>\"}"
```

Kết quả mong đợi:
- email hợp lệ
- URL hợp lệ
- filename hợp lệ
- SQL được sanitize
- HTML được escape

## Bước 5: kiểm tra log đã che giấu PII

Sau khi request được gửi, mở file log:

```powershell
notepad secure.log
```

Bạn sẽ thấy các dữ liệu nhạy cảm như:
- email
- token
- password
- api key

đã được thay bằng dạng:

```text
<email_masked>
<token_masked>
```

## Bước 6: kiểm tra chữ ký log

Mở file:

```powershell
notepad secure.log.sig
```

Mỗi dòng trong file này là hash SHA-256 của một dòng log tương ứng.

## Bước 7: kiểm tra bằng Python trực tiếp

```powershell
python
from securelogger.logger import get_secure_logger, mask_pii
print(mask_pii("Email: user@example.com and token=abcd1234efgh"))
print(get_secure_logger())
```

## Kết luận

Nếu pytest chạy pass và log trong secure.log đã che giấu PII, nghĩa là lab secure logger đã hoạt động đúng yêu cầu bảo mật.
