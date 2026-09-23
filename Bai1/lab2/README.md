# Lab 2 - Git pre-commit security hook

## Mục tiêu

Lab này mục tiêu kiểm tra khả năng chặn secret, API key, password và các dữ liệu nhạy cảm trước khi commit code.

- Chặn các chuỗi nhạy cảm trong file đã staged
- Cảnh báo khi file có password, token, API key, AWS key
- Sử dụng Git hook để ngăn commit không an toàn
- Kiểm tra bằng pytest để xác nhận logic hoạt động

## Cấu trúc thư mục

- .githooks/pre-commit: hook Git chạy trước khi commit
- pre-commit-hook-test/: thư mục chứa ví dụ file tốt và file xấu
- requirements.txt: phụ thuộc cần thiết
- README.md: hướng dẫn lab

## Bước 1: cài đặt dependency

```powershell
cd E:\Bai1\Lab2
python -m pip install -r requirements.txt
```

## Bước 2: định nghĩa Git hook

```powershell
git config core.hooksPath .githooks
```

Kiểm tra lại:

```powershell
git config --get core.hooksPath
```

## Bước 3: test trường hợp xấu

```powershell
git add pre-commit-hook-test/bad.py
git commit -m "test bad secret"
```

Kết quả mong đợi:
- commit bị chặn
- thông báo phát hiện sensitive data

## Bước 4: test trường hợp tốt

```powershell
git add pre-commit-hook-test/good.py
git commit -m "test good file"
```

Kết quả mong đợi:
- commit được phép
- không có cảnh báo

## Bước 5: chạy test Python ở thư mục lab con

```powershell
cd E:\Bai1\Lab2\pre-commit-hook-test
python -m pytest -q
```

Kết quả mong đợi:

```text
3 passed
```

## Bước 6: chạy hook thủ công

```powershell
cd E:\Bai1\Lab2
bash .githooks/pre-commit
```

Nếu đang dùng PowerShell trên Windows, bạn có thể chạy bằng Git Bash hoặc gọi shell tương ứng.

## Kết luận

Nếu file bad.py bị chặn và file good.py không bị chặn, lab này đang hoạt động đúng như mục tiêu bảo mật trước khi commit.
