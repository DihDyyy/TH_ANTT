"""
NetworkTrafficAnalyzer - Phân tích lưu lượng mạng và siêu dữ liệu kết nối.
Thu thập số liệu I/O qua psutil.net_io_counters và thông tin socket metadata,
xử lý an toàn quyền truy cập (AccessDenied) và lọc kết nối theo PID.
"""

from typing import Dict, List, Any, Optional
import psutil


class NetworkTrafficAnalyzer:
    """
    Bộ phân tích mạng cấp độ siêu dữ liệu hệ điều hành (OS Socket Metadata Analyzer).
    
    LƯU Ý BẢO MẬT VÀ PHẠM VI GIÁM SÁT:
    1. Không phân tích gói tin sâu (Deep Packet Inspection - DPI):
       Module này chỉ quan sát metadata kết nối (IP cục bộ, port, IP đích, trạng thái socket TCP/UDP)
       do hệ điều hành cung cấp thông qua psutil.
    2. Giới hạn phát hiện C2 / Exfiltration:
       Chỉ dựa trên socket metadata không thể khẳng định 100% một luồng kết nối là C2 (Command & Control)
       hay rò rỉ dữ liệu nhạy cảm (data exfiltration), bởi không thu thập nội dung tải trọng (payload)
       hoặc kiểm tra chứng chỉ TLS/SSL.
    3. Tuân thủ quyền riêng tư:
       Không tự ý thu thập dữ liệu người dùng hay can thiệp vào các phiên mạng ngoài phạm vi kiểm thử.
    """

    def get_network_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê I/O của toàn bộ card mạng (bytes gửi/nhận, gói tin lỗi).
        
        Returns:
            Dict[str, snetio]: Dict các interface mạng cùng số liệu gửi/nhận.
        """
        try:
            return psutil.net_io_counters(pernic=True)
        except Exception:
            return {}

    def get_connections(self, pid: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các kết nối mạng đang hoạt động, có thể lọc theo PID.
        
        Args:
            pid (Optional[int]): Lọc kết nối của tiến trình cụ thể (nếu có).
            
        Returns:
            List[Dict[str, Any]]: Danh sách thông tin metadata kết nối.
        """
        connections_list: List[Dict[str, Any]] = []

        try:
            # Nếu chỉ định PID, lấy kết nối trực tiếp từ Process đó để tránh đòi quyền admin toàn cục
            if pid is not None:
                try:
                    proc = psutil.Process(pid)
                    raw_connections = proc.net_connections(kind='inet')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return []
            else:
                try:
                    raw_connections = psutil.net_connections(kind='inet')
                except (psutil.AccessDenied, PermissionError):
                    # Trên Windows, nếu không chạy dưới quyền Administrator, net_connections() toàn cục có thể bị từ chối
                    return []

            for conn in raw_connections:
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""

                connections_list.append({
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": laddr,
                    "remote_address": raddr,
                    "status": conn.status,
                    "pid": conn.pid
                })
        except Exception:
            return []

        return connections_list
