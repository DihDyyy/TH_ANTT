import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError

class JWTValidator:
    def __init__(self, secret, algorithms=None):
        self.secret=secret; self.algorithms=algorithms or ['HS256']
    def validate(self, token):
        try:
            payload=jwt.decode(token,self.secret,algorithms=self.algorithms,options={'require':['exp','sub']})
            return {'valid':True,'payload':payload}
        except ExpiredSignatureError: return {'valid':False,'reason':'Token expired'}
        except InvalidSignatureError: return {'valid':False,'reason':'Invalid signature'}
        except InvalidTokenError as exc: return {'valid':False,'reason':str(exc)}
