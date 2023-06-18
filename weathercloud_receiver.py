import socket
import requests
import dns.resolver
from send_api_weathercloud_net import resolve_hostname, send_weathercloud

def extract_rainrate(data):
    # Convert the received data to a string
    data = data.decode()
    lines = data.split('\n')  # Split the data into lines

    # Loop through the lines and find the line containing 'rainrate='
    for line in lines:
        if 'rainrate=' in line:
            start_index = line.index('rainrate=') + len('rainrate=')
            end_index = line.index('&', start_index)  # Find the end index of the value
            rainrate_mm = line[start_index:end_index]  # Extract the rainrate value in millimeters as a string
            return rainrate_mm

    return None

def send_to_iobroker(rainrate):
    # ioBroker Simple API Adapter configuration
    adapter_url = 'http://localhost:8087'
    state_id = 'javascript.0.Wetterstation.Weathercloud_Regenrate'  # Replace with the actual state ID in ioBroker

    # Prepare the URL with the value
    url = f"{adapter_url}/set/{state_id}?value={rainrate}&ack=true"

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

            # Send the data to Weathercloud
            resolved_ip = resolve_hostname('api.weathercloud.net')
            if resolved_ip is not None:
                print("Resolved IP:", resolved_ip)
                send_weathercloud(resolved_ip, data)

            # Extract the rainrate parameter
            rainrate = extract_rainrate(data)
            if rainrate is not None:
                print("Rainrate in mm:", rainrate)

                # Send the rainrate value to ioBroker
                send_to_iobroker(rainrate)

        # Close the client connection
        client_socket.close()

# Start the server
start_server()