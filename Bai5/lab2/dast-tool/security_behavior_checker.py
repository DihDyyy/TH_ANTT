"""
SecurityBehaviorChecker - Phân tích hành vi bảo mật động (Dynamic Behavioral Analysis).
Sử dụng phương pháp tiếp cận Rule-based kết hợp Heuristic để đánh giá các hành vi
nghi vấn trong lúc thực thi và phân loại mức độ cảnh báo.
"""

import os
from typing import List, Dict, Any, Optional


class SecurityBehaviorChecker:
    """
    Bộ kiểm tra và đánh giá hành vi bảo mật runtime.
    
    NGUYÊN TẮC PHÂN TÍCH AN TOÀN:
    1. Không khẳng định mã độc đơn phương:
       Một dấu hiệu đơn lẻ (như CPU tăng cao đột ngột hoặc mở socket) chưa đủ để kết luận
       tiến trình là mã độc. Hệ thống đưa ra cảnh báo để hỗ trợ chuyên viên phân tích.
    2. Phân biệt môi trường thực thi và mô phỏng:
       Các dấu hiệu kiểm tra chuỗi (như suspicious_calls) là kiểm tra phát hiện mẫu tĩnh/mô phỏng,
       trong khi evaluate_runtime_events phân tích dựa trên dữ liệu động thu thập được từ OS.
    """

    def suspicious_calls(self, target_filepath: Optional[str] = None) -> List[str]:
        """
        Kiểm tra sự xuất hiện của các lời gọi nhạy cảm (os.system, eval, exec).
        Giữ nguyên tương thích với mã nguồn bài thực hành Lab 05.
        
        Args:
            target_filepath: File cần kiểm tra, mặc định kiểm tra chính file hiện hành.
            
        Returns:
            List[str]: Danh sách tên các lời gọi nghi vấn phát hiện được.
        """
        suspicious: List[str] = []
        syscalls = ["os.system", "eval", "exec"]
        file_to_check = target_filepath or __file__
        try:
            with open(file_to_check, 'r', encoding='utf-8') as f:
                content = f.read()
                for call in syscalls:
                    if call in content:
                        suspicious.append(call)
        except Exception:
            pass
        return suspicious

    def evaluate_runtime_events(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Đánh giá các chỉ số runtime theo luật để phát hiện hành vi bất thường.
        
        Args:
            metrics (Dict[str, Any]): Dữ liệu runtime gồm cpu_percent, memory_rss, connections_count, open_files_count.
            
        Returns:
            List[Dict[str, Any]]: Danh sách cảnh báo có phân cấp mức độ (HIGH, MEDIUM, LOW).
        """
        alerts: List[Dict[str, Any]] = []

        # Luật 1: Kiểm tra CPU bất thường (nghi ngờ DoS hoặc Crypto Mining cục bộ)
        cpu = metrics.get("cpu_percent", 0.0)
        if cpu > 85.0:
            alerts.append({
                "level": "HIGH",
                "category": "CPU_ANOMALY",
                "reason": f"Tỷ lệ sử dụng CPU đạt {cpu:.1f}%, vượt ngưỡng an toàn (85%).",
                "event_data": {"cpu_percent": cpu}
            })
        elif cpu > 50.0:
            alerts.append({
                "level": "MEDIUM",
                "category": "HIGH_CPU_ACTIVITY",
                "reason": f"CPU tăng cao ({cpu:.1f}%), cần theo dõi thêm tiến trình.",
                "event_data": {"cpu_percent": cpu}
            })

        # Luật 2: Kiểm tra số lượng kết nối mạng mở bất thường
        conn_count = metrics.get("connections_count", 0)
        if conn_count > 50:
            alerts.append({
                "level": "HIGH",
                "category": "NETWORK_BURST",
                "reason": f"Số lượng kết nối mạng ngoại vi cao bất thường ({conn_count} sockets).",
                "event_data": {"connections_count": conn_count}
            })

        # Luật 3: Kiểm tra hành vi mở quá nhiều tệp tin
        files_count = metrics.get("open_files_count", 0)
        if files_count > 100:
            alerts.append({
                "level": "MEDIUM",
                "category": "HIGH_FILE_DESCRIPTORS",
                "reason": f"Tiến trình đang mở đồng thời {files_count} tệp tin, có thể gây kiệt quệ tài nguyên.",
                "event_data": {"open_files_count": files_count}
            })

        # Luật 4: Cảnh báo từ bộ phân tích bộ nhớ
        if metrics.get("memory_alert", False):
            alerts.append({
                "level": "MEDIUM",
                "category": "MEMORY_LEAK_SUSPICION",
                "reason": metrics.get("memory_message", "Nghi ngờ rò rỉ bộ nhớ qua các chu kỳ lấy mẫu."),
                "event_data": {"growth_percent": metrics.get("memory_growth_percent", 0.0)}
            })

        return alerts
