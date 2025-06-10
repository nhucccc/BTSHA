import hashlib
import socket

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def send_file_socket(filepath, filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5001))  # Gửi tới socket_server
    s.send(filename.encode())
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            s.sendall(data)
    s.close()
