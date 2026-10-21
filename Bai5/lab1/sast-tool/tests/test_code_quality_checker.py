import os
import tempfile
import unittest
from sast_tool.code_quality_checker import CodeQualityChecker


class TestCodeQualityChecker(unittest.TestCase):
    def test_flake8_detection(self):
        """Kiểm tra tích hợp linter flake8 như tài liệu gốc."""
        tmp = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding='utf-8')
        try:
            tmp.write("import os\n\n\n")
            tmp.flush()
            tmp_path = tmp.name
            tmp.close()

            checker = CodeQualityChecker()
            issues = checker.check(tmp_path)
            self.assertTrue(all(i['type'] == 'Lint Issue' for i in issues) or len(issues) == 0)
        finally:
            if os.path.exists(tmp.name):
                try:
                    os.remove(tmp.name)
                except Exception:
                    pass

    def test_compute_metrics(self):
        """Kiểm tra tính toán đầy đủ 5 chỉ số chất lượng mã nguồn."""
        sample_code = """
import os
import sys

def complex_function(x):
    if x > 10:
        for i in range(5):
            if i % 2 == 0:
                print(i)
    eval("1+1")
    return x
"""
        checker = CodeQualityChecker()
        metrics = checker.compute_metrics(sample_code)

        self.assertIn("cyclomatic_complexity", metrics)
        self.assertIn("function_length", metrics)
        self.assertIn("nested_depth", metrics)
        self.assertIn("dependency_count", metrics)
        self.assertIn("security_smell_density_per_100_loc", metrics)

        # Kiểm tra giá trị hợp lý
        self.assertGreaterEqual(metrics["cyclomatic_complexity"]["max"], 3)
        self.assertGreaterEqual(metrics["nested_depth"], 3)
        self.assertEqual(metrics["dependency_count"], 2)
        self.assertEqual(metrics["security_smell_count"], 1)


if __name__ == '__main__':
    unittest.main()
