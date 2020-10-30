import socket
from . import settings


def send(conn: socket.socket, msg: str):
    message = msg.encode(settings.FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(settings.FORMAT)
    send_length += b' ' * (settings.HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)
