import socket
import threading
import os
from utils import calculate_sha256

HOST = '127.0.0.1'
PORT = 5001
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def handle_client(conn, addr):
    print(f"[KẾT NỐI] {addr}")
    filename = conn.recv(1024).decode()
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    with open(file_path, 'wb') as f:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            f.write(data)
    conn.close()

    print(f"[XONG] Đã nhận file {filename}")
    print(f"[HASH] SHA-256 = {calculate_sha256(file_path)}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Đang chờ file tại {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()
