import unittest
from sast_tool.ast_analyzer import ASTAnalyzer


class TestASTAnalyzer(unittest.TestCase):
    def test_eval_detection(self):
        """Kiểm tra phát hiện lời gọi eval() như bài lab yêu cầu."""
        code = "eval('2+2')"
        analyzer = ASTAnalyzer()
        issues = analyzer.analyze(code)
        self.assertTrue(any(i['type'] == 'Use of eval' for i in issues))

    def test_exec_detection(self):
        """Kiểm tra phát hiện lời gọi exec()."""
        code = "exec('print(123)')"
        analyzer = ASTAnalyzer(detect_all=True)
        issues = analyzer.analyze(code)
        self.assertTrue(any(i['type'] == 'Use of exec' for i in issues))

    def test_os_system_detection(self):
        """Kiểm tra phát hiện gọi os.system()."""
        code = "import os\nos.system('dir')"
        analyzer = ASTAnalyzer(detect_all=True)
        issues = analyzer.analyze(code)
        self.assertTrue(any(i['type'] == 'Risky OS Command' for i in issues))

    def test_syntax_error_handling(self):
        """Kiểm tra xử lý lỗi cú pháp an toàn mà không làm sập chương trình."""
        invalid_code = "def broken_func(:\n    pass"
        analyzer = ASTAnalyzer()
        issues = analyzer.analyze(invalid_code)
        self.assertTrue(any(i['type'] == 'Syntax Error' for i in issues))

    def test_safe_code_no_false_positive(self):
        """Kiểm tra mã nguồn an toàn không bị báo lỗi giả (false positive)."""
        safe_code = """
def calculate_sum(a, b):
    return a + b

print(calculate_sum(10, 20))
"""
        analyzer = ASTAnalyzer(detect_all=True)
        issues = analyzer.analyze(safe_code)
        self.assertEqual(len(issues), 0)


if __name__ == '__main__':
    unittest.main()
