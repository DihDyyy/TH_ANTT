import json
from datetime import datetime, timezone
from pathlib import Path

class ReportGenerator:
    def generate(self, target, results, output_dir='reports'):
        out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
        report={'target':target,'generated_at':datetime.now(timezone.utc).isoformat(),
                'summary':{'total_findings':len(results),'by_severity':{}},'findings':results}
        for item in results:
            sev=item.get('severity','Info'); report['summary']['by_severity'][sev]=report['summary']['by_severity'].get(sev,0)+1
        path=out / ('report_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        return str(path)
