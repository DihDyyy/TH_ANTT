from urllib.parse import urlencode
import requests

class OAuthClient:
    """OAuth 2.0 Authorization Code client helper; configure endpoints from your provider."""
    def __init__(self, client_id, client_secret, auth_url, token_url, redirect_uri):
        self.client_id=client_id; self.client_secret=client_secret
        self.auth_url=auth_url; self.token_url=token_url; self.redirect_uri=redirect_uri
    def get_auth_url(self, scope='openid', state=None):
        if not state: raise ValueError('Phải tạo và lưu state ngẫu nhiên để chống CSRF OAuth.')
        params={'response_type':'code','client_id':self.client_id,'redirect_uri':self.redirect_uri,'scope':scope,'state':state}
        return f'{self.auth_url}?{urlencode(params)}'
    def get_token(self, code, timeout=10):
        data={'grant_type':'authorization_code','code':code,'redirect_uri':self.redirect_uri,'client_id':self.client_id,'client_secret':self.client_secret}
        response=requests.post(self.token_url,data=data,timeout=timeout)
        response.raise_for_status(); return response.json()
