import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from runtime_monitor import RuntimeMonitor


class TestRuntimeMonitor(unittest.TestCase):
    def test_cpu_and_memory(self):
        """Kiểm tra đo CPU và bộ nhớ theo chuẩn bài lab."""
        rm = RuntimeMonitor(os.getpid())
        self.assertIsInstance(rm.get_cpu_usage(interval=0.1), float)
        self.assertGreaterEqual(rm.get_memory_usage(), 0)

    def test_open_files_list(self):
        """Kiểm tra lấy danh sách file đang mở không bị lỗi."""
        rm = RuntimeMonitor(os.getpid())
        files = rm.get_open_files()
        self.assertIsInstance(files, list)

    def test_nonexistent_pid(self):
        """Kiểm tra xử lý PID không tồn tại an toàn không bị sập."""
        rm = RuntimeMonitor(9999999)
        self.assertFalse(rm.is_running())
        self.assertEqual(rm.get_cpu_usage(), 0.0)
        self.assertEqual(rm.get_memory_usage(), 0)
        self.assertEqual(rm.get_open_files(), [])


if __name__ == '__main__':
    unittest.main()
