import argparse
from urllib.parse import urlparse
from scanners.xss_scanner import XSSScanner
from scanners.sql_injection_tester import SQLInjectionTester
from scanners.csrf_detector import CSRFDetector
from scanners.ssrf_tester import SSRFTester
from report.report_generator import ReportGenerator

def validate_target(url):
    p=urlparse(url)
    if p.scheme not in ('http','https') or not p.netloc:
        raise ValueError('URL phải bắt đầu bằng http:// hoặc https://')
    return url

def run_scan(url):
    validate_target(url)
    results=[]
    for scanner_name, scanner in [
        ('XSS', XSSScanner()), ('SQLi', SQLInjectionTester()),
        ('CSRF', CSRFDetector()), ('SSRF', SSRFTester())]:
        if scanner_name=='CSRF': findings=scanner.scan(url)
        elif scanner_name=='SSRF': findings=scanner.scan(url)
        else: findings=scanner.scan(url)
        for f in findings:
            f['scanner']=scanner_name; results.append(f)
    report_path=ReportGenerator().generate(url,results)
    return results, report_path

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Web vulnerability scanner for authorized testing')
    parser.add_argument('url',help='URL thuộc hệ thống bạn được phép kiểm thử')
    args=parser.parse_args()
    try:
        findings,path=run_scan(args.url)
        print(f'Đã hoàn tất. Số kết quả: {len(findings)}')
        for item in findings: print(f"[{item.get('severity','Info')}] {item.get('scanner','')} - {item.get('type')}: {item.get('evidence','')}")
        print('Báo cáo:',path)
    except ValueError as exc: print('Lỗi:',exc)
