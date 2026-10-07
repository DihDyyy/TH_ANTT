# -*- coding: utf-8 -*-
"""
SecureChat - Multi-threaded Socket Server với mTLS và AES-256 E2EE
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Username: dihdyyy
"""
import socket
import ssl
import threading
import os
import binascii
from message_encryption import MessageEncryption
from connection_manager import ConnectionManager
from room_manager import RoomManager

HOST = '127.0.0.1'
PORT = 8443

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_CERT = os.path.join(BASE_DIR, 'certs', 'ca', 'ca.crt')
SERVER_CERT = os.path.join(BASE_DIR, 'certs', 'server', 'server.crt')
SERVER_KEY = os.path.join(BASE_DIR, 'certs', 'server', 'server.key')

conn_mgr = ConnectionManager()
room_mgr = RoomManager()

def handle_client(ssl_sock, addr):
    print(f"[+] Client connected: {addr}")
    try:
        # Nhận tin nhắn đầu tiên chứa username:key_hex
        init_data = ssl_sock.recv(1024).decode()
        username, key_hex = init_data.split(':', 1)
        aes_key = binascii.unhexlify(key_hex)
        me = MessageEncryption(aes_key)

        conn_mgr.add_client(ssl_sock, username, me)
        room_mgr.add_to_room('general', username)

        while True:
            enc_data = ssl_sock.recv(4096)
            if not enc_data:
                break
            # Server giải mã dữ liệu của người gửi
            plain_msg = me.decrypt(enc_data)
            print(f"[{username}]: {plain_msg}", flush=True)

            # Broadcast tin nhắn cho các client khác trong room 'general'
            members = room_mgr.get_room_members('general')
            for member in members:
                if member != username:
                    client_conn = conn_mgr.get_client_by_name(member)
                    if client_conn:
                        target_sock, target_me = client_conn
                        try:
                            # Server mã hóa lại tin nhắn bằng khóa AES của người nhận
                            formatted_msg = f"[{username}]: {plain_msg}"
                            re_enc = target_me.encrypt(formatted_msg)
                            target_sock.send(re_enc)
                        except Exception:
                            pass
    except Exception as e:
        print(f"[-] Client error {addr}: {e}")
    finally:
        client_name = conn_mgr.get_name_by_sock(ssl_sock)
        if client_name:
            room_mgr.remove_from_room('general', client_name)
        conn_mgr.remove_client(ssl_sock)
        ssl_sock.close()
        print(f"[-] Client disconnected: {addr}")

def main():
    print("=" * 65)
    print("SecureChat Server - SSL/TLS mTLS & AES-256 CBC")
    print("Sinh viên: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1 - dihdyyy)")
    print(f"Đang lắng nghe an toàn tại {HOST}:{PORT}")
    print("=" * 65)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    context.load_verify_locations(cafile=CA_CERT)
    context.verify_mode = ssl.CERT_REQUIRED

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        sock, addr = server.accept()
        try:
            ssl_sock = context.wrap_socket(sock, server_side=True)
            t = threading.Thread(target=handle_client, args=(ssl_sock, addr))
            t.daemon = True
            t.start()
        except ssl.SSLError as e:
            print(f"[!] SSL Handshake failed from {addr}: {e}")
            sock.close()

if __name__ == '__main__':
    main()
