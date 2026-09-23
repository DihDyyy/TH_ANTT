import os

from gitsecure import collect_findings, scan_sensitive


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_scan_sensitive_detects_api_key():
    file_path = os.path.join(BASE_DIR, "bad.py")
    result = scan_sensitive(file_path)
    assert result is not None
    assert "Sensitive info" in result


def test_scan_sensitive_allows_clean_file():
    file_path = os.path.join(BASE_DIR, "good.py")
    result = scan_sensitive(file_path)
    assert result is None


def test_collect_findings_detects_bad_file():
    file_path = os.path.join(BASE_DIR, "bad.py")
    findings = collect_findings([file_path])
    assert any("Sensitive info" in item for item in findings)
