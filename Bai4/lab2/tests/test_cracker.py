from jwt_cracker.cracker import JWTCracker
import jwt

def test_crack_token_from_temporary_wordlist(tmp_path):
    secret='lab-secret'
    token=jwt.encode({'sub':'test'},secret,algorithm='HS256')
    wordlist=tmp_path/'words.txt'; wordlist.write_text('wrongpass\nlab-secret\n',encoding='utf-8')
    assert JWTCracker(token,str(wordlist)).crack()==secret
