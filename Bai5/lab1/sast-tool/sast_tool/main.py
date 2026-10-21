"""
Main - Điểm khởi chạy dòng lệnh (CLI) cho SAST Tool.
Tích hợp ASTAnalyzer, VulnPatternMatcher, CodeQualityChecker, SecurityRuleEngine và SarifReporter.
Chạy từ thư mục gốc: python -m sast_tool.main <file_to_analyze.py>
"""

import os
import sys
from typing import List, Dict, Any

from sast_tool.ast_analyzer import ASTAnalyzer
from sast_tool.vuln_pattern_matcher import VulnPatternMatcher
from sast_tool.security_rule_engine import SecurityRuleEngine
from sast_tool.code_quality_checker import CodeQualityChecker
from sast_tool.sarif_reporter import SarifReporter


# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def print_banner():
    print("=" * 68)
    print("      PYSAST - STATIC APPLICATION SECURITY TESTING TOOL (LAB 05)")
    print("=" * 68)


def display_terminal_summary(file_path: str, issues: List[Dict[str, Any]], metrics: Dict[str, Any]):
    """Display scan results clearly in the terminal."""
    print(f"\n[+] Analyzing file: {file_path}")
    print("-" * 68)
    print(f"{'LINE':<6} | {'SEVERITY':<8} | {'TYPE':<20} | {'MESSAGE'}")
    print("-" * 68)

    for issue in issues:
        lineno = issue.get('lineno', '?')
        severity = str(issue.get('severity', 'medium')).upper()
        issue_type = str(issue.get('type', 'Finding'))[:20]
        message = str(issue.get('message', ''))
        if len(message) > 55:
            message = message[:52] + "..."
        print(f"{str(lineno):<6} | {severity:<8} | {issue_type:<20} | {message}")

    print("-" * 68)
    print("[*] Code Quality Metrics:")
    print(f"  - LOC (Lines of Code)       : {metrics.get('loc', 0)}")
    print(f"  - Cyclomatic Complexity     : avg={metrics.get('cyclomatic_complexity', {}).get('average', 1.0)}, max={metrics.get('cyclomatic_complexity', {}).get('max', 1)}")
    print(f"  - Function Length           : avg={metrics.get('function_length', {}).get('average', 0.0)} lines, max={metrics.get('function_length', {}).get('max', 0)} lines")
    print(f"  - Nested Depth              : {metrics.get('nested_depth', 0)}")
    print(f"  - Dependency Count          : {metrics.get('dependency_count', 0)} ({', '.join(metrics.get('dependencies', [])) or 'None'})")
    print(f"  - Security Smell Density    : {metrics.get('security_smell_density_per_100_loc', 0.0)} smells / 100 LOC")
    print("-" * 68)


def main(file_path: str, full_mode: bool = False):
    """Hàm thực thi phân tích chính."""
    if not os.path.exists(file_path):
        print(f"[!] Lỗi: Tệp nguồn không tồn tại: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"[!] Lỗi khi đọc tệp {file_path}: {e}")
        sys.exit(1)

    # 1. Khởi tạo các module phân tích
    # full_mode: nếu True kích hoạt kiểm tra mở rộng (exec, os.system, credentials)
    ast_analyzer = ASTAnalyzer(detect_all=full_mode)
    pattern_matcher = VulnPatternMatcher()
    quality_checker = CodeQualityChecker()
    rule_engine = SecurityRuleEngine()

    # 2. Phân tích AST, Pattern và Linting
    ast_issues = ast_analyzer.analyze(code, filename=file_path)
    pattern_issues = pattern_matcher.match(code)
    quality_issues = quality_checker.check(file_path)
    metrics = quality_checker.compute_metrics(file_path)

    # 3. Đánh giá và lọc issue qua Rule Engine
    evaluated_security_issues = rule_engine.evaluate(ast_issues, pattern_issues)

    # 4. Gộp toàn bộ kết quả phát hiện
    final_issues = evaluated_security_issues + quality_issues

    # 5. Xuất báo cáo SARIF 2.1.0
    reporter = SarifReporter()
    reporter.generate_report(final_issues, output_file='report.sarif', analyzed_file=file_path)

    # 6. In bảng tổng kết và thông báo hoàn thành (khớp thông điệp chuẩn trong lab)
    display_terminal_summary(file_path, final_issues, metrics)
    print("Analysis complete.")
    print(f"Report saved to report.sarif with {len(final_issues)} issues.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m sast_tool.main <file_to_analyze.py> [--full]")
        sys.exit(1)

    target_file = sys.argv[1]
    is_full = "--full" in sys.argv
    main(target_file, full_mode=is_full)
