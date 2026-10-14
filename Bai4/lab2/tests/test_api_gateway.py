from api_gateway.gateway import APIGateway
from token_manager.manager import TokenManager
import pytest

@pytest.fixture
def client():
    secret='test-secret-at-least-32-characters-long'
    gateway=APIGateway(secret); gateway.app.config['TESTING']=True
    return gateway.app.test_client(),TokenManager(secret)

def test_protected_route_with_valid_token(client):
    test_client,manager=client; access,_=manager.generate_tokens('tester')
    response=test_client.get('/protected',headers={'Authorization':f'Bearer {access}'})
    assert response.status_code==200
    assert response.json['user']=='tester'

def test_protected_route_with_invalid_token(client):
    test_client,_=client
    assert test_client.get('/protected',headers={'Authorization':'Bearer invalid'}).status_code==401
