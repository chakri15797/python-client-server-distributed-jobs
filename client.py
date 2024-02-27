import socket
import subprocess
import json 
import os

FILENAME = 'server_info.txt'
CLIENT_ID = None
BUFFER = ""
LOG_FILE= None


def print_and_log(message):
    global CLIENT_ID, BUFFER, LOG_FILE
    if CLIENT_ID is not None:
        if not LOG_FILE:
            LOG_FILE = open(f"logs/client_{CLIENT_ID}.log", 'w')
        if BUFFER != "":
            message = BUFFER + message
            BUFFER = ""
        LOG_FILE.write(message + '\n')
    else:
        BUFFER += message + "\n"
    print(message)

def read_server_info_from_file():
    with open(FILENAME, 'r') as file:
        server_info = file.readline().strip().split(':')
    return server_info[0], int(server_info[1])

def connect_to_server():
    global CLIENT_ID, LOG_FILE
    server_host, server_port = read_server_info_from_file()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        print_and_log(f"Connected to server {server_host}:{server_port}")
        while True:
            try:
                command = client_socket.recv(1024).decode()
                if not command:
                    print_and_log("Empty command received")
                    break
                print_and_log(f"Received command: {command}")
                command_data = json.loads(command)
                client_id = command_data["client_id"]
                CLIENT_ID = client_id
                command_id = command_data["command_id"]
                command_text = command_data["command"].strip()
                if command_text=='ping':
                    continue
                output = subprocess.check_output(command_text, shell=True).decode()
                print_and_log(f"Processed command: {command_text}")
                print_and_log(f"Output: {output}")
                response = {"client_id": client_id, "command_id": command_id, "response": output}
                client_socket.sendall(json.dumps(response).encode())
                LOG_FILE.flush
            except KeyboardInterrupt:
                print("KeyboardInterrupt: Stopping the client")
                client_socket.close()
                break
            except Exception as e:
                print_and_log(f"Error processing command: {e}")
                client_socket.close()
                break

if __name__ == "__main__":
    directory = 'logs'
    if not os.path.exists(directory):
        os.makedirs(directory)
    connect_to_server()
