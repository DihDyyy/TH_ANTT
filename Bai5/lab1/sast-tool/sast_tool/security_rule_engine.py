"""
SecurityRuleEngine - Quản lý, cấu hình và áp dụng các luật bảo mật.
Đọc các luật từ JSON, hỗ trợ bật/tắt luật, thêm luật động và gán mức độ nghiêm trọng.
"""

import json
import os
from typing import List, Dict, Any, Optional


class SecurityRuleEngine:
    """Động cơ luật bảo mật dựa trên tệp cấu hình JSON."""

    def __init__(self, rules_file: str = 'rules/default_rules.json'):
        """
        Khởi tạo động cơ luật bảo mật.
        
        Args:
            rules_file (str): Đường dẫn đến file JSON chứa danh sách luật.
        """
        self.rules_file = rules_file
        self.rules: List[Dict[str, Any]] = self._load_rules(rules_file)

    def _load_rules(self, rules_file: str) -> List[Dict[str, Any]]:
        """Đọc và kiểm tra tính hợp lệ của file luật JSON."""
        resolved_path = rules_file
        if not os.path.exists(resolved_path):
            # Thử tìm kiếm tương đối từ vị trí file hiện tại
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidate = os.path.join(base_dir, rules_file)
            if os.path.exists(candidate):
                resolved_path = candidate

        if not os.path.exists(resolved_path):
            # Nếu file không tồn tại, sử dụng luật dự phòng mặc định
            return [
                {"type": "Use of eval", "severity": "high", "enabled": True},
                {"type": "Use of exec", "severity": "high", "enabled": True},
                {"type": "Risky OS Command", "severity": "high", "enabled": True},
                {"type": "Hardcoded Credential", "severity": "medium", "enabled": True},
                {"type": "Pattern Match", "severity": "medium", "enabled": True},
                {"type": "Lint Issue", "severity": "low", "enabled": True}
            ]

        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Cấu hình rules phải là một danh sách JSON (list).")
                for rule in data:
                    if not isinstance(rule, dict) or 'type' not in rule:
                        raise ValueError(f"Luật không hợp lệ: {rule}")
                return data
        except Exception as e:
            raise RuntimeError(f"Không thể tải cấu hình luật từ '{rules_file}': {str(e)}")

    def add_rule(self, rule_type: str, severity: str = "medium", enabled: bool = True) -> None:
        """Thêm luật mới mà không cần sửa đổi mã nguồn chính."""
        self.rules.append({
            "type": rule_type,
            "severity": severity,
            "enabled": enabled
        })

    def evaluate(self, ast_issues: List[Dict[str, Any]], pattern_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Đánh giá các issue dựa trên tập luật đã cấu hình.
        Gán mức độ nghiêm trọng (severity) và lọc theo trạng thái bật/tắt của luật.
        
        Args:
            ast_issues: Danh sách issue từ ASTAnalyzer.
            pattern_issues: Danh sách issue từ VulnPatternMatcher.
            
        Returns:
            List[Dict[str, Any]]: Danh sách issue đã được gắn severity.
        """
        evaluated_issues: List[Dict[str, Any]] = []

        for issue in ast_issues + pattern_issues:
            for rule in self.rules:
                # Kiểm tra cờ bật/tắt (mặc định là True nếu không có trường 'enabled')
                if not rule.get('enabled', True):
                    continue

                if rule['type'] in issue['type']:
                    # Tạo bản sao issue và gán severity từ luật
                    matched_issue = dict(issue)
                    matched_issue['severity'] = rule.get('severity', 'medium')
                    evaluated_issues.append(matched_issue)
                    break  # Tránh gán trùng lặp nhiều lần cho cùng một issue

        return evaluated_issues
