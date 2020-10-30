import socket
import threading
from threading import Lock
from typing import List, Dict, Any

import shared.protocol as protocol
from shared.logging import log
from shared.utils import send
from . import settings

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(settings.ADDR)


class User:
    def __init__(self, username: str, conn: socket.socket, addr):
        self.username = username
        self.conn = conn
        self.addr = addr


active_connections: Dict[Any, User] = {}
active_connections_lock = Lock()


def handle_connect(conn: socket.socket, addr, message: List[str]):
    user = User(message[1], conn, addr)
    with active_connections_lock:
        active_connections[addr] = user
    send(conn, protocol.OK)


def handle_disconnect(conn: socket.socket, addr, _: List[str]):
    with active_connections_lock:
        del active_connections[addr]
    send(conn, protocol.OK)


def handle_msg_all(conn: socket.socket, addr, message: List[str]):
    msg = ' '.join(message[1:])
    send(conn, protocol.OK)
    threads = None
    with active_connections_lock:
        sender = active_connections[addr]
        notify_others_msg = f"{protocol.RECV_MSG} {sender.username} {msg}"

        threads = [threading.Thread(target=send, args=(user.conn, notify_others_msg)) for user in
                   active_connections.values()]
    if threads:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


MESSAGE_HANDLERS = {
    protocol.CONNECT_MSG_HEADER: handle_connect,
    protocol.DISCONNECT_MSG: handle_disconnect,
    protocol.SEND_MSG: handle_msg_all
}


def delegate_message(conn: socket.socket, addr, message: str):
    tokens = message.split()
    command = tokens[0]
    MESSAGE_HANDLERS[command](conn, addr, tokens)


def handle_client(conn: socket.socket, addr):
    log(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg_length = conn.recv(settings.HEADER).decode(settings.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(settings.FORMAT)
            log(f"[{addr}] {msg}")
            delegate_message(conn, addr, msg)

            if msg == protocol.DISCONNECT_MSG:
                connected = False

    conn.close()


def start():
    server.listen()
    log(f'[LISTENING] Server ist listening on {settings.SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        log(f"[ACTIVE CONNECTIONS] {threading.active_count()}")


def main():
    log(f'Server is starting on {settings.SERVER}:{settings.PORT}')
    start()
