import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from network_traffic_analyzer import NetworkTrafficAnalyzer


class TestNetworkTrafficAnalyzer(unittest.TestCase):
    def test_get_network_stats(self):
        """Kiểm tra lấy thống kê I/O card mạng theo chuẩn bài lab."""
        nta = NetworkTrafficAnalyzer()
        stats = nta.get_network_stats()
        self.assertIsInstance(stats, dict)

    def test_get_connections_safe(self):
        """Kiểm tra truy vấn danh sách kết nối an toàn với PID hiện hành."""
        nta = NetworkTrafficAnalyzer()
        conns = nta.get_connections(pid=os.getpid())
        self.assertIsInstance(conns, list)

    def test_get_connections_invalid_pid(self):
        """Kiểm tra xử lý an toàn khi truyền PID không tồn tại."""
        nta = NetworkTrafficAnalyzer()
        conns = nta.get_connections(pid=9999999)
        self.assertEqual(conns, [])


if __name__ == '__main__':
    unittest.main()
