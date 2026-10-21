"""
RuntimeMonitor - Giám sát tiến trình và tài nguyên hệ thống theo thời gian thực.
Theo dõi CPU, bộ nhớ (RSS), danh sách tệp mở, xử lý an toàn lỗi quyền truy cập
(AccessDenied) và tiến trình đã kết thúc (NoSuchProcess).
"""

import time
from typing import List, Dict, Any, Optional
import psutil


class RuntimeMonitor:
    """Bộ giám sát hành vi thực thi của tiến trình (Process Runtime Monitor)."""

    def __init__(self, pid: int):
        """
        Khởi tạo bộ giám sát cho một PID cụ thể.
        
        Args:
            pid (int): Mã định danh tiến trình cần theo dõi.
        """
        self.pid = pid
        try:
            self.process = psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.process = None

    def is_running(self) -> bool:
        """Kiểm tra tiến trình còn đang hoạt động hay không."""
        if not self.process:
            return False
        try:
            return self.process.is_running() and self.process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def get_cpu_usage(self, interval: float = 1.0) -> float:
        """
        Lấy tỷ lệ sử dụng CPU của tiến trình (%) trong khoảng thời gian interval.
        """
        if not self.is_running():
            return 0.0
        try:
            return float(self.process.cpu_percent(interval=interval))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def get_memory_usage(self) -> int:
        """
        Lấy lượng bộ nhớ RAM vật lý (RSS - Resident Set Size) mà tiến trình đang chiếm dụng (bytes).
        """
        if not self.is_running():
            return 0
        try:
            return int(self.process.memory_info().rss)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0

    def get_open_files(self) -> List[Any]:
        """
        Lấy danh sách các file mà tiến trình đang mở.
        Bảo vệ an toàn trước ngoại lệ AccessDenied trên Windows.
        """
        if not self.is_running():
            return []
        try:
            return self.process.open_files()
        except (psutil.AccessDenied, PermissionError):
            # Trên Windows, đọc open_files của một số tệp hệ thống có thể bị từ chối quyền
            return []
        except (psutil.NoSuchProcess, Exception):
            return []

    def get_process_info(self) -> Dict[str, Any]:
        """Lấy thông tin tổng quan của tiến trình."""
        if not self.is_running():
            return {"pid": self.pid, "status": "TERMINATED_OR_UNAVAILABLE"}

        try:
            return {
                "pid": self.pid,
                "name": self.process.name(),
                "status": self.process.status(),
                "create_time": self.process.create_time(),
                "cpu_percent": self.get_cpu_usage(interval=0.1),
                "memory_rss": self.get_memory_usage(),
                "num_threads": self.process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"pid": self.pid, "status": "ACCESS_DENIED_OR_TERMINATED"}
