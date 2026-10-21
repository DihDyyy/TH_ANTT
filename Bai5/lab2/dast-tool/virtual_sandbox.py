"""
VirtualSandbox - Môi trường thực thi cô lập cơ bản cho ứng dụng mẫu.
Sử dụng thư mục tạm biệt lập, giới hạn thời gian chạy (timeout),
và cơ chế dọn dẹp tài nguyên sau khi kiểm thử.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Tuple, Optional


class VirtualSandbox:
    """
    Hộp cát thực thi mức tiến trình cục bộ (Process-level Virtual Sandbox).
    
    CẢNH BÁO BẢO MẬT & GIỚI HẠN TRÊN WINDOWS:
    1. Giới hạn phân tách trên Windows:
       Việc chạy tiến trình con trong thư mục tạm (tempfile.mkdtemp) CHỈ giới hạn thư mục làm việc (cwd).
       Trên Windows, tiến trình con vẫn sở hữu cùng Access Token của người dùng, vẫn có thể truy cập
       mạng, đọc Registry, và can thiệp vào các tệp khác nếu người dùng có quyền.
    2. KHÔNG PHẢI MÔI TRƯỜNG PHÂN TÍCH MALWARE THẬT:
       Không bao giờ thực thi mã độc thật sự (real malware) bằng class này!
       Đối với phân tích phần mềm độc hại thực tế, BẮT BUỘC phải sử dụng Máy ảo chuyên dụng (Cuckoo Sandbox,
       FlareVM trong VirtualBox/VMware với Snapshot đóng băng và Host-Only network) hoặc Windows Sandbox cô lập hoàn toàn.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """Khởi tạo thư mục tạm cô lập."""
        self.temp_dir = tempfile.mkdtemp(dir=base_dir, prefix="dast_sandbox_")

    def run_isolated(self, command: str, timeout: int = 5) -> Tuple[str, str]:
        """
        Thực thi lệnh trong môi trường thư mục tạm với giới hạn timeout.
        
        Args:
            command (str): Câu lệnh cần chạy.
            timeout (int): Thời gian tối đa (giây) trước khi tiến trình bị cưỡng chế dừng.
            
        Returns:
            Tuple[str, str]: (stdout, stderr) dưới dạng chuỗi đã decode.
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.temp_dir,
                capture_output=True,
                shell=True,
                timeout=timeout,
                text=False
            )
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            return stdout, stderr
        except subprocess.TimeoutExpired:
            return "", f"Execution Timeout: Lệnh vượt quá giới hạn cho phép ({timeout}s)."
        except Exception as e:
            return "", f"Execution Error: {str(e)}"

    def cleanup(self) -> None:
        """Dọn dẹp và xóa bỏ thư mục tạm thời sau khi kết thúc thử nghiệm."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __del__(self):
        self.cleanup()
