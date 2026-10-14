"""Phát hiện endpoint có tham số URL đáng chú ý mà không gửi request tới mạng nội bộ."""
from urllib.parse import urlparse, parse_qsl
import requests

class SSRFTester:
    URL_KEYS={'url','uri','target','dest','destination','redirect','image','fetch','callback','webhook'}
    def __init__(self, timeout=8): self.timeout=timeout
    def scan(self, url):
        parsed=urlparse(url)
        params=dict(parse_qsl(parsed.query,keep_blank_values=True))
        findings=[]
        keys=[k for k in params if k.lower() in self.URL_KEYS]
        if keys:
            for key in keys:
                findings.append({'type':'Potential SSRF endpoint','parameter':key,'severity':'Medium',
                                 'evidence':'Endpoint nhận tham số có vẻ là URL; cần xác minh trong staging bằng callback do bạn kiểm soát.'})
        else:
            findings.append({'type':'No obvious URL parameter','severity':'Info',
                             'evidence':'Không thấy tham số URL phổ biến trong query string.'})
        # Chỉ GET trang mục tiêu đã cung cấp; không thay tham số bằng địa chỉ nội bộ.
        try:
            requests.get(url, timeout=self.timeout, allow_redirects=False)
        except requests.RequestException as exc:
            findings.append({'type':'Request error','severity':'Info','evidence':str(exc)})
        return findings
