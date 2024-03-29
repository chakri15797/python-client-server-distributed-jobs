import socket
import threading
from queue import Queue
from itertools import count
import json
import atexit
import os
import time
import sys
import queue
from signal import pthread_kill, SIGUSR1, SIGTSTP

HOST = '0.0.0.0'
PORT = 5000
FILENAME = 'server_info.txt'
COMMANDS = Queue()
CLIENTS = []
command_counter = count(1)
client_counter = count(1)
THREAD_STATUS = {}
SHUTDOWN_FLAG = False  # Flag to indicate shutdown
THREADS = []

def is_socket_closed(sock):
    try:
        data = sock.recv(1)
        if not data:
            return True
        else:
            return False
    except socket.error as e:
        return True
    except socket.timeout:
        return True

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
    global COMMANDS, SHUTDOWN_FLAG, CLIENTS
    client_id = next(client_counter)
    print(f"Client {client_id} connected from {addr}")
    client_queue = Queue()
    CLIENTS.append((client_id, conn, addr, client_queue))
    THREAD_STATUS[client_id] = 'Connected'  # Update status when client connects
    while not SHUTDOWN_FLAG:
        try:
            if not client_queue.empty():
                if THREAD_STATUS[client_id] == 'Disconnected':
                    COMMANDS.put((command["command_id"],command["command"]))
                    break
                command = client_queue.get()
                print(f"Sending command {command} to client {client_id}")
                conn.sendall(json.dumps(command).encode())
                response = conn.recv(1024).decode()
                print(f"Received response from client {client_id}: {response}")
            else:
                if THREAD_STATUS[client_id] == 'Disconnected':
                    break
                time.sleep(1)  # Wait for 1 second before checking again
        except Exception as e:
            COMMANDS.put((command["command_id"],command["command"]))
            print(f"Error receiving data from client {client_id}: {e}")
            break
    print(f"Client {client_id} disconnected")
    temp = (client_id, conn, addr, client_queue)
    if (client_id, conn, addr, client_queue) in CLIENTS:
        CLIENTS.remove(temp)
        THREAD_STATUS[client_id] = 'Disconnected'  # Update status when client disconnects
    conn.close()
    print("Exiting handle_client")


def process_commands():
    global SHUTDOWN_FLAG, COMMANDS, CLIENTS
    while not SHUTDOWN_FLAG:
        if not COMMANDS.empty() and len(CLIENTS)!=0:
            command_id, command = COMMANDS.get(timeout=1)
            if command_id == -1:
                break
            if CLIENTS:
                client_id, _, _, client_queue = min(CLIENTS, key=lambda x: x[3].qsize())
                client_queue.put({"client_id": client_id, "command_id": command_id, "command": command})
    print("Exiting process_commands")

def start_server():
    global SHUTDOWN_FLAG
    port = find_free_port(PORT)
    write_server_info_to_file(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, port))
        server_socket.listen()
        server_socket.settimeout(0.1)
        print(f"Server listening on {HOST}:{port}")
        (t := threading.Thread(name="ask_for_commands",target=ask_for_commands)).start()
        THREADS.append(t)
        t = threading.Thread(name="process_commands",target=process_commands).start()
        THREADS.append(t)
        while not SHUTDOWN_FLAG:
            try:
                conn, addr = server_socket.accept()
                threading.Thread(name="handle_client",target=handle_client, args=(conn, addr)).start()
                THREADS.append(t)
            except socket.timeout:
                pass
    print("Exiting start_server")

def ask_for_commands():
    global SHUTDOWN_FLAG, COMMANDS
    while not SHUTDOWN_FLAG:
        command = input("Enter command to send to clients (or 'exit' to quit): ")
        if not command:  # Check if the command is empty
            continue
        if command.lower() == 'exit':
            COMMANDS.put((-1, ''))
            SHUTDOWN_FLAG = True  # Set the shutdown flag
            print("Exiting ask_for_commands")
            break
        else:
            COMMANDS.put((next(command_counter), command))

def monitor_threads():
    global SHUTDOWN_FLAG
    with open('logs/thread_status.txt', 'w') as file:
        while not SHUTDOWN_FLAG:  # Continue monitoring until shutdown flag is set
            for client_id, status in THREAD_STATUS.items():
                file.write(f"Client {client_id}: {status}\n")
            file.write("\n")
            file.flush()
            time.sleep(10)  # Wait for 10 seconds before checking again
    print("Exiting monitor_threads")

def monitor_clients():
    global SHUTDOWN_FLAG
    while not SHUTDOWN_FLAG:  # Continue monitoring until shutdown flag is set
        for client_id, conn, addr, client_queue in CLIENTS:
            if is_socket_closed(conn):
                THREAD_STATUS[client_id] = 'Disconnected'
                if not SHUTDOWN_FLAG:
                    CLIENTS.remove((client_id, conn, addr, client_queue))
        time.sleep(0.1)
    print("Exiting monitor_clients")

def exit_handler():
    print("Exiting...")

def kill_threads():
    while True:
        if SHUTDOWN_FLAG:
            time.sleep(1)
            for t in THREADS:
                if t is not None and t.is_alive():
                    pthread_kill(t.ident, SIGTSTP)
            break
    print("Exiting kill_threads")

if __name__ == "__main__":
    try:
        directory = 'logs'
        if not os.path.exists(directory):
            os.makedirs(directory)
        #(t := threading.Thread(name="monitor_threads",target=monitor_threads)).start()
        #THREADS.append(t)
        (t := threading.Thread(name="monitor_clients",target=monitor_clients)).start()
        THREADS.append(t)
        threading.Thread(name="kill_threads",target=kill_threads).start()
        start_server()
    except KeyboardInterrupt:
        SHUTDOWN_FLAG = True  # Set the shutdown flag when Ctrl+C is pressed     
        print("Shutting down server...")
    finally:
        atexit.register(exit_handler)