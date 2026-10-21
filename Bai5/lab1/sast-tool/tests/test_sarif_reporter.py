import json
import os
import unittest
from sast_tool.sarif_reporter import SarifReporter


class TestSarifReporter(unittest.TestCase):
    def test_generate_report(self):
        """Kiểm tra sinh file SARIF từ danh sách issue theo tài liệu."""
        issues = [{
            'type': 'Test',
            'message': 'Test message',
            'lineno': 1,
            'col_offset': 0
        }]
        reporter = SarifReporter()
        output_file = "test_report.sarif"
        reporter.generate_report(issues, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Kiểm tra nội dung JSON hợp lệ và đúng schema SARIF
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data.get("version"), "2.1.0")
            self.assertIn("runs", data)
            self.assertEqual(len(data["runs"][0]["results"]), 1)

        os.remove(output_file)

    def test_generate_empty_report(self):
        """Kiểm tra trường hợp không có issue nào, vẫn tạo SARIF 2.1.0 hợp lệ."""
        reporter = SarifReporter()
        output_file = "empty_report.sarif"
        reporter.generate_report([], output_file)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data.get("version"), "2.1.0")
            self.assertEqual(len(data["runs"][0]["results"]), 0)

        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
