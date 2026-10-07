# -*- coding: utf-8 -*-
"""
NetRecon - Flask Web Application
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Email: dihdyyy@gmail.com
"""
import os
import asyncio
from flask import Flask, render_template, request
from dotenv import load_dotenv

from modules import port_scanner, service_detector, banner_grabber
from modules import network_mapper, vuln_checker, email_sender

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form['target']
    ports_raw = request.form.get('ports', '22,80,443')
    ports = list(map(int, [p.strip() for p in ports_raw.split(',') if p.strip()]))
    mode = request.form.get('mode', 'all')
    email = request.form.get('email', 'dihdyyy@gmail.com')
    result = {}

    if mode in ['scan', 'all']:
        result['scan'] = asyncio.run(port_scanner.async_scan_ports(target, ports))
    if mode in ['service', 'all']:
        result['service'] = service_detector.detect_service(target, ports)
    if mode in ['banner', 'all']:
        result['banner'] = {port: banner_grabber.grab_banner(target, port) for port in ports}
    if mode in ['map', 'all']:
        result['map'] = network_mapper.map_network()
    if mode in ['vuln', 'all']:
        result['vuln'] = vuln_checker.check_vulns(ports)

    body = f"Kết quả NetRecon - Báo cáo an ninh mạng\n" \
           f"Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)\n" \
           f"Email người gửi: {os.getenv('SMTP_USER', 'dihdyyy@gmail.com')}\n" \
           f"Mục tiêu: {target} | Cổng: {ports_raw}\n\n"
    for k, v in result.items():
        body += f"--- {k.upper()} ---\n{v}\n\n"

    smtp_user = os.getenv("SMTP_USER", "dihdyyy@gmail.com")
    smtp_pass = os.getenv("SMTP_PASS")
    if smtp_user and smtp_pass and email:
        email_sender.send_email(email, f"Kết quả quét NetRecon [dihdyyy] - {target}", body, smtp_user, smtp_pass)

    return render_template('result.html', result=result)

if __name__ == '__main__':
    print("=" * 60)
    print("NetRecon Web App - Sinh viên: Lê Đình Duy (MSSV: 2387700102)")
    print("Lớp: 23DATA1 | Username: dihdyyy | Email: dihdyyy@gmail.com")
    print("Đang khởi động trên http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
