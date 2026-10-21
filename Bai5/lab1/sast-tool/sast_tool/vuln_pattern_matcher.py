"""
VulnPatternMatcher - Nhận diện mẫu mã nguy hiểm bằng kết hợp
Literal Pattern (Regex) và Structural Pattern (ast.NodeVisitor).
"""

import ast
import re
from typing import List, Dict, Any, Optional


class StructuralPatternVisitor(ast.NodeVisitor):
    """
    Duyệt cây AST để nhận diện mẫu cú pháp cấu trúc (Structural Pattern).
    Không chỉ tìm chuỗi thô mà phân tích quan hệ ngữ pháp giữa các node.
    """

    def __init__(self):
        self.findings: List[Dict[str, Any]] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name in ("pickle", "marshal", "shelve"):
                self.findings.append({
                    'type': 'Pattern Match',
                    'category': 'structural_import',
                    'message': f"Usage of serialization module '{alias.name}' can lead to unsafe deserialization.",
                    'lineno': node.lineno,
                    'col_offset': node.col_offset
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module in ("pickle", "marshal", "shelve"):
            self.findings.append({
                'type': 'Pattern Match',
                'category': 'structural_import',
                'message': f"Usage of serialization module '{node.module}' can lead to unsafe deserialization.",
                'lineno': node.lineno,
                'col_offset': node.col_offset
            })
        self.generic_visit(node)


class VulnPatternMatcher(ast.NodeVisitor):
    """
    Bộ so khớp mẫu lỗ hổng tùy biến kết hợp regex (literal pattern)
    và AST Visitor (structural pattern).
    """

    def __init__(self, custom_patterns: Optional[List[Dict[str, str]]] = None):
        super().__init__()
        # Literal patterns mặc định (tương thích trực tiếp với tài liệu Lab 05)
        self.patterns = [
            {'pattern': r'password\s*=\s*".*"', 'message': 'Hardcoded password detected.'},
            {'pattern': r'import\s+pickle', 'message': 'Usage of pickle module can be unsafe.'}
        ]
        if custom_patterns:
            self.patterns.extend(custom_patterns)

    def add_pattern(self, pattern: str, message: str) -> None:
        """Thêm pattern regex mới vào danh sách quy tắc."""
        self.patterns.append({'pattern': pattern, 'message': message})

    def match(self, code: str) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các mẫu nguy hiểm trong chuỗi mã nguồn Python.
        
        Args:
            code (str): Chuỗi mã nguồn.
            
        Returns:
            List[Dict[str, Any]]: Danh sách issue dạng 'Pattern Match'.
        """
        issues: List[Dict[str, Any]] = []

        # 1. So khớp mẫu dạng chuỗi/literal (Regex Pattern Matching)
        for p in self.patterns:
            for match_obj in re.finditer(p['pattern'], code):
                start = match_obj.start()
                lineno = code[:start].count('\n') + 1
                last_newline = code.rfind('\n', 0, start)
                col_offset = start if last_newline == -1 else start - last_newline - 1

                issues.append({
                    'type': 'Pattern Match',
                    'message': p['message'],
                    'lineno': lineno,
                    'col_offset': col_offset
                })

        return issues

    def match_structural(self, code: str) -> List[Dict[str, Any]]:
        """
        Duyệt mã nguồn bằng AST NodeVisitor để nhận diện các structural pattern.
        """
        try:
            tree = ast.parse(code)
            visitor = StructuralPatternVisitor()
            visitor.visit(tree)
            return visitor.findings
        except Exception:
            return []
