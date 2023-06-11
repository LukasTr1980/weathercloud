import socket

def extract_wdir(data):
    # Convert the received data to a string
    data = data.decode()
    lines = data.split('\n')  # Split the data into lines

    # Loop through the lines and find the line containing 'wdir='
    for line in lines:
        if 'wdir=' in line:
            start_index = line.index('wdir=') + len('wdir=')
            end_index = line.index('&', start_index)  # Find the end index of the value
            wdir = line[start_index:end_index]  # Extract the wind direction value
            return wdir

    return None

def start_server():
    # Define the server's host and port
    host = 'localhost'
    port = 8882

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Listening on {host}:{port}...")

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print(f"Received connection from {client_address[0]}:{client_address[1]}")

        # Receive data from the client
        data = client_socket.recv(1024)
        if data:
            print("Received data:")
            print(data.decode())

            # Extract the wind direction parameter
            wdir = extract_wdir(data)
            if wdir is not None:
                print("Wind Direction:", wdir)

        # Close the client connection
        client_socket.close()

# Start the server
start_server()
