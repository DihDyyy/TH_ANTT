# 📑 BÁO CÁO THỰC HÀNH LAB 1: QUÉT LỖ HỔNG WEB APP (WEBVULNSCANNER)

---

## 👨‍🎓 Thông tin sinh viên
- **Họ và tên:** Lê Đình Duy
- **Mã số sinh viên (MSSV):** 2387700102
- **Lớp:** 23DATA1
- **Username hệ thống:** dihdyyy
- **Môn học:** Bảo mật mạng máy tính / Lập trình An ninh thông tin
- **Bài thực hành:** Bài 4 - Lab 1: Xây dựng công cụ quét lỗ hổng Web App (WebVulnScanner)

---

## 🎯 Mục tiêu bài thực hành
1. **Tìm hiểu các lỗ hổng Web phổ biến trong OWASP Top 10:** Hiểu rõ bản chất, cơ chế khai thác và hậu quả của các lỗ hổng XSS (Reflected, Stored, DOM), SQL Injection (Classic, Blind, Time-based, Union), CSRF và SSRF.
2. **Xây dựng module XSSScanner:** Tự động phát hiện lỗ hổng XSS thông qua việc gửi các payload kiểm thử chuẩn hóa và phân tích phản hồi HTTP.
3. **Xây dựng module SQLInjectionTester:** Kiểm tra các biến thể tấn công SQL Injection trên các tham số Query String của URL.
4. **Xây dựng module CSRFDetector:** Phân tích mã HTML trả về để phát hiện các form nhập dữ liệu thiếu token bảo vệ chống tấn công CSRF.
5. **Xây dựng module SSRFTester:** Phát hiện các tham số có nguy cơ trỏ tới địa chỉ IP hoặc dải mạng nội bộ (`127.0.0.1`, `localhost`, `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`).
6. **Xây dựng ReportGenerator và Web UI:** Tự động tổng hợp kết quả quét ra file HTML báo cáo chi tiết, tích hợp giao diện web thân thiện sử dụng Flask Framework.

---

## 🏗️ Cấu trúc thư mục dự án
```text
lab1/
├── __init__.py
├── main.py                          # Điểm chạy chính của CLI scanner
├── requirements.txt                 # Khai báo các thư viện phụ thuộc
├── reportlab1.md                    # Báo cáo thực hành chi tiết Lab 1
├── images/                          # Ảnh chụp minh chứng các bước thực nghiệm Lab 1
├── report/
│   ├── __init__.py
│   └── report_generator.py          # Module tạo báo cáo kết quả quét HTML
├── scanners/
│   ├── __init__.py
│   ├── csrf_detector.py             # Bộ phát hiện lỗ hổng CSRF
│   ├── sql_injection_tester.py      # Bộ kiểm thử SQL Injection
│   ├── ssrf_tester.py               # Bộ kiểm thử SSRF
│   └── xss_scanner.py               # Bộ quét lỗ hổng XSS
├── tests/
│   ├── __init__.py
│   ├── test_csrf.py                 # Test case kiểm thử module CSRF
│   ├── test_report.py               # Test case kiểm thử module Report
│   ├── test_sql_injection.py        # Test case kiểm thử module SQLi
│   ├── test_ssrf.py                 # Test case kiểm thử module SSRF
│   └── test_xss.py                  # Test case kiểm thử module XSS
└── ui/
    ├── __init__.py
    ├── app.py                       # Máy chủ Flask cung cấp giao diện Web
    └── templates/
        ├── index.html               # Trang chủ nhập URL kiểm thử
        └── result.html              # Trang hiển thị chi tiết kết quả quét
```

---

## 🛠️ Các bước thực hiện & Kết quả kiểm thử

### Bước 1: Khai báo và cài đặt các gói phụ thuộc (`requirements.txt`)
- **Mục đích:** Cài đặt các thư viện Python cần thiết bao gồm `Flask` để triển khai giao diện Web UI và `requests` phục vụ gửi HTTP request quét lỗ hổng.
- **Nội dung `requirements.txt`:**
  ```text
  Flask
  requests
  ```
