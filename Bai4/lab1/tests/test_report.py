import json
from report.report_generator import ReportGenerator

def test_report_generation(tmp_path):
    path=ReportGenerator().generate('https://example.test',[{'type':'demo','severity':'Low'}],tmp_path)
    data=json.loads(open(path,encoding='utf-8').read())
    assert data['target']=='https://example.test'
    assert data['summary']['total_findings']==1
