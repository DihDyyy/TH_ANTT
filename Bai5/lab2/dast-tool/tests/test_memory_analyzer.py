import os
import sys
import unittest

# Đảm bảo đường dẫn module gốc được nạp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory_analyzer import MemoryAnalyzer


class TestMemoryAnalyzer(unittest.TestCase):
    def test_check_overflow(self):
        """Kiểm tra tràn số theo chuẩn bài lab."""
        ma = MemoryAnalyzer()
        self.assertTrue(ma.check_overflow(2**64))
        self.assertFalse(ma.check_overflow(100))

    def test_check_memory_leaks(self):
        """Kiểm tra đối tượng rò rỉ rác qua GC."""
        ma = MemoryAnalyzer()
        leaks = ma.check_memory_leaks()
        self.assertIsInstance(leaks, list)

    def test_memory_trend_analysis(self):
        """Kiểm tra phân tích xu hướng tăng trưởng bộ nhớ."""
        ma = MemoryAnalyzer()
        # Không đủ mẫu
        self.assertEqual(ma.analyze_trend()["trend"], "INSUFFICIENT_DATA")

        # Ghi nhận mẫu ổn định
        ma.record_sample(1000)
        ma.record_sample(1050)
        trend_normal = ma.analyze_trend(threshold_growth_percent=30.0)
        self.assertFalse(trend_normal["alert"])

        # Ghi nhận mẫu tăng vọt (1000 -> 2000 = +100%)
        ma.record_sample(2000)
        trend_spike = ma.analyze_trend(threshold_growth_percent=30.0)
        self.assertTrue(trend_spike["alert"])


if __name__ == '__main__':
    unittest.main()