- **📸 Ảnh chụp file requirements.txt:**

  ![Bước 1: File requirements.txt](images/01_requirements.jpeg)

- **Lệnh thực hiện cài đặt trên Terminal:**
  ```cmd
  pip install -r requirements.txt
  ```
- **📸 Ảnh chụp màn hình cài đặt pip:**

  ![Bước 1: Cài đặt các gói phụ thuộc](images/02_pip_install.jpeg)

---

### Bước 2: Xây dựng module phát hiện CSRF (`scanners/csrf_detector.py`)
- **Mục đích:** Sử dụng biểu thức chính quy (Regex) quét qua nội dung HTML trả về từ mục tiêu, tìm kiếm các trường token bảo vệ như `csrf_token`, `_csrf`, `csrfmiddlewaretoken`. Nếu form không chứa token, hệ thống ghi nhận lỗ hổng mức độ `Medium`.
- **Mã nguồn triển khai:**
  ```python
  import re

  class CSRFDetector:
      csrf_token_patterns = [
          re.compile(r'name=["\']csrf_token["\']', re.I),
          re.compile(r'name=["\']_csrf["\']', re.I),
          re.compile(r'name=["\']csrfmiddlewaretoken["\']', re.I)
      ]

      def scan(self, html_content):
          for pattern in self.csrf_token_patterns:
              if pattern.search(html_content):
                  return {'csrf_protected': True}
          return {'csrf_protected': False, 'desc': 'No CSRF token found, vulnerable to CSRF', 'risk': 'Medium'}
  ```
- **📸 Ảnh chụp mã nguồn `scanners/csrf_detector.py`:**

  ![Bước 2: Module csrf_detector.py](images/03_csrf_detector.jpeg)

---

### Bước 3: Xây dựng module kiểm thử SQL Injection (`scanners/sql_injection_tester.py`)
- **Mục đích:** Phân tích các tham số trên URL (`urlparse`, `parse_qs`), kiểm tra các giá trị tham số với danh sách payload SQLi đặc trưng như `' OR '1'='1`, `'; DROP TABLE users;--`, `' UNION SELECT NULL--` để phát hiện điểm tiêm mã SQL.
- **Mã nguồn triển khai:**
  ```python
  from urllib.parse import urlparse, parse_qs

  class SQLInjectionTester:
      payloads = [
          "' OR '1'='1",
          "'; DROP TABLE users;--",
          "\" OR 1=1--",
          "' UNION SELECT NULL--"
      ]

      def scan(self, url):
          findings = []
          parsed = urlparse(url)
          params = parse_qs(parsed.query)

          for param, values in params.items():
              for val in values:
                  for payload in self.payloads:
                      if payload in val:
                          findings.append({
                              'param': param,
                              'payload': payload,
                              'desc': 'Potential SQL Injection',
                              'risk': 'Critical'
                          })
          return findings
  ```
- **📸 Ảnh chụp mã nguồn `scanners/sql_injection_tester.py`:**

  ![Bước 3: Module sql_injection_tester.py](images/04_sql_injection_tester.jpeg)

---

### Bước 4: Xây dựng module kiểm thử SSRF (`scanners/ssrf_tester.py`)
- **Mục đích:** Phát hiện các tham số URL chứa địa chỉ trỏ tới tài nguyên mạng nội bộ hoặc dải địa chỉ Private/Loopback (`localhost`, `127.0.0.1`, `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`) nhằm ngăn chặn việc kẻ tấn công lợi dụng máy chủ truy cập trái phép hạ tầng bên trong.
- **Mã nguồn triển khai:**
  ```python
  import re
  from urllib.parse import urlparse, parse_qs

  class SSRFTester:
      internal_ips = [
          re.compile(r'127\.0\.0\.1'),
          re.compile(r'localhost'),
          re.compile(r'10\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
          re.compile(r'192\.168\.\d{1,3}\.\d{1,3}'),
          re.compile(r'172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}')
      ]

      def scan(self, url):
          findings = []
          parsed = urlparse(url)
          params = parse_qs(parsed.query)

          for param, values in params.items():
              for val in values:
                  for pattern in self.internal_ips:
                      if pattern.search(val):
                          findings.append({
                              'param': param,
                              'value': val,
                              'desc': 'Potential SSRF to internal resource',
                              'risk': 'High'
                          })
          return findings
  ```
