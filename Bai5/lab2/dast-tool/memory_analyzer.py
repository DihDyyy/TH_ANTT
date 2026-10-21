"""
MemoryAnalyzer - Giám sát và phân tích hành vi sử dụng bộ nhớ tiến trình.
Phát hiện các đối tượng không thể thu hồi rác (uncollectable garbage),
kiểm tra giới hạn tràn số nguyên (integer overflow simulation),
và theo dõi xu hướng tăng trưởng bộ nhớ (memory growth trend analysis).
"""

import gc
from typing import List, Dict, Any, Optional


class MemoryAnalyzer:
    """
    Bộ phân tích bộ nhớ động (Dynamic Memory Analyzer).
    
    LƯU Ý BẢO MẬT VÀ GIỚI HẠN KHOA HỌC:
    1. Giới hạn suy luận Memory Leak:
       Chỉ số Resident Set Size (RSS) thu được từ hệ điều hành phản ánh toàn bộ các trang nhớ
       đang được ánh xạ trong RAM. Trong Python, cơ chế cấp phát bộ nhớ (pymalloc / arena)
       thường không trả ngay bộ nhớ cho hệ điều hành ngay cả khi các đối tượng đã được thu hồi.
       Do đó, mức RSS tăng không phải lúc nào cũng là lỗi rò rỉ bộ nhớ (memory leak) thực sự.
    2. Giới hạn phát hiện Buffer Overflow:
       Việc kiểm tra tràn số (overflow) ở đây chỉ là mô phỏng ngưỡng số học 64-bit có dấu.
       Python 3 tự động chuyển đổi số nguyên sang độ dài tùy ý (arbitrary-precision integer),
       nên không bao giờ xảy ra tràn buffer ở cấp độ ngôn ngữ thuần Python.
       Để phát hiện tràn buffer thực thụ trong mã C/C++, cần dùng AddressSanitizer (ASan)
       hoặc Valgrind, chứ không thể chỉ đo đạc RSS của tiến trình.
    """

    def __init__(self):
        self.memory_history: List[int] = []

    def check_memory_leaks(self) -> List[Any]:
        """
        Kiểm tra rò rỉ bộ nhớ thông qua Garbage Collector của Python.
        Phát hiện các đối tượng nằm trong chu trình tham chiếu vòng (circular reference)
        và có định nghĩa phương thức __del__ dẫn đến gc không thể tự động giải phóng.
        """
        gc.collect()
        leaks = [obj for obj in gc.garbage if hasattr(obj, '__del__')]
        return leaks

    def check_overflow(self, value: Any) -> bool:
        """
        Kiểm tra giá trị số nguyên có vượt quá ngưỡng giới hạn 64-bit có dấu (2^63) hay không.
        
        Args:
            value: Giá trị số cần kiểm tra.
            
        Returns:
            bool: True nếu giá trị là số nguyên và vượt quá 2^63.
        """
        try:
            if isinstance(value, int) and abs(value) > 2**63:
                return True
        except Exception:
            return False
        return False

    def record_sample(self, rss_bytes: int) -> None:
        """Ghi nhận một mẫu giá trị Resident Set Size (RSS) theo thời gian."""
        self.memory_history.append(rss_bytes)

    def analyze_trend(self, threshold_growth_percent: float = 30.0) -> Dict[str, Any]:
        """
        Phân tích xu hướng tăng trưởng bộ nhớ giữa các lần lấy mẫu.
        
        Args:
            threshold_growth_percent: Ngưỡng phần trăm tăng trưởng để phát cảnh báo.
            
        Returns:
            Dict[str, Any]: Thống kê xu hướng bộ nhớ và cảnh báo rò rỉ tiềm ẩn.
        """
        if len(self.memory_history) < 2:
            return {
                "samples_count": len(self.memory_history),
                "trend": "INSUFFICIENT_DATA",
                "alert": False,
                "message": "Cần tối thiểu 2 mẫu để phân tích xu hướng."
            }

        first_sample = self.memory_history[0]
        latest_sample = self.memory_history[-1]
        growth_bytes = latest_sample - first_sample
        growth_percent = ((growth_bytes / first_sample) * 100.0) if first_sample > 0 else 0.0

        is_alert = growth_percent >= threshold_growth_percent

        return {
            "samples_count": len(self.memory_history),
            "initial_rss_bytes": first_sample,
            "latest_rss_bytes": latest_sample,
            "growth_bytes": growth_bytes,
            "growth_percent": round(growth_percent, 2),
            "alert": is_alert,
            "message": (
                f"CẢNH BÁO: Bộ nhớ RSS tăng {growth_percent:.1f}%, nghi ngờ rò rỉ tài nguyên."
                if is_alert else "Mức tiêu thụ bộ nhớ ổn định trong ngưỡng cho phép."
            )
        }
