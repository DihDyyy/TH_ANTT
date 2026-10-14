from scanners.ssrf_tester import SSRFTester

def test_url_parameter_detection():
    assert 'url' in SSRFTester.URL_KEYS
    assert 'callback' in SSRFTester.URL_KEYS