- **📸 Ảnh chụp mã nguồn `scanners/ssrf_tester.py`:**

  ![Bước 4: Module ssrf_tester.py](images/05_ssrf_tester.jpeg)

---

### Bước 5: Xây dựng module quét XSS (`scanners/xss_scanner.py`)
- **Mục đích:** Khởi tạo thư viện payload XSS (`<script>alert(1)</script>`, `"><svg/onload=alert(1)>`), gửi request kiểm thử đến máy chủ và kiểm tra xem payload có bị phản chiếu lại trong mã HTML hay không.
- **📸 Ảnh chụp mã nguồn `scanners/xss_scanner.py`:**

  ![Bước 5: Module xss_scanner.py - Phần 1](images/06_xss_scanner_part1.jpeg)

  ![Bước 5: Module xss_scanner.py - Phần 2](images/07_xss_scanner_part2.jpeg)

---

### Bước 6: Xây dựng bộ Unit Tests kiểm thử tự động (`tests/`)
- **Mục đích:** Đảm bảo toàn bộ các bộ scanner, module tạo báo cáo hoạt động chính xác trước khi đưa vào chạy thực tế.
- **Kiểm thử CSRF (`tests/test_csrf.py`):**
  ![Bước 6: Test CSRF](images/08_test_csrf.jpeg)

- **Kiểm thử SQL Injection (`tests/test_sql_injection.py`):**
  ![Bước 6: Test SQLi](images/09_test_sql_injection.jpeg)

- **Kiểm thử SSRF (`tests/test_ssrf.py`):**
  ![Bước 6: Test SSRF](images/10_test_ssrf.jpeg)

- **Kiểm thử XSS (`tests/test_xss.py`):**
  ![Bước 6: Test XSS](images/11_test_xss.jpeg)

- **Kiểm thử Report Generator (`tests/test_report.py`):**
  ![Bước 6: Test Report - Phần 1](images/12_test_report_part1.jpeg)
  ![Bước 6: Test Report - Phần 2](images/13_test_report_part2.jpeg)

---

### Bước 7: Xây dựng điểm chạy dòng lệnh chính (`main.py`)
- **Mục đích:** Tiếp nhận URL từ đối số dòng lệnh (`argparse`), kiểm tra tính hợp lệ của URL, kích hoạt đồng thời 4 module quét và gọi `ReportGenerator` để xuất báo cáo.
- **📸 Ảnh chụp mã nguồn `main.py`:**

  ![Bước 7: File main.py - Phần 1](images/14_main_part1.jpeg)

  ![Bước 7: File main.py - Phần 2](images/15_main_part2.jpeg)

---

### Bước 8: Xây dựng module xuất báo cáo HTML (`report/report_generator.py`)
- **Mục đích:** Định dạng kết quả quét thành bảng HTML chuyên nghiệp kèm phân loại mức độ rủi ro (Critical, High, Medium, Low) cùng mốc thời gian quét.
- **📸 Ảnh chụp mã nguồn `report/report_generator.py`:**

  ![Bước 8: File report_generator.py](images/16_report_generator.jpeg)

---

### Bước 9: Xây dựng giao diện người dùng Web UI bằng Flask (`ui/`)
- **Mục đích:** Cung cấp giao diện trực quan cho người dùng nhập URL mục tiêu và hiển thị trực tiếp danh sách lỗ hổng phát hiện được trên trình duyệt web.
- **Mã nguồn điều khiển (`ui/app.py`):**
  ![Bước 9: Code ui/app.py - Phần 1](images/17_app_ui_part1.jpeg)
  ![Bước 9: Code ui/app.py - Phần 2](images/18_app_ui_part2.jpeg)

