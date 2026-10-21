"""
Flask API - Cổng giám sát an ninh động (DAST Monitoring Platform).
Cung cấp các RESTful API phục vụ demo học tập giám sát tiến trình, bộ nhớ,
kết nối mạng và kiểm thử hành vi trong sandbox.
"""

import os
import psutil
from flask import Flask, jsonify, request

from runtime_monitor import RuntimeMonitor
from memory_analyzer import MemoryAnalyzer
from network_traffic_analyzer import NetworkTrafficAnalyzer
from security_behavior_checker import SecurityBehaviorChecker
from virtual_sandbox import VirtualSandbox

app = Flask(__name__)
CURRENT_PID = os.getpid()

# ============================================================================
# CÁC ENDPOINT TƯƠNG THÍCH THEO TÀI LIỆU LAB 05 (TRANG 20 - 21)
# ============================================================================

@app.route("/api/monitor", methods=["GET"])
def monitor():
    """Lấy thông số CPU, RAM và tệp mở của tiến trình hiện hành."""
    try:
        rm = RuntimeMonitor(CURRENT_PID)
        return jsonify({
            "cpu_usage": rm.get_cpu_usage(interval=0.1),
            "memory_usage": rm.get_memory_usage(),
            "open_files": [getattr(f, 'path', str(f)) for f in rm.get_open_files()]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/memory", methods=["GET"])
def memory():
    """Kiểm tra rò rỉ bộ nhớ qua GC và kiểm tra tràn số 64-bit."""
    try:
        ma = MemoryAnalyzer()
        return jsonify({
            "memory_leaks": str(ma.check_memory_leaks()),
            "overflow_test": ma.check_overflow(2**64)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/network", methods=["GET"])
def network():
    """Lấy số liệu I/O mạng từ các interface."""
    try:
        nta = NetworkTrafficAnalyzer()
        return jsonify({
            "network_stats": {k: v._asdict() for k, v in nta.get_network_stats().items()}
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/security", methods=["GET"])
def security():
    """Kiểm tra các lời gọi hệ thống/hàm nhạy cảm trong mã nguồn."""
    try:
        sbc = SecurityBehaviorChecker()
        return jsonify({
            "suspicious_calls": sbc.suspicious_calls()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sandbox", methods=["POST"])
def sandbox():
    """Thực thi câu lệnh mẫu trong thư mục tạm có giới hạn."""
    try:
        data = request.get_json(silent=True) or {}
        command = data.get("command", "echo Hello Sandbox")
        # Giới hạn an toàn: không cho phép các chuỗi lệnh phá hoại hệ thống
        blocked_keywords = ["rmdir /s /q c:\\", "format", "del /f /s /q c:\\"]
        if any(bad in command.lower() for bad in blocked_keywords):
            return jsonify({"error": "Command blocked by security policy"}), 400

        vs = VirtualSandbox()
        try:
            stdout, stderr = vs.run_isolated(command, timeout=5)
            return jsonify({
                "stdout": stdout,
                "stderr": stderr
            }), 200
        finally:
            vs.cleanup()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CÁC ENDPOINT MỞ RỘNG BẮT BUỘC THEO YÊU CẦU ĐỀ BÀI (MỤC 4.2 G)
# ============================================================================

@app.route("/", methods=["GET"])
def root_info():
    """Thông tin chung và trạng thái tổng quan của hệ thống DAST."""
    return jsonify({
        "service": "DAST Runtime Monitoring API",
        "lab": "Lab 05 - Phân tích và kiểm thử bảo mật",
        "status": "ONLINE",
        "host_pid": CURRENT_PID,
        "endpoints": {
            "GET /": "Thông tin dịch vụ",
            "GET /health": "Tình trạng sức khỏe API",
            "GET /processes": "Danh sách tiến trình giám sát được",
            "GET /connections": "Metadata các kết nối mạng",
            "GET /alerts": "Danh sách cảnh báo an ninh runtime",
            "GET /summary": "Báo cáo tổng hợp toàn diện",
            "GET /api/monitor": "Thông số monitor lab gốc",
            "GET /api/memory": "Thông số memory lab gốc",
            "GET /api/network": "Thông số network stats lab gốc",
            "GET /api/security": "Thông số security calls lab gốc",
            "POST /api/sandbox": "Chạy thử lệnh trong sandbox"
        },
        "disclaimer": "Hệ thống phục vụ mục đích học tập và nghiên cứu mã nguồn, không thay thế giải pháp EDR doanh nghiệp."
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Kiểm tra tình trạng hoạt động của API giám sát."""
    return jsonify({
        "status": "UP",
        "pid": CURRENT_PID,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "system_memory_percent": psutil.virtual_memory().percent
    }), 200


@app.route("/processes", methods=["GET"])
def get_processes():
    """Lấy danh sách các tiến trình phù hợp (giới hạn 15 tiến trình an toàn)."""
    procs = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                pinfo = proc.info
                # Lấy thêm thông tin bộ nhớ cơ bản
                mem_rss = proc.memory_info().rss // 1024  # KB
                procs.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "status": pinfo['status'],
                    "memory_kb": mem_rss
                })
                if len(procs) >= 15:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "count": len(procs),
        "processes": procs
    }), 200


@app.route("/connections", methods=["GET"])
def get_connections():
    """Lấy metadata kết nối mạng an toàn (không lấy payload)."""
    try:
        nta = NetworkTrafficAnalyzer()
        # Ưu tiên lấy kết nối của tiến trình hiện tại để đảm bảo quyền truy cập không bị từ chối
        conns = nta.get_connections(pid=CURRENT_PID)
        return jsonify({
            "pid_monitored": CURRENT_PID,
            "connections_count": len(conns),
            "connections": conns
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/alerts", methods=["GET"])
def get_alerts():
    """Trả về danh sách cảnh báo bảo mật dựa trên chỉ số runtime hiện tại."""
    try:
        rm = RuntimeMonitor(CURRENT_PID)
        sbc = SecurityBehaviorChecker()
        nta = NetworkTrafficAnalyzer()

        cpu = rm.get_cpu_usage(interval=0.1)
        mem = rm.get_memory_usage()
        conns = nta.get_connections(pid=CURRENT_PID)

        metrics_data = {
            "cpu_percent": cpu,
            "memory_rss": mem,
            "connections_count": len(conns),
            "open_files_count": len(rm.get_open_files())
        }

        alerts = sbc.evaluate_runtime_events(metrics_data)
        suspicious = sbc.suspicious_calls()

        return jsonify({
            "pid": CURRENT_PID,
            "runtime_alerts": alerts,
            "suspicious_static_calls": suspicious
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summary", methods=["GET"])
def get_summary():
    """Báo cáo tổng hợp tình trạng an ninh và tài nguyên của tiến trình."""
    try:
        rm = RuntimeMonitor(CURRENT_PID)
        ma = MemoryAnalyzer()
        sbc = SecurityBehaviorChecker()
        nta = NetworkTrafficAnalyzer()

        cpu = rm.get_cpu_usage(interval=0.1)
        mem = rm.get_memory_usage()
        conns = nta.get_connections(pid=CURRENT_PID)

        metrics_data = {
            "cpu_percent": cpu,
            "memory_rss": mem,
            "connections_count": len(conns),
            "open_files_count": len(rm.get_open_files())
        }

        return jsonify({
            "pid": CURRENT_PID,
            "process_name": psutil.Process(CURRENT_PID).name(),
            "cpu_usage_percent": cpu,
            "memory_usage_bytes": mem,
            "memory_overflow_test": ma.check_overflow(2**64),
            "connections_active": len(conns),
            "alerts": sbc.evaluate_runtime_events(metrics_data),
            "suspicious_calls": sbc.suspicious_calls()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Mặc định chỉ bind vào 127.0.0.1 để đảm bảo an toàn cục bộ
    app.run(host="127.0.0.1", port=5000, debug=False)
