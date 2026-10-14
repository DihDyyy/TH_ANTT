"""Kiểm tra dấu hiệu SQLi bằng các probe lỗi không phá hoại.
Không tự động trích xuất dữ liệu hay chạy payload trì hoãn.
"""
import requests
from urllib.parse import urlparse, parse_qsl, urlunparse

class SQLInjectionTester:
    ERROR_MARKERS = ('sql syntax', 'sqlite error', 'mysql_fetch', 'postgresql',
                     'odbc sql', 'unclosed quotation', 'ora-00933', 'sqlstate')
    PROBES = ("'", '"', "')")

    def __init__(self, timeout=8): self.timeout = timeout

    def scan(self, url, params=None):
        parsed=urlparse(url); base=urlunparse(parsed._replace(query=''))
        query=dict(parse_qsl(parsed.query, keep_blank_values=True)); query.update(params or {})
        if not query: query={'id':'1'}
        findings=[]
        for key, original in query.items():
            for probe in self.PROBES:
                test=dict(query); test[key]=str(original)+probe
                try:
                    resp=requests.get(base, params=test, timeout=self.timeout)
                    body=resp.text.lower()
                    marker=next((m for m in self.ERROR_MARKERS if m in body), None)
                    if marker:
                        findings.append({'type':'Potential SQL Injection','parameter':key,
                                         'severity':'High','evidence':f'Phản hồi chứa dấu hiệu lỗi DB: {marker}',
                                         'url':resp.url})
                        break
                except requests.RequestException as exc:
                    findings.append({'type':'Request error','parameter':key,'severity':'Info','evidence':str(exc)})
                    break
        return findings
