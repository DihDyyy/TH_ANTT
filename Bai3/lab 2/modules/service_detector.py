# -*- coding: utf-8 -*-
"""
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Username: dihdyyy | Email: dihdyyy@gmail.com
"""
import subprocess, logging
from datetime import datetime

logging.basicConfig(filename='netrecon.log', level=logging.INFO)

def log(msg):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[{now}] {msg}")

def detect_service(ip, ports):
    ports_str = ','.join(str(p) for p in ports)
    cmd = ["nmap", "-sV", "-p", ports_str, ip]
    log(f"Running service detection on {ip}:{ports_str}")
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        log(result)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode() if e.output else str(e)}"
    except FileNotFoundError:
        return "Error: nmap executable not found in PATH. Please install Nmap and add it to PATH."
    except Exception as e:
        return f"Error: {e}"
