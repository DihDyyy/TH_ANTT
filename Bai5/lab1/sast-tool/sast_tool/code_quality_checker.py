"""
CodeQualityChecker - Đánh giá chất lượng mã nguồn và rủi ro bảo mật.
Bao gồm tích hợp linter tĩnh (flake8) và tính toán 5 chỉ số chất lượng:
1. Cyclomatic Complexity
2. Function Length
3. Nested Depth
4. Dependency Count
5. Security Smell Density
"""

import ast
import os
import subprocess
import sys
from typing import List, Dict, Any, Union


class CodeQualityChecker:
    """
    Công cụ đánh giá chất lượng mã nguồn và các chỉ số liên quan đến bảo mật.
    
    LƯU Ý GIỚI HẠN KHOA HỌC:
    Các chỉ số trong module này được tính toán dựa trên giải thuật phỏng đoán (heuristics)
    ở cấp độ AST cơ bản cho mục đích học tập. Chúng KHÔNG hoàn toàn tương đương với
    các bộ đo chuẩn chuyên sâu của các hệ thống phân tích mã chuyên nghiệp (như SonarQube,
    Coverity hay CodeQL vốn có engine data-flow, taint-analysis và interprocedural analysis).
    """

    def check(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Chạy flake8 để tìm kiếm các lỗi quy chuẩn mã nguồn (PEP 8, unused imports, syntax issues).
        
        Args:
            filepath (str): Đường dẫn tới file Python cần kiểm tra.
            
        Returns:
            List[Dict[str, Any]]: Danh sách các lint issues tương thích format lab.
        """
        issues: List[Dict[str, Any]] = []
        if not os.path.exists(filepath):
            return issues

        try:
            # Ưu tiên gọi flake8 qua sys.executable để đảm bảo đúng virtualenv trên Windows
            cmd = [sys.executable, "-m", "flake8", filepath]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = result.stdout
        except Exception:
            try:
                # Fallback gọi trực tiếp flake8
                result = subprocess.run(["flake8", filepath], capture_output=True, text=True, check=False)
                output = result.stdout
            except Exception:
                output = ""

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) >= 4:
                try:
                    lineno = int(parts[1])
                    col_offset = int(parts[2])
                except ValueError:
                    continue
                issues.append({
                    'type': 'Lint Issue',
                    'message': line,
                    'lineno': lineno,
                    'col_offset': col_offset
                })
        return issues

    def compute_metrics(self, code_or_filepath: str) -> Dict[str, Any]:
        """
        Tính toán 5 chỉ số chất lượng mã nguồn từ file hoặc chuỗi code.
        
        Cách tính từng chỉ số:
        1. Cyclomatic Complexity (CC):
           Đếm số nhánh độc lập qua cấu trúc rẽ nhánh (If, For, While, Try, Except, BoolOp).
           CC = 1 + số_nhánh_điều_kiện cho mỗi hàm.
        2. Function Length:
           Độ dài từng hàm tính theo số dòng (end_lineno - lineno + 1).
        3. Nested Depth:
           Độ sâu lồng nhau tối đa của các khối lệnh điều khiển (If/For/While/Try/With).
        4. Dependency Count:
           Số lượng các thư viện/module bên ngoài được import.
        5. Security Smell Density:
           Tần suất xuất hiện của 'mùi bảo mật' (eval, exec, pickle, os.system) trên 100 LOC.
        """
        if os.path.exists(code_or_filepath):
            with open(code_or_filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        else:
            code = code_or_filepath

        lines = [line for line in code.splitlines() if line.strip() and not line.strip().startswith('#')]
        loc = max(1, len(lines))

        try:
            tree = ast.parse(code)
        except Exception:
            return {
                "loc": loc,
                "cyclomatic_complexity": {"average": 1.0, "max": 1},
                "function_length": {"average": 0.0, "max": 0},
                "nested_depth": 0,
                "dependency_count": 0,
                "security_smell_density": 0.0,
                "note": "Syntax error prevented complete AST metrics calculation"
            }

        # 1. Cyclomatic Complexity & 2. Function Length
        func_complexities = []
        func_lengths = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Function length
                end_lineno = getattr(node, 'end_lineno', node.lineno)
                length = end_lineno - node.lineno + 1
                func_lengths.append(length)

                # Cyclomatic complexity
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                func_complexities.append(complexity)

        avg_cc = (sum(func_complexities) / len(func_complexities)) if func_complexities else 1.0
        max_cc = max(func_complexities) if func_complexities else 1
        avg_len = (sum(func_lengths) / len(func_lengths)) if func_lengths else 0.0
        max_len = max(func_lengths) if func_lengths else 0

        # 3. Nested Depth
        def calc_depth(node: ast.AST, current_depth: int) -> int:
            nesting_nodes = (ast.If, ast.For, ast.While, ast.Try, ast.With)
            max_d = current_depth
            for child in ast.iter_child_nodes(node):
                child_depth = current_depth + (1 if isinstance(child, nesting_nodes) else 0)
                max_d = max(max_d, calc_depth(child, child_depth))
            return max_d

        max_depth = calc_depth(tree, 0)

        # 4. Dependency Count
        dependencies = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split('.')[0])
        dependency_count = len(dependencies)

        # 5. Security Smell Density
        smell_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in ("eval", "exec", "system", "popen"):
                    smell_count += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("pickle", "telnetlib"):
                            smell_count += 1
                elif node.module in ("pickle", "telnetlib"):
                    smell_count += 1

        smell_density = round((smell_count / loc) * 100, 2)

        return {
            "loc": loc,
            "cyclomatic_complexity": {
                "average": round(avg_cc, 2),
                "max": max_cc
            },
            "function_length": {
                "average": round(avg_len, 2),
                "max": max_len
            },
            "nested_depth": max_depth,
            "dependency_count": dependency_count,
            "dependencies": sorted(list(dependencies)),
            "security_smell_count": smell_count,
            "security_smell_density_per_100_loc": smell_density
        }
