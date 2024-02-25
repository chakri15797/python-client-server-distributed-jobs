import socket
import threading
from queue import Queue
from itertools import count

HOST = 'localhost'
PORT = 5000
FILENAME = 'server_info.txt'
COMMANDS = Queue()
CLIENTS = []
command_counter = count(1)
client_counter = count(1)
THREAD_STATUS = {}

def find_free_port(start_port):
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, port))
            return port
        except OSError:
            port += 1

def write_server_info_to_file(port):
    with open(FILENAME, 'w') as file:
        file.write(f"{HOST}:{port}")

def handle_client(conn, addr):
    client_id = next(client_counter)
    print(f"Client {client_id} connected from {addr}")
    client_queue = Queue()
    CLIENTS.append((client_id, conn, addr, client_queue))
    THREAD_STATUS[client_id] = 'Connected'  # Update status when client connects
    while True:
        try:
            if not client_queue.empty():
                command = client_queue.get()
                print(f"Sending command {command} to client {client_id}")
                conn.sendall(command.encode())
                response = conn.recv(1024).decode()
                print(f"Received response from client {client_id}: {response}")
            else:
                threading.Event().wait(2)  # Wait for 2 seconds before checking again
        except Exception as e:
            print(f"Error receiving data from client {client_id}: {e}")
            break
    print(f"Client {client_id} disconnected")
    CLIENTS.remove((client_id, conn, addr, client_queue))
    THREAD_STATUS[client_id] = 'Disconnected'  # Update status when client disconnects
    conn.close()


def process_commands():
    while True:
        command_id, command, client_id = COMMANDS.get()
        if command_id == -1:
            break
        if CLIENTS:
            _, _, _, client_queue = min(CLIENTS, key=lambda x: x[3].qsize())
            client_queue.put(command)

def start_server():
    port = find_free_port(PORT)
    write_server_info_to_file(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, port))
        server_socket.listen()
        print(f"Server listening on {HOST}:{port}")
        threading.Thread(target=process_commands).start()
        threading.Thread(target=ask_for_commands).start()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

def ask_for_commands():
    while True:
        command = input("Enter command to send to clients (or 'exit' to quit): ")
        if not command:  # Check if the command is empty
            continue
        if command.lower() == 'exit':
            COMMANDS.put((-1, '', None))
            break
        else:
            COMMANDS.put((next(command_counter), command, None))

def monitor_threads():
    with open('thread_status.txt', 'w') as file:
        while True:
            for client_id, status in THREAD_STATUS.items():
                file.write(f"Client {client_id}: {status}\n")
            file.write("\n")
            file.flush()
            threading.Event().wait(60)  # Wait for 5 seconds before checking again

if __name__ == "__main__":
    threading.Thread(target=monitor_threads).start()
    start_server()
