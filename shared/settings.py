import socket

DEBUG = True

HEADER = 128
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 65000
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
