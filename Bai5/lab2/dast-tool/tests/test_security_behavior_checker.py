import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security_behavior_checker import SecurityBehaviorChecker


class TestSecurityBehaviorChecker(unittest.TestCase):
    def test_suspicious_calls(self):
        """Kiểm tra tìm kiếm các lời gọi nguy hiểm theo chuẩn bài lab."""
        sbc = SecurityBehaviorChecker()
        self.assertIsInstance(sbc.suspicious_calls(), list)

    def test_evaluate_runtime_events_normal(self):
        """Kiểm tra đánh giá sự kiện khi chỉ số bình thường không sinh cảnh báo HIGH."""
        sbc = SecurityBehaviorChecker()
        normal_metrics = {
            "cpu_percent": 15.0,
            "memory_rss": 20 * 1024 * 1024,
            "connections_count": 2,
            "open_files_count": 10
        }
        alerts = sbc.evaluate_runtime_events(normal_metrics)
        self.assertEqual(len(alerts), 0)

    def test_evaluate_runtime_events_spike(self):
        """Kiểm tra phát hiện cảnh báo khi CPU và kết nối mạng tăng vọt."""
        sbc = SecurityBehaviorChecker()
        anomalous_metrics = {
            "cpu_percent": 95.0,
            "memory_rss": 500 * 1024 * 1024,
            "connections_count": 80,
            "open_files_count": 200,
            "memory_alert": True,
            "memory_message": "Memory growth spike detected"
        }
        alerts = sbc.evaluate_runtime_events(anomalous_metrics)
        self.assertGreaterEqual(len(alerts), 3)
        self.assertTrue(any(a["level"] == "HIGH" for a in alerts))


if __name__ == '__main__':
    unittest.main()
