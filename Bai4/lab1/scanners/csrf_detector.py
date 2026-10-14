"""Kiểm tra tín hiệu phòng vệ CSRF cơ bản; kết quả cần được xác minh thủ công."""
import requests
from bs4 import BeautifulSoup

class CSRFDetector:
    TOKEN_NAMES=('csrf','xsrf','authenticity_token','_token','requestverificationtoken')
    def __init__(self, timeout=8): self.timeout=timeout
    def scan(self, url):
        findings=[]
        try:
            r=requests.get(url, timeout=self.timeout)
            soup=BeautifulSoup(r.text,'html.parser')
            forms=soup.find_all('form')
            for i, form in enumerate(forms,1):
                method=(form.get('method') or 'get').lower()
                if method not in ('post','put','patch','delete'): continue
                names=[(el.get('name') or '').lower() for el in form.find_all(['input','textarea'])]
                has_token=any(any(token in name for token in self.TOKEN_NAMES) for name in names)
                if not has_token:
                    findings.append({'type':'Potential missing CSRF token','form':i,
                                     'severity':'Medium','evidence':f'Form method={method.upper()} không thấy trường token CSRF.'})
            if not forms:
                findings.append({'type':'No HTML forms found','severity':'Info','evidence':'Không tìm thấy form HTML để kiểm tra.'})
        except requests.RequestException as exc:
            findings.append({'type':'Request error','severity':'Info','evidence':str(exc)})
        return findings
