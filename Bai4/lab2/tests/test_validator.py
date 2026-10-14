from jwt_validator.validator import JWTValidator
import jwt, datetime

def make_token(secret):
    now=datetime.datetime.now(datetime.timezone.utc)
    return jwt.encode({'sub':'test','iat':now,'exp':now+datetime.timedelta(minutes=5)},secret,algorithm='HS256')

def test_valid_token():
    token=make_token('secret123')
    result=JWTValidator('secret123').validate(token)
    assert result['valid'] is True and result['payload']['sub']=='test'

def test_invalid_signature():
    result=JWTValidator('correct-secret').validate(make_token('wrong-secret'))
    assert result['valid'] is False
