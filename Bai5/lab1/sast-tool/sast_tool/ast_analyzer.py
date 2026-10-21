"""
ASTAnalyzer - Phân tích mã nguồn tĩnh sử dụng Python Abstract Syntax Tree (AST).
Phát hiện các lời gọi hàm nguy hiểm (eval, exec, os.system), hard-coded credentials,
và xử lý lỗi cú pháp an toàn mà không thực thi mã nguồn.
"""

import ast
from typing import List, Dict, Any, Optional


class ASTAnalyzer:
    """Bộ phân tích AST phát hiện lỗ hổng bảo mật cấp độ cú pháp."""

    def __init__(self, detect_all: bool = True):
        """
        Khởi tạo ASTAnalyzer.
        
        Args:
            detect_all (bool): Nếu True, kiểm tra đầy đủ eval, exec, os.system, credentials.
                               Nếu False (chế độ lab tương thích), chỉ kiểm tra eval.
        """
        self.detect_all = detect_all

    def analyze(self, code: str, filename: str = "input.py") -> List[Dict[str, Any]]:
        """
        Phân tích chuỗi mã nguồn Python bằng AST.
        
        Args:
            code (str): Nội dung mã nguồn Python cần phân tích.
            filename (str): Tên file nguồn (phục vụ báo cáo vị trí).
            
        Returns:
            List[Dict[str, Any]]: Danh sách các issue bảo mật phát hiện được.
        """
        issues: List[Dict[str, Any]] = []

        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            issues.append({
                'type': 'Syntax Error',
                'rule_id': 'SEC-AST-000',
                'severity': 'high',
                'message': f"Lỗi cú pháp không thể phân tích: {e.msg}",
                'lineno': e.lineno or 1,
                'col_offset': e.offset or 0,
                'filename': filename
            })
            return issues
        except Exception as e:
            issues.append({
                'type': 'Parse Error',
                'rule_id': 'SEC-AST-ERR',
                'severity': 'medium',
                'message': f"Lỗi đọc AST: {str(e)}",
                'lineno': 1,
                'col_offset': 0,
                'filename': filename
            })
            return issues

        # Duyệt cây AST để phát hiện các mẫu rủi ro
        for node in ast.walk(tree):
            # 1. Phát hiện lời gọi hàm (ast.Call)
            if isinstance(node, ast.Call):
                func_id = ""
                # Trường hợp gọi hàm trực tiếp: eval(), exec()
                if isinstance(node.func, ast.Name):
                    func_id = node.func.id
                    if func_id == 'eval':
                        issues.append({
                            'type': 'Use of eval',
                            'rule_id': 'SEC-AST-001',
                            'severity': 'high',
                            'message': 'Use of eval() is dangerous and should be avoided.',
                            'lineno': node.lineno,
                            'col_offset': node.col_offset,
                            'filename': filename
                        })
                    elif self.detect_all and func_id == 'exec':
                        issues.append({
                            'type': 'Use of exec',
                            'rule_id': 'SEC-AST-002',
                            'severity': 'high',
                            'message': 'Use of exec() is dangerous and allows arbitrary statement execution.',
                            'lineno': node.lineno,
                            'col_offset': node.col_offset,
                            'filename': filename
                        })

                # Trường hợp gọi thuộc tính: os.system(), subprocess.run/call/Popen
                elif self.detect_all and isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    obj_name = getattr(node.func.value, 'id', '')
                    if obj_name == 'os' and attr_name in ('system', 'popen', 'spawnl', 'spawnlp', 'execv'):
                        issues.append({
                            'type': 'Risky OS Command',
                            'rule_id': 'SEC-AST-003',
                            'severity': 'high',
                            'message': f"Dangerous OS command execution via os.{attr_name}() detected.",
                            'lineno': node.lineno,
                            'col_offset': node.col_offset,
                            'filename': filename
                        })
                    elif obj_name == 'subprocess' and attr_name in ('Popen', 'call', 'run', 'check_output'):
                        # Kiểm tra xem có shell=True không
                        has_shell = any(
                            isinstance(kw, ast.keyword) and kw.arg == 'shell' and getattr(kw.value, 'value', False) is True
                            for kw in node.keywords
                        )
                        if has_shell:
                            issues.append({
                                'type': 'Risky OS Command',
                                'rule_id': 'SEC-AST-003-SHELL',
                                'severity': 'high',
                                'message': f"Subprocess invocation '{obj_name}.{attr_name}' with shell=True is risky.",
                                'lineno': node.lineno,
                                'col_offset': node.col_offset,
                                'filename': filename
                            })

            # 2. Phát hiện Hardcoded Credentials thông qua gán biến (ast.Assign)
            if self.detect_all and isinstance(node, ast.Assign):
                secret_keywords = {'password', 'passwd', 'secret_key', 'api_token', 'private_key'}
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        target_lower = target.id.lower()
                        # Chỉ kiểm tra các tên biến đặc thù xác thực để tránh trùng với regex nếu tên là password
                        if target_lower in secret_keywords and target_lower != 'password':
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                issues.append({
                                    'type': 'Hardcoded Credential',
                                    'rule_id': 'SEC-AST-004',
                                    'severity': 'medium',
                                    'message': f"Hardcoded credential detected in variable '{target.id}'.",
                                    'lineno': node.lineno,
                                    'col_offset': node.col_offset,
                                    'filename': filename
                                })

        return issues

    def analyze_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Đọc và phân tích trực tiếp từ đường dẫn file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.analyze(code, filename=filepath)
        except FileNotFoundError:
            return [{
                'type': 'File Error',
                'rule_id': 'SEC-AST-IO',
                'severity': 'high',
                'message': f"File không tồn tại: {filepath}",
                'lineno': 1,
                'col_offset': 0,
                'filename': filepath
            }]
        except Exception as e:
            return [{
                'type': 'File Error',
                'rule_id': 'SEC-AST-IO',
                'severity': 'high',
                'message': f"Không thể đọc file {filepath}: {str(e)}",
                'lineno': 1,
                'col_offset': 0,
                'filename': filepath
            }]
