import os
from api_gateway.gateway import APIGateway
from token_manager.manager import TokenManager

if __name__=='__main__':
    secret=os.environ.get('JWT_SECRET')
    if not secret or len(secret)<32:
        raise SystemExit('Hãy đặt biến môi trường JWT_SECRET có ít nhất 32 ký tự ngẫu nhiên.')
    manager=TokenManager(secret)
    access_token,refresh_token=manager.generate_tokens('student-demo')
    print('Access Token:',access_token)
    print('Refresh Token:',refresh_token)
    print('Chỉ dùng token demo trong lab; không commit token hoặc secret vào Git.')
    APIGateway(secret).run()
