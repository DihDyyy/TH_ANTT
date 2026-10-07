# -*- coding: utf-8 -*-
"""
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Username: dihdyyy | Email: dihdyyy@gmail.com
"""
import threading

class ConnectionManager:
    def __init__(self):
        # socket -> dict {'username': username, 'encryption': me}
        self.clients = {}
        self.lock = threading.Lock()

    def add_client(self, client_sock, username, encryption_obj):
        with self.lock:
            self.clients[client_sock] = {
                'username': username,
                'encryption': encryption_obj
            }

    def remove_client(self, client_sock):
        with self.lock:
            if client_sock in self.clients:
                del self.clients[client_sock]

    def get_client(self, client_sock):
        with self.lock:
            return self.clients.get(client_sock)

    def get_name_by_sock(self, client_sock):
        with self.lock:
            client_info = self.clients.get(client_sock)
            return client_info['username'] if client_info else None

    def get_client_by_name(self, username):
        with self.lock:
            for sock, info in self.clients.items():
                if info.get('username') == username:
                    return sock, info.get('encryption')
            return None

    def broadcast(self, message, sender_sock):
        with self.lock:
            for client in self.clients:
                if client != sender_sock:
                    try:
                        client.send(message)
                    except Exception:
                        pass
