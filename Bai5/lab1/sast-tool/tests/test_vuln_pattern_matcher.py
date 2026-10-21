import unittest
from sast_tool.vuln_pattern_matcher import VulnPatternMatcher


class TestVulnPatternMatcher(unittest.TestCase):
    def test_hardcoded_password(self):
        """Kiểm tra phát hiện hardcoded password bằng regex pattern."""
        code = 'password = "secret"'
        matcher = VulnPatternMatcher()
        issues = matcher.match(code)
        self.assertTrue(any(i['type'] == 'Pattern Match' for i in issues))

    def test_pickle_import(self):
        """Kiểm tra phát hiện import pickle không an toàn."""
        code = 'import pickle'
        matcher = VulnPatternMatcher()
        issues = matcher.match(code)
        self.assertTrue(any(i['type'] == 'Pattern Match' for i in issues))

    def test_custom_pattern_extension(self):
        """Kiểm tra khả năng mở rộng pattern mới linh hoạt."""
        matcher = VulnPatternMatcher()
        matcher.add_pattern(r'api_key\s*=\s*".*"', "API key hardcoded.")
        code = 'api_key = "AIzaSyD-12345"'
        issues = matcher.match(code)
        self.assertTrue(any("API key hardcoded." in i['message'] for i in issues))

    def test_structural_pattern_matching(self):
        """Kiểm tra nhận diện mẫu cấu trúc qua AST Visitor."""
        code = "from pickle import loads\ndata = loads(b'abc')"
        matcher = VulnPatternMatcher()
        structural_issues = matcher.match_structural(code)
        self.assertTrue(any("pickle" in i['message'] for i in structural_issues))

    def test_safe_code_no_matches(self):
        """Kiểm tra code an toàn không kích hoạt pattern."""
        code = 'message = "Welcome to Cyber Security Lab"'
        matcher = VulnPatternMatcher()
        issues = matcher.match(code)
        self.assertEqual(len(issues), 0)


if __name__ == '__main__':
    unittest.main()
