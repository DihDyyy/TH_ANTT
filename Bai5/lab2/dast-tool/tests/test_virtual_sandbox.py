import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from virtual_sandbox import VirtualSandbox


class TestVirtualSandbox(unittest.TestCase):
    def test_run_isolated(self):
        """Kiểm tra thực thi lệnh cô lập theo chuẩn bài lab."""
        vs = VirtualSandbox()
        try:
            out, err = vs.run_isolated("echo test")
            self.assertIn("test", out)
            self.assertEqual(err, "")
        finally:
            vs.cleanup()

    def test_timeout_protection(self):
        """Kiểm tra cơ chế timeout ngắt lệnh chạy quá lâu."""
        vs = VirtualSandbox()
        try:
            # Lệnh sleep trong PowerShell / Windows ping
            out, err = vs.run_isolated("powershell -Command Start-Sleep -Seconds 3", timeout=1)
            self.assertIn("Timeout", err)
        finally:
            vs.cleanup()

    def test_cleanup_removes_temp_dir(self):
        """Kiểm tra dọn dẹp thư mục tạm thành công."""
        vs = VirtualSandbox()
        temp_dir = vs.temp_dir
        self.assertTrue(os.path.exists(temp_dir))
        vs.cleanup()
        self.assertFalse(os.path.exists(temp_dir))


if __name__ == '__main__':
    unittest.main()
