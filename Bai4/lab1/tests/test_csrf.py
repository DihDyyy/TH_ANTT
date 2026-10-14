from scanners.csrf_detector import CSRFDetector

def test_common_token_names():
    assert 'csrf' in CSRFDetector.TOKEN_NAMES
    assert '_token' in CSRFDetector.TOKEN_NAMES
