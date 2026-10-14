from scanners.sql_injection_tester import SQLInjectionTester

def test_probe_set_is_small_and_non_destructive():
    assert "'" in SQLInjectionTester.PROBES
    assert not any('sleep(' in p.lower() or 'union select' in p.lower() for p in SQLInjectionTester.PROBES)
