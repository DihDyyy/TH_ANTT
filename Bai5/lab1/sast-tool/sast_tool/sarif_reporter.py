"""
SarifReporter - Xuất báo cáo kết quả phân tích theo chuẩn OASIS SARIF 2.1.0.
Hỗ trợ mở trực tiếp bằng SARIF Viewer trong Visual Studio Code và các hệ thống CI/CD.
"""

import json
from typing import List, Dict, Any

try:
    from sarif_om import (
        SarifLog, Run, Tool, ToolComponent, Result, Message,
        ArtifactLocation, Location, PhysicalLocation, Region
    )
    import jsonpickle
    SARIF_OM_AVAILABLE = True
except ImportError:
    SARIF_OM_AVAILABLE = False


class SarifReporter:
    """Bộ tạo báo cáo bảo mật chuẩn SARIF 2.1.0 (Static Analysis Results Interchange Format)."""

    SEVERITY_TO_LEVEL = {
        'high': 'error',
        'critical': 'error',
        'medium': 'warning',
        'low': 'note',
        'info': 'note'
    }

    def generate_report(self, issues: List[Dict[str, Any]], output_file: str = 'report.sarif', analyzed_file: str = "input.py") -> str:
        """
        Sinh file SARIF 2.1.0 từ danh sách issue.
        
        Args:
            issues (List[Dict[str, Any]]): Danh sách các phát hiện bảo mật và chất lượng code.
            output_file (str): Tên file đích cần lưu (mặc định 'report.sarif').
            analyzed_file (str): Đường dẫn file được phân tích.
            
        Returns:
            str: Đường dẫn file SARIF đã được ghi thành công.
        """
        if SARIF_OM_AVAILABLE:
            results = []
            for i in issues:
                rule_id = i.get('rule_id', i.get('type', 'SEC-001'))
                severity = i.get('severity', 'medium').lower()
                level = self.SEVERITY_TO_LEVEL.get(severity, 'warning')
                line = max(1, int(i.get('lineno', 1)))
                col = max(1, int(i.get('col_offset', 0)) + 1)

                result = Result(
                    rule_id=rule_id,
                    level=level,
                    message=Message(text=str(i.get('message', 'Issue detected'))),
                    locations=[Location(
                        physical_location=PhysicalLocation(
                            artifact_location=ArtifactLocation(uri=analyzed_file),
                            region=Region(
                                start_line=line,
                                start_column=col
                            )
                        )
                    )]
                )
                results.append(result)

            run = Run(
                tool=Tool(driver=ToolComponent(name="PySAST", version="1.0.0")),
                results=results
            )
            log = SarifLog(
                schema_uri="https://json.schemastore.org/sarif-2.1.0.json",
                version="2.1.0",
                runs=[run]
            )

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(jsonpickle.encode(log, unpicklable=False, indent=2))
        else:
            # Fallback tạo cấu trúc SARIF 2.1.0 thuần định dạng JSON chuẩn
            results_data = []
            for i in issues:
                severity = i.get('severity', 'medium').lower()
                level = self.SEVERITY_TO_LEVEL.get(severity, 'warning')
                line = max(1, int(i.get('lineno', 1)))
                col = max(1, int(i.get('col_offset', 0)) + 1)
                rule_id = i.get('rule_id', i.get('type', 'SEC-001'))

                results_data.append({
                    "ruleId": rule_id,
                    "level": level,
                    "message": {"text": str(i.get('message', 'Issue detected'))},
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": analyzed_file},
                            "region": {
                                "startLine": line,
                                "startColumn": col
                            }
                        }
                    }]
                })

            sarif_data = {
                "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "PySAST",
                                "version": "1.0.0",
                                "informationUri": "https://github.com/DihDyyy/TH_ANTT"
                            }
                        },
                        "results": results_data
                    }
                ]
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sarif_data, f, indent=2, ensure_ascii=False)

        return output_file
