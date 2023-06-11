import socket
import requests

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

def send_to_iobroker(wdir):
    # ioBroker Simple API Adapter configuration
    adapter_url = 'http://localhost:8087'
    state_id = 'javascript.0.Wetterstation.Weathercloud_Regenrate'  # Replace with the actual state ID in ioBroker

    # Prepare the URL with the value
    url = f"{adapter_url}/set/{state_id}?value={wdir}&ack=true"

    # Send the data to ioBroker
    response = requests.get(url)
    if response.status_code == 200:
        print('Data sent to ioBroker successfully.')
    else:
        print(f'Failed to send data to ioBroker. Error: {response.status_code}')

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

                # Send the wind direction value to ioBroker
                send_to_iobroker(wdir)

        # Close the client connection
        client_socket.close()

# Start the server
start_server()
