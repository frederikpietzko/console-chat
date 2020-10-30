import socket
import sys
import threading
from typing import List

from shared import protocol
from shared.utils import send
from . import settings

connected = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect(user: str, addr=settings.ADDR):
    global connected
    client.connect(addr)
    conn_msg = f"{protocol.CONNECT_MSG_HEADER} {user}"
    send(client, conn_msg)
    connected = True


def handle_recv_msg(message: List[str]):
    user = message[1]
    msg = ' '.join(message[2:])
    print(f"[{user}]:\t{msg}")


def handle_ok(_: List[str]):
    pass


MESSAGE_HANDLERS = {
    protocol.RECV_MSG: handle_recv_msg,
    protocol.OK: handle_ok
}


def delegate_msg(message: str):
    tokens = message.split()
    msg_header = tokens[0]
    MESSAGE_HANDLERS[msg_header](tokens)


def receive():
    while connected:
        msg_length = client.recv(settings.HEADER).decode(settings.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(settings.FORMAT)
            delegate_msg(msg)


def send_msg(msg: str):
    f_msg = f"{protocol.SEND_MSG} {msg}"
    send(client, f_msg)


def msg_prompt():
    global connected
    while connected:
        msg = input("")
        sys.stdout.write("\033[F")  # back to previous line
        sys.stdout.write("\033[K")
        if msg == protocol.DISCONNECT_MSG:
            send(client, protocol.DISCONNECT_MSG)
            connected = False
            continue

        send_msg(msg)


def main():
    username = input("Select a username: \t")

    connect(username)

    recv_thread = threading.Thread(target=receive)
    recv_thread.start()
    input_thread = threading.Thread(target=msg_prompt)
    input_thread.start()
    recv_thread.join()
    input_thread.join()
