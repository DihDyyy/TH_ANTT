"""Wordlist checker for locally generated lab JWTs only."""
import jwt
from concurrent.futures import ThreadPoolExecutor

class JWTCracker:
    def __init__(self, token, wordlist_path): self.token=token; self.wordlist_path=wordlist_path
    def _try_secret(self, secret):
        secret=secret.strip()
        if not secret: return None
        try:
            jwt.decode(self.token,secret,algorithms=['HS256'],options={'verify_exp':False})
            return secret
        except jwt.PyJWTError: return None
    def crack(self):
        with open(self.wordlist_path,'r',encoding='utf-8',errors='ignore') as f: secrets=[x.strip() for x in f if x.strip()]
        with ThreadPoolExecutor(max_workers=4) as executor:
            for result in executor.map(self._try_secret,secrets):
                if result: return result
        return None
