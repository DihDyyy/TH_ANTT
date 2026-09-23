import unittest
import sys
import os

# Đảm bảo import được module từ thư mục gốc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from securevalidator import (
    validate_email, validate_url, validate_filename,
    sanitize_sql_input, sanitize_html_input
)
from app import app


class TestValidatorsAutomated(unittest.TestCase):
    """Bộ kiểm thử tự động toàn diện cho thư viện SecureValidator và Web App."""

    def setUp(self):
        # Tạo test client giả lập gửi request đến Flask app
        self.app_client = app.test_client()
        self.app_client.testing = True

    # ==========================================
    # 1. TỰ ĐỘNG KIỂM TRA EMAIL
    # ==========================================
    def test_01_email_auto(self):
        """Tự động duyệt danh sách email hợp lệ và không hợp lệ."""
        test_cases = [
            ("user@example.com", True, "Email chuẩn"),
            ("admin.security@domain.vn", True, "Email có dấu chấm"),
            ("test_123@sub.domain.org", True, "Email có subdomain và số"),
            ("plainaddress", False, "Thiếu @ và domain"),
            ("@missingusername.com", False, "Thiếu username"),
            ("user@.com", False, "Domain thiếu tên"),
            ("user@@doubleat.com", False, "Chứa 2 ký tự @"),
            ("user@domain..com", False, "Chứa 2 dấu chấm liên tiếp"),
        ]
        print("\n--- [1] Tự động kiểm tra Email ---")
        for email, expected, desc in test_cases:
            with self.subTest(email=email):
                result = validate_email(email)
                status = "PASS" if result == expected else "FAIL"
                print(f"  [{status}] {desc:32} | Input: {email:26} => {result}")
                self.assertEqual(result, expected)

    # ==========================================
    # 2. TỰ ĐỘNG KIỂM TRA URL & PHÁT HIỆN SSRF
    # ==========================================
    def test_02_url_auto(self):
        """Tự động kiểm tra URL hợp lệ và cảnh báo lỗ hổng SSRF."""
        test_cases = [
            ("https://google.com", True, "URL HTTPS hợp lệ"),
            ("http://sub.example.com/api", True, "URL HTTP có path"),
            ("ftp://files.example.com", False, "Chặn giao thức FTP"),
            ("javascript:alert(1)", False, "Chặn pseudo-protocol Javascript"),
            ("not_a_valid_url", False, "Chuỗi ký tự ngẫu nhiên"),
        ]
        print("\n--- [2] Tự động kiểm tra URL & SSRF ---")
        for url, expected, desc in test_cases:
            with self.subTest(url=url):
                result = validate_url(url)
                status = "PASS" if result == expected else "FAIL"
                print(f"  [{status}] {desc:32} | Input: {url:26} => {result}")
                self.assertEqual(result, expected)

        # Tự động quét các vector SSRF vào Localhost / mạng nội bộ
        ssrf_targets = ["http://127.0.0.1", "http://localhost:5000", "http://169.254.169.254"]
        print("  [!] Kiểm tra khả năng chống SSRF:")
        for ssrf in ssrf_targets:
            is_valid = validate_url(ssrf)
            print(f"      -> Target: {ssrf:25} | Được chấp nhận: {is_valid} (Nguy cơ SSRF!)")

    # ==========================================
    # 3. TỰ ĐỘNG KIỂM TRA FILENAME & PATH TRAVERSAL
    # ==========================================
    def test_03_filename_auto(self):
        """Tự động kiểm tra tên file và kỹ thuật Path Traversal."""
        test_cases = [
            ("report.pdf", True, "Tên file thông thường"),
            ("my_document_2026.docx", True, "Tên file có dấu gạch dưới"),
            ("../../etc/passwd", False, "Path traversal dạng relative ../"),
            ("..\\Windows\\System32\\cmd.exe", False, "Path traversal dạng Windows ..\\"),
            ("/var/log/syslog", False, "Đường dẫn tuyệt đối Linux"),
            ("C:\\boot.ini", False, "Đường dẫn tuyệt đối Windows"),
        ]
        print("\n--- [3] Tự động kiểm tra Filename & Traversal ---")
        for filename, expected, desc in test_cases:
            with self.subTest(filename=filename):
                result = validate_filename(filename)
                status = "PASS" if result == expected else "FAIL"
                print(f"  [{status}] {desc:32} | Input: {filename:26} => {result}")
                self.assertEqual(result, expected)

        # Tự động thử nghiệm Bypass bằng mã hóa URL
        bypass_payload = "%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        b_res = validate_filename(bypass_payload)
        print(f"  [!] Kiểm tra Bypass URL Encoding: {bypass_payload} => Chấp nhận: {b_res}")

    # ==========================================
    # 4. TỰ ĐỘNG KIỂM TRA SQL SANITIZATION & BYPASS
    # ==========================================
    def test_04_sql_auto(self):
        """Tự động kiểm tra làm sạch SQL và phát hiện Bypass lồng từ khóa."""
        print("\n--- [4] Tự động kiểm tra SQL Sanitization ---")
        # Chuỗi an toàn không bị mất chữ
        safe_str = "san pham cong nghe"
        self.assertEqual(sanitize_sql_input(safe_str), safe_str)
        print(f"  [PASS] Chuỗi văn bản an toàn được giữ nguyên: '{safe_str}'")

        # Chuỗi tấn công cơ bản
        injections = [
            ("admin' OR 1=1 --", "Lọc dấu nháy và --"),
            ("test; DROP TABLE users;", "Lọc dấu chấm phẩy ; và DROP"),
        ]
        for inj, desc in injections:
            cleaned = sanitize_sql_input(inj)
            self.assertNotIn("'", cleaned)
            self.assertNotIn(";", cleaned)
            self.assertNotIn("--", cleaned)
            print(f"  [PASS] {desc:32} | Sau lọc: '{cleaned}'")

        # Tự động thử nghiệm kỹ thuật lồng từ khóa (Nested keyword bypass)
        nested_payload = "1 oORr 1=1"
        cleaned_nested = sanitize_sql_input(nested_payload)
        has_or = "or" in cleaned_nested.lower()
        print(f"  [!] Thử nghiệm SQL Bypass (Nested keyword):")
        print(f"      -> Input: '{nested_payload}' => Sau lọc: '{cleaned_nested}'")
        if has_or:
            print("      => CẢNH BÁO: Từ khóa 'or' vẫn tồn tại sau khi lọc (Lỗ hổng Bypass)!")

    # ==========================================
    # 5. TỰ ĐỘNG KIỂM TRA HTML / XSS SANITIZATION
    # ==========================================
    def test_05_html_auto(self):
        """Tự động kiểm tra mã hóa XSS."""
        print("\n--- [5] Tự động kiểm tra HTML XSS ---")
        xss_payload = '<script>alert("XSS")</script>'
        escaped = sanitize_html_input(xss_payload)
        self.assertNotIn("<script>", escaped)
        self.assertIn("&lt;script&gt;", escaped)
        print(f"  [PASS] Đã mã hóa thẻ script thành entities: {escaped}")

    # ==========================================
    # 6. TỰ ĐỘNG TEST TOÀN BỘ GIAO DIỆN WEB APP FLASK
    # ==========================================
    def test_06_web_app_auto(self):
        """Tự động gửi request GET và POST đến Web App."""
        print("\n--- [6] Tự động kiểm tra Web App (GET & POST Request) ---")
        # 1. Tự động kiểm tra trang chủ GET /
        res_get = self.app_client.get("/")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn(b"SecureValidator", res_get.data)
        print("  [PASS] GET / phản hồi mã 200 và giao diện hoạt động.")

        # 2. Tự động gửi form POST dữ liệu
        form_data = {
            "email": "dinhduy@gmail.com",
            "url": "https://github.com",
            "filename": "report.pdf",
            "sql": "hello world",
            "html": "<b>test</b>"
        }
        res_post = self.app_client.post("/", data=form_data)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn("Email hợp lệ".encode("utf-8"), res_post.data)
        self.assertIn("URL hợp lệ".encode("utf-8"), res_post.data)
        self.assertIn("Tên file hợp lệ".encode("utf-8"), res_post.data)
        print("  [PASS] POST / gửi form tự động: Server xử lý và hiển thị kết quả chuẩn xác.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
