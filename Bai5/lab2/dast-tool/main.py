"""
Main - Điểm khởi chạy dòng lệnh cho Dynamic Application Security Testing (DAST Tool).
Tích hợp RuntimeMonitor, MemoryAnalyzer, NetworkTrafficAnalyzer, SecurityBehaviorChecker, VirtualSandbox.
Hỗ trợ chạy một lượt (one-shot khớp chuẩn lab) hoặc chạy giám sát theo chu kỳ (loop/duration) với dừng an toàn bằng Ctrl+C.
"""

import argparse
import os
import sys
import time

from runtime_monitor import RuntimeMonitor
from memory_analyzer import MemoryAnalyzer
from network_traffic_analyzer import NetworkTrafficAnalyzer
from security_behavior_checker import SecurityBehaviorChecker
from virtual_sandbox import VirtualSandbox

# Đảm bảo UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def run_single_scan(pid: int):
    """
    Chạy phân tích động 1 lần khớp chính xác định dạng kết quả trong tài liệu Lab 05.
    """
    print("[+] Monitoring current process:", pid)
    rm = RuntimeMonitor(pid)
    print("CPU Usage:", rm.get_cpu_usage(interval=0.5))
    print("Memory Usage:", rm.get_memory_usage())
    print("Open Files:", rm.get_open_files())

    ma = MemoryAnalyzer()
    print("Memory Leaks:", ma.check_memory_leaks())
    print("Overflow Test:", ma.check_overflow(2**64))

    nta = NetworkTrafficAnalyzer()
    print("Network Stats:", nta.get_network_stats())

    sbc = SecurityBehaviorChecker()
    print("Suspicious Calls:", sbc.suspicious_calls())

    vs = VirtualSandbox()
    try:
        out, err = vs.run_isolated("echo Hello Sandbox")
        print("Sandbox stdout:", out)
        print("Sandbox stderr:", err)
    finally:
        vs.cleanup()


def run_continuous_monitor(pid: int, interval: float, duration: int):
    """
    Chạy giám sát theo chu kỳ thời gian và dừng an toàn bằng phím tắt Ctrl+C.
    """
    print(f"[+] Bắt đầu giám sát PID {pid} (chu kỳ {interval}s, thời lượng tối đa {duration}s)...")
    print("[*] Nhấn Ctrl+C để dừng giám sát an toàn bất kỳ lúc nào.\n")

    rm = RuntimeMonitor(pid)
    ma = MemoryAnalyzer()
    nta = NetworkTrafficAnalyzer()
    sbc = SecurityBehaviorChecker()

    start_time = time.time()
    iteration = 0

    try:
        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                print("\n[+] Đã đạt thời lượng giám sát tối đa.")
                break

            iteration += 1
            cpu = rm.get_cpu_usage(interval=interval)
            mem = rm.get_memory_usage()
            ma.record_sample(mem)
            trend = ma.analyze_trend()
            conns = nta.get_connections(pid=pid)

            metrics_data = {
                "cpu_percent": cpu,
                "memory_rss": mem,
                "connections_count": len(conns),
                "open_files_count": len(rm.get_open_files()),
                "memory_alert": trend.get("alert", False),
                "memory_message": trend.get("message", "")
            }

            alerts = sbc.evaluate_runtime_events(metrics_data)

            print(f"[{time.strftime('%H:%M:%S')}] #{iteration} | CPU: {cpu:>4.1f}% | RAM: {mem // 1024:>6} KB | Conns: {len(conns):>2} | Alerts: {len(alerts)}")
            for alert in alerts:
                print(f"   --> [{alert['level']}] {alert['category']}: {alert['reason']}")

    except KeyboardInterrupt:
        print("\n\n[!] Nhận tín hiệu dừng từ người dùng (Ctrl+C). Đang đóng tiến trình giám sát an toàn...")
    finally:
        print("[+] Hoàn tất phiên giám sát DAST.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DAST Tool - Dynamic Application Security Testing")
    parser.add_argument("--loop", action="store_true", help="Bật chế độ giám sát liên tục theo chu kỳ")
    parser.add_argument("--interval", type=float, default=2.0, help="Khoảng thời gian lấy mẫu (giây)")
    parser.add_argument("--duration", type=int, default=30, help="Tổng thời gian chạy giám sát (giây, 0 = vô hạn)")
    parser.add_argument("--pid", type=int, default=os.getpid(), help="PID tiến trình cần giám sát (mặc định: PID hiện tại)")

    args = parser.parse_args()

    if args.loop:
        run_continuous_monitor(args.pid, args.interval, args.duration)
    else:
        run_single_scan(args.pid)
