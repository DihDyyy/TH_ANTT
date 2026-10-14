from scanners.xss_scanner import XSSScanner

def test_payloads_are_non_executable_markers():
    scanner=XSSScanner()
    assert scanner.payloads
    assert all('script' not in p.lower() for p in scanner.payloads)
