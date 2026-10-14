from oauth_client.client import OAuthClient
import pytest

def test_auth_url_contains_parameters():
    client=OAuthClient('client_id','secret','https://auth.example/authorize','https://auth.example/token','http://localhost/callback')
    url=client.get_auth_url(state='random-state')
    assert url.startswith('https://auth.example/authorize?')
    assert 'client_id=client_id' in url and 'state=random-state' in url

def test_state_is_required():
    client=OAuthClient('id','secret','https://auth.example','https://token.example','http://localhost')
    with pytest.raises(ValueError): client.get_auth_url()
