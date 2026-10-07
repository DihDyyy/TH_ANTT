# -*- coding: utf-8 -*-
"""
Sinh viên thực hiện: Lê Đình Duy (MSSV: 2387700102 - Lớp: 23DATA1)
Tài khoản / Username: dihdyyy | Email: dihdyyy@gmail.com
"""
import threading

class RoomManager:
    def __init__(self):
        # room_name -> set(usernames)
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, room_name):
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = set()

    def join_room(self, room_name, client_sock_or_user):
        self.add_to_room(room_name, client_sock_or_user)

    def add_to_room(self, room_name, username):
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = set()
            self.rooms[room_name].add(username)

    def leave_room(self, room_name, username):
        self.remove_from_room(room_name, username)

    def remove_from_room(self, room_name, username):
        with self.lock:
            if room_name in self.rooms:
                self.rooms[room_name].discard(username)

    def get_room_members(self, room_name):
        with self.lock:
            return list(self.rooms.get(room_name, set()))

    def broadcast_room(self, room_name, message, sender_sock):
        with self.lock:
            if room_name not in self.rooms:
                return
            for client in self.rooms[room_name]:
                if hasattr(client, 'send') and client != sender_sock:
                    try:
                        client.send(message)
                    except Exception:
                        pass