- **Giao diện trang chủ (`ui/templates/index.html`):**
  ![Bước 9: Template index.html - Phần 1](images/19_template_index_part1.jpeg)
  ![Bước 9: Template index.html - Phần 2](images/20_template_index_part2.jpeg)

- **Giao diện kết quả (`ui/templates/result.html`):**
  ![Bước 9: Template result.html - Phần 1](images/21_template_result_part1.jpeg)
  ![Bước 9: Template result.html - Phần 2](images/22_template_result_part2.jpeg)

---

### Bước 10: Chạy và kiểm tra kết quả Unit Test
- **Mục đích:** Xác minh toàn bộ chức năng kiểm thử đơn vị của các module.
- **Lệnh thực hiện trên Terminal:**
  ```cmd
  python -m pytest tests/
  ```
- **Kết quả kỳ vọng:** Toàn bộ 5 bài kiểm thử đều đạt trạng thái `PASSED`.
- **📸 Ảnh chụp màn hình chạy Unit Test:**

  ![Bước 10: Kết quả chạy Unit Test](images/23_unittest_run.jpeg)

---

### Bước 11: Kiểm thử quét mục tiêu qua dòng lệnh CLI
- **Mục đích:** Thực thi quét một URL mẫu chứa tham số truy vấn qua giao diện dòng lệnh:
- **Lệnh thực hiện:**
  ```cmd
  python main.py "http://testphp.vulnweb.com/listproducts.php?cat=1"
  ```
- **📸 Ảnh chụp kết quả quét qua CLI:**

  ![Bước 11: Chạy quét bằng dòng lệnh](images/24_main_run.jpeg)

---

### Bước 12: Khởi chạy và kiểm tra trên Web UI
- **Mục đích:** Khởi động máy chủ Flask tại cổng 5001 và thực hiện quét trực quan từ trình duyệt.
- **Lệnh thực hiện:**
  ```cmd
  python ui/app.py
  ```
- **📸 Ảnh chụp khởi động Web UI trên Terminal:**

  ![Bước 12: Khởi động Web UI](images/25_ui_run.jpeg)

- **📸 Ảnh chụp giao diện nhập URL trên trình duyệt:**

  ![Bước 12: Giao diện nhập URL quét](images/26_ui_browser_index.jpeg)

- **📸 Ảnh chụp bảng kết quả quét lỗ hổng:**

  ![Bước 12: Kết quả quét trên Web UI](images/27_ui_browser_result.jpeg)

---

### Bước 13: Môi trường kiểm thử mẫu và Commit mã nguồn lên Git
- **Môi trường thử nghiệm hợp lệ:** Sử dụng các trang web được thiết kế chuyên biệt cho kiểm thử bảo mật như `http://testphp.vulnweb.com/` và `http://testhtml5.vulnweb.com/`.
- **📸 Ảnh chụp danh sách trang web kiểm thử:**

  ![Bước 13: Danh sách web kiểm thử](images/28_test_sites.jpeg)

- **Đóng gói mã nguồn lên GitHub:**
  ```cmd
  git add .
  git commit -m "[add] web vulnerability scanner"
  git push origin main
  ```
- **📸 Ảnh chụp commit và push Git:**

  ![Bước 13: Git commit và push](images/29_git_commit_push.jpeg)

---

## 💡 Đánh giá và Kết luận
- **Tính thực tiễn:** Công cụ `WebVulnScanner` đã hoàn thành đầy đủ các yêu cầu cốt lõi, có khả năng phát hiện nhanh các nguy cơ bảo mật web phổ biến trong giai đoạn phát triển và kiểm thử phần mềm.
- **Kiến trúc module hóa:** Việc phân tách độc lập giữa các scanner, bộ sinh báo cáo và giao diện web giúp mã nguồn dễ đọc, dễ bảo trì và có thể dễ dàng mở rộng thêm các kỹ thuật quét khác như Path Traversal hoặc Open Redirect.
- **Tính an toàn và đạo đức:** Mọi hoạt động kiểm thử chỉ được thực hiện trên môi trường giả lập hoặc các hệ thống có sự cho phép rõ ràng từ chủ quản hệ thống.
