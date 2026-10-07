# -*- coding: utf-8 -*-
"""
NetRecon - Command Line Interface (CLI)
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Email: dihdyyy / dihdyyy@gmail.com
"""
import click
import asyncio
from modules.port_scanner import async_scan_ports
from modules.service_detector import detect_service
from modules.banner_grabber import grab_banner
from modules.network_mapper import map_network
from modules.vuln_checker import check_vulns

@click.command()
@click.option('--target', prompt='Target IP', default='127.0.0.1', help='Target IP address.')
@click.option('--ports', default='22,80,443', help='Comma-separated port list or range.')
@click.option('--rate-limit', default=100, help='Max concurrent scans.')
@click.option('--mode', default='all', help='Choose from: scan, service, banner, map, vuln, all')
def cli(target, ports, rate_limit, mode):
    print("=" * 65)
    print("NetRecon CLI - Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)")
    print(f"Target: {target} | Mode: {mode} | User: dihdyyy")
    print("=" * 65)
    ports_list = list(map(int, [p.strip() for p in ports.split(',') if p.strip()]))

    if mode in ['scan', 'all']:
        asyncio.run(async_scan_ports(target, ports_list, rate_limit))
    if mode in ['service', 'all']:
        print(detect_service(target, ports_list))
    if mode in ['banner', 'all']:
        for p in ports_list:
            print(f"{p}: {grab_banner(target, p)}")
    if mode in ['map', 'all']:
        print(map_network())
    if mode in ['vuln', 'all']:
        print(check_vulns(ports_list))

if __name__ == '__main__':
    cli()
