import json
import os
import unittest
from sast_tool.security_rule_engine import SecurityRuleEngine


class TestSecurityRuleEngine(unittest.TestCase):
    def setUp(self):
        # Tạo file luật tạm thời cho unit test
        self.rules = [
            {"type": "Use of eval", "severity": "high"},
            {"type": "Pattern Match", "severity": "medium"}
        ]
        os.makedirs("rules", exist_ok=True)
        self.temp_rules_path = os.path.join("rules", "temp_rules.json")
        with open(self.temp_rules_path, "w", encoding='utf-8') as f:
            json.dump(self.rules, f)
        self.engine = SecurityRuleEngine(self.temp_rules_path)

    def tearDown(self):
        if os.path.exists(self.temp_rules_path):
            os.remove(self.temp_rules_path)

    def test_evaluate(self):
        """Kiểm tra đánh giá và gán severity theo cấu hình luật."""
        ast_issues = [{"type": "Use of eval", "message": "msg", "lineno": 1, "col_offset": 0}]
        pattern_issues = [{"type": "Pattern Match", "message": "msg", "lineno": 2, "col_offset": 1}]
        results = self.engine.evaluate(ast_issues, pattern_issues)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['severity'], "high")
        self.assertEqual(results[1]['severity'], "medium")

    def test_add_rule_dynamically(self):
        """Kiểm tra tính năng mở rộng thêm luật mới mà không cần sửa code gốc."""
        self.engine.add_rule(rule_type="Custom Vulnerability", severity="critical")
        custom_issues = [{"type": "Custom Vulnerability", "message": "custom detected", "lineno": 5, "col_offset": 2}]
        results = self.engine.evaluate([], custom_issues)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['severity'], "critical")

    def test_disable_rule(self):
        """Kiểm tra tắt luật (enabled=False) thì issue không bị gắn cờ."""
        self.engine.rules.append({"type": "Disabled Rule", "severity": "low", "enabled": False})
        issues = [{"type": "Disabled Rule", "message": "should be ignored", "lineno": 3, "col_offset": 0}]
        results = self.engine.evaluate(issues, [])
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
