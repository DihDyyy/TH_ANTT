# Lab 2 - Git pre-commit security hook

## Mục tiêu

Lab này kiểm tra khả năng chặn secret, API key, password và các rủi ro bảo mật trước khi commit code.

- file .githooks/pre-commit: hook kiểm tra commit
- file bad.py: mã ví dụ có secret nhạy cảm
- file good.py: mã sạch
- file test_apikey.py: kiểm thử bằng Python

## Cấu trúc thư mục

- .githooks/pre-commit: hook Git chạy trước khi commit
- bad.py: ví dụ chứa secret, token và password
- good.py: ví dụ không chứa secret
- test_apikey.py: script kiểm tra phát hiện secret

## Bước 1: cài đặt phụ thuộc

Mở PowerShell trong thư mục Lab 2:

```powershell
cd E:\Bai1\Lab2
python -m pip install -r requirements.txt
```

## Bước 2: thiết lập Git hook

Từ thư mục Lab 2:

```powershell
git config core.hooksPath .githooks
```

Nếu bạn muốn kiểm tra lại:

```powershell
git config --get core.hooksPath
```

Kết quả mong đợi:

```text
.githooks
```

## Bước 3: test trường hợp xấu

Thử stage file có chứa secret:

```powershell
git add pre-commit-hook-test/bad.py
git commit -m "test bad secret"
```

Kết quả mong đợi:
- commit bị chặn
- hiển thị cảnh báo: secret, password, token hoặc API key phát hiện

## Bước 4: test trường hợp tốt

Thử stage file sạch:

```powershell
git add pre-commit-hook-test/good.py
git commit -m "test good file"
```

Kết quả mong đợi:
- commit được phép
- hook không phát hiện rủi ro

## Bước 5: chạy test Python trực tiếp

```powershell
cd E:\Bai1\Lab2\pre-commit-hook-test
python test_apikey.py
```

Nếu script không có output, nghĩa là file đang không phát hiện nếu secret chưa được kiểm tra đúng cách.

## Bước 6: kiểm tra hook thủ công

Bạn có thể chạy hook mà không cần commit:

```powershell
bash .githooks/pre-commit
```

Nếu đang dùng PowerShell trên Windows, có thể dùng:

```powershell
python .githooks/pre-commit
```

Hoặc chạy Git bash nếu có sẵn.

## Gợi ý kiểm tra nhanh

Dùng file bad.py chứa mẫu như:
- password
- token
- api key
- AWS key

Đây là dữ liệu hook phải chặn.

## Kết luận

Nếu hook chặn được file bad.py nhưng không chặn file good.py, nghĩa là lab đã hoạt động đúng mục tiêu của bảo mật trước khi commit.
