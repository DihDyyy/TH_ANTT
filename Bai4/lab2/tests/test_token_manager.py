from token_manager.manager import TokenManager
import jwt

def test_token_creation_and_refresh_rotation():
    manager=TokenManager('secret123-at-least-32-characters')
    access,refresh=manager.generate_tokens('user1')
    payload=jwt.decode(access,manager.secret,algorithms=['HS256'])
    assert payload['sub']=='user1' and payload['type']=='access'
    new_pair=manager.refresh_access_token(refresh)
    assert new_pair is not None
    assert manager.refresh_access_token(refresh) is None
