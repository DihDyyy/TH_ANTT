import jwt, datetime, secrets

class TokenManager:
    def __init__(self, secret, algorithm='HS256', access_exp=15, refresh_exp=60*24):
        self.secret=secret; self.algorithm=algorithm; self.access_exp=access_exp; self.refresh_exp=refresh_exp
        self.revoked_refresh_tokens=set()
    def _generate(self,payload,minutes):
        now=datetime.datetime.now(datetime.timezone.utc)
        claims=dict(payload); claims['iat']=now; claims['exp']=now+datetime.timedelta(minutes=minutes)
        return jwt.encode(claims,self.secret,algorithm=self.algorithm)
    def generate_tokens(self,user_id):
        access=self._generate({'sub':user_id,'type':'access'},self.access_exp)
        refresh=self._generate({'sub':user_id,'type':'refresh','jti':secrets.token_urlsafe(16)},self.refresh_exp)
        return access,refresh
    def refresh_access_token(self,refresh_token):
        if refresh_token in self.revoked_refresh_tokens: return None
        try:
            payload=jwt.decode(refresh_token,self.secret,algorithms=[self.algorithm],options={'require':['exp','sub','jti','type']})
            if payload.get('type')!='refresh': return None
            # Rotation: revoke the old refresh token and issue a new pair.
            self.revoked_refresh_tokens.add(refresh_token)
            return self.generate_tokens(payload['sub'])
        except jwt.PyJWTError: return None
    def revoke_refresh_token(self,refresh_token): self.revoked_refresh_tokens.add(refresh_token)
