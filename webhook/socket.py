import socket

HOST = "127.0.0.1"
PORT = 8001

def send_task(task):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(str(task.id).encode())
