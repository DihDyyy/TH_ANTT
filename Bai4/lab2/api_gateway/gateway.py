from flask import Flask, request, jsonify
import jwt

class APIGateway:
    def __init__(self, secret, algorithm='HS256'):
        self.secret=secret; self.algorithm=algorithm; self.app=Flask(__name__); self.routes()
    def routes(self):
        @self.app.get('/health')
        def health(): return jsonify({'status':'ok'})
        @self.app.get('/protected')
        def protected():
            header=request.headers.get('Authorization','')
            if not header.startswith('Bearer '): return jsonify({'message':'Access denied'}),401
            token=header[7:].strip()
            try:
                payload=jwt.decode(token,self.secret,algorithms=[self.algorithm],options={'require':['exp','sub']})
                if payload.get('type','access')!='access': return jsonify({'message':'Access token required'}),401
                return jsonify({'message':'Access granted','user':payload['sub']})
            except jwt.PyJWTError:
                return jsonify({'message':'Access denied'}),401
    def run(self): self.app.run(host='127.0.0.1',port=5000,debug=False)
