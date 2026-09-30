# 🔐 CryptoToolkit - SecureCrypto

> **Bài 2: Mã hoá, Triển khai PKI** — Thư viện mật mã Python

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Mô tả

**SecureCrypto** là thư viện mật mã được xây dựng bằng Python, cung cấp các chức năng:

| Chức năng | Mô tả |
|-----------|--------|
| `encrypt_file_aes(filepath, password)` | Mã hóa file bằng **AES-256-GCM** |
| `decrypt_file_aes(encrypted_file, password)` | Giải mã file |
| `generate_rsa_keypair(key_size)` | Tạo cặp khóa **RSA** |
| `sign_data_rsa(data, private_key)` | Ký số dữ liệu bằng RSA |
| `verify_signature_rsa(data, signature, public_key)` | Xác thực chữ ký số |
| `hash_password_secure(password)` | Băm mật khẩu an toàn bằng **Argon2** |

---

## 📁 Cấu trúc thư mục

```
crypto-toolkit/
├── files/
│   └── data.txt                # File dữ liệu mẫu
├── securecrypto/
│   ├── __init__.py             # Package init (v0.1.0)
│   ├── aes_utils.py            # Mã hóa/giải mã AES-256-GCM
│   ├── hash_utils.py           # Băm mật khẩu Argon2
│   ├── rsa_utils.py            # RSA keypair, ký số, xác thực
│   ├── cli.py                  # Giao diện dòng lệnh (CLI)
│   ├── api.py                  # Flask REST API
│   └── app_gui.py              # Giao diện đồ họa (Tkinter GUI)
├── tests/
│   ├── test_aes_utils.py       # Unit test AES
│   ├── test_hash_utils.py      # Unit test Hash
│   └── test_rsa_utils.py       # Unit test RSA
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🚀 Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/dihdyyy/crypto-toolkit.git
cd crypto-toolkit
```

### 2. Cài đặt package

```bash
pip install -e .
```

---

## 🧪 Chạy Unit Tests

```bash
pytest tests/ -v
```

**Kết quả mong đợi:**

```
tests/test_aes_utils.py::test_encrypt_decrypt PASSED
tests/test_hash_utils.py::test_hash_password_and_verify PASSED
tests/test_hash_utils.py::test_wrong_password_verification PASSED
tests/test_rsa_utils.py::test_rsa_keypair_generation PASSED
tests/test_rsa_utils.py::test_sign_and_verify PASSED
tests/test_rsa_utils.py::test_verify_invalid_signature PASSED

============================== 6 passed ==============================
```

---

## 💻 Sử dụng CLI

### Mã hóa file

```bash
securecrypto-cli --encrypt .\files\data.txt --password pass123
```

> 📌 Lưu lại chuỗi **base64 key** được in ra để dùng cho giải mã.

### Giải mã file

```bash
securecrypto-cli --decrypt .\files\data.txt.enc --password <BASE64_KEY>
```

### Kiểm tra kết quả

```bash
cat .\files\data.txt.dec
# Output: HUTECH University
```

---

## 🖥️ Sử dụng GUI

```bash
python securecrypto/app_gui.py
```

1. Nhập mật khẩu
2. Chọn nút **Encrypt** → Chọn file → OK
3. Lưu Key để giải mã
4. Chọn nút **Decrypt** → Chọn file `.enc` → OK

---

## 🌐 Sử dụng Flask API

### Khởi động server

```bash
python securecrypto/api.py
```

> Server chạy tại: `http://127.0.0.1:5000`

### API Encrypt

```
POST http://127.0.0.1:5000/encrypt
Content-Type: form-data
  - file: <chọn file>
  - password: pass123
```

**Response:**
```json
{
  "key": "FfvGs3AV63u0AOWSHXnKF6V9uE1QPo4FewsAVj5KhrQ="
}
```

### API Decrypt

```
POST http://127.0.0.1:5000/decrypt
Content-Type: form-data
  - file: <chọn file .enc>
  - password: <BASE64_KEY>
```

**Response:**
```json
{
  "output": "path/to/decrypted/file"
}
```


---

## 🛠️ Công nghệ sử dụng

- **Python 3.10+**
- **cryptography** — AES-256-GCM, RSA, PBKDF2
- **argon2-cffi** — Băm mật khẩu Argon2
- **Flask** — REST API
- **Tkinter** — GUI
- **pytest** — Unit testing