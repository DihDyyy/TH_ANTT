"""Kiểm tra phản hồi phản chiếu payload XSS vô hại trên ứng dụng được phép test."""
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import requests

class XSSScanner:
    def __init__(self, timeout=8):
        self.timeout = timeout
        self.payloads = ['<xss-test-marker>', '"xss-test-marker"', "'xss-test-marker'"]

    def scan(self, url, params=None):
        """Gửi marker không thực thi JavaScript; phát hiện marker phản chiếu chưa encode."""
        findings = []
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.update(params or {})
        if not query:
            query = {'q': ''}
        for key in list(query):
            for payload in self.payloads:
                test_params = dict(query)
                test_params[key] = payload
                try:
                    response = requests.get(urlunparse(parsed._replace(query='')),
                                            params=test_params, timeout=self.timeout)
                    raw_reflected = payload in response.text
                    encoded_reflected = ('&lt;' in response.text and 'xss-test-marker' in response.text)
                    if raw_reflected:
                        findings.append({'type':'Potential Reflected XSS', 'parameter':key,
                                         'payload':payload, 'url':response.url,
                                         'severity':'Medium',
                                         'evidence':'Marker xuất hiện nguyên dạng trong response.'})
                        break
                    if encoded_reflected:
                        # Marker đã được encode là tín hiệu tốt, không ghi nhận là lỗ hổng.
                        continue
                except requests.RequestException as exc:
                    findings.append({'type':'Request error','parameter':key,'severity':'Info','evidence':str(exc)})
                    break
        return findings
