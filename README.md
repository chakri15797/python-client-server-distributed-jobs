# Command Execution Client-Server System
This project implements a client-server system where clients can connect to a server and execute commands received from the server. The server acts as a central hub, receiving commands from the user and distributing them to the connected clients. The clients execute the commands and send the output back to the server.

## Features
* Clients can connect to the server using the server's host and port information
* The server listens for incoming client connections and assigns a unique ID to each client
* The server receives commands from the user and distributes them to the available clients in a load-balanced manner
* Clients execute the received commands and send the output back to the server
* The server displays the output received from the clients
* The system supports multiple concurrent clients and commands
* Clients log their activity and output in individual log files
* The server monitors the status of client connections and threads

## Flow Diagrams
### Server Flow
                    +---------------------+
                    |    Start Server     |
                    +----------+----------+
                               |
                    +----------v----------+
                    |   Find Free Port    |
                    +----------+----------+
                               |
                    +----------v----------+
                    | Write Server Info   |
                    |      to File        |
                    +----------+----------+
                               |
                    +----------v----------+
         +----------+   Listen for Client  +----------+
         |          |      Connections     |          |
         |          +----------+----------+          |
         |                     |                     |
         |                     v                     v
+--------+--------+   +-----------------+   +-----------------+
|  Handle Client  |   | Ask for Commands|   | Process Commands|
|    Connection   |   |     (Thread)    |   |     (Thread)    |
+--------+--------+   +-------+---------+   +--------+--------+
         |                    |                       |
         |                    v                       |
         |         +----------+----------+           |
         |         |  User Input Command |           |
         |         +----------+----------+           |
         |                    |                      |
         |                    v                      v
         |         +----------+----------+  +--------+--------+
         |         | Add Command to Queue|  |Get Command from |
         |         +----------+----------+  |      Queue      |
         |                    |             +--------+--------+
         |                    |                      |
         |                    |                      v
         |                    +----------------+-----+-----+
         |                                     | Load Balance|
         |                                     | to Clients  |
         |                                     +-----+-----+
         |                                           |
         +-------------------------------------------+

This diagram illustrates the flow of the server component. The server starts by finding a free port, writing the server information to a file, and then listening for incoming client connections. Three main threads are spawned: "Handle Client," "Ask for Commands," and "Process Commands."

* The "Handle Client" thread manages client connections, receives output from clients, and handles client disconnections.
* The "Ask for Commands" thread prompts the user to enter commands and adds them to a queue.
* The "Process Commands" thread retrieves commands from the queue and load-balances them to the available clients.

### Client Flow

                    +---------------------+
                    |   Connect to Server |
                    +----------+----------+
                               |
                    +----------v----------+
                    |  Receive Command    |
                    +----------+----------+
                               |
                    +----------v----------+
                    |   Execute Command   |
                    +----------+----------+
                               |
                    +----------v----------+
                    |  Send Output to     |
                    |      Server         |
                    +----------+----------+
                               |
                               v
                    +----------+----------+
                    |   Log Output        |
                    +----------+----------+

This diagram illustrates the flow of the client component. The client first connects to the server using the server's host and port information. It then enters a loop where it receives commands from the server, executes them, sends the output back to the server, and logs the output in a client-specific log file.

### Demonstration
Start the server by running the server.py script: 
**python server.py**
The server will find a free port, write the server information to the server_info.txt file, and start listening for client connections.

Open one or more terminal windows and run the client.py script in each window:
**python client.py**
The clients will connect to the server using the information from the server_info.txt file.

In the server terminal, enter a command to be executed by the clients. For example:
**Enter command to send to clients (or 'exit' to quit): ls**
The server will distribute the command to the available clients in a load-balanced manner.

The clients will execute the command and send the output back to the server. The server will display the output received from the clients.
To stop the server and clients, enter the exit command in the server terminal.

### Logging
The clients log their activity and output in individual log files located in the logs directory. The log files are named client_<client_id>.log, where <client_id> is the unique ID assigned to the client by the server.

The server also logs the status of client connections and threads in the logs/thread_status.txt file.

### Dependencies
This project requires Python 3.x and the following libraries:

* socket
* threading
* queue
* itertools
* json
* atexit
* os
* time
* sys
* signal
No additional dependencies need to be installed.

### Contributing
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.


