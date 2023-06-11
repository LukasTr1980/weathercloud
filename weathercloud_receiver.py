import socket
import requests

def extract_rainrate(data):
    # Convert the data to a string
    data_str = data.decode('utf-8')

    # Split the data into lines
    lines = data_str.split('\n')

    # Search for the rainrate parameter in the lines
    for line in lines:
        if 'wdir=' in line:
            # Extract the rainrate value from the line
            rainrate = line.split('=')[1]

            # Convert the rainrate value to a float
            rainrate = float(rainrate)

            # Return the rainrate value
            return rainrate

    return None

def set_rainrate(saved_rainrate):
    # Define the Simple API endpoint URL
    url = 'http://localhost:8087/setObject'

    # Define the object ID and value to set
    object_id = 'javascript.0.Wetterstation.Weathercloud_Regenrate'

    # Define the request body as a JSON object
    data = {
        'id': object_id,
        'val': saved_rainrate
    }

    # Send the HTTP POST request to the Simple API endpoint
    response = requests.post(url, json=data)

    # Check the response status code
    if response.status_code != 200:
        print('Error setting value:', response.text)
    else:
        print('Value set successfully:', saved_rainrate)

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

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        # Receive data from the client
        data = client_socket.recv(1024)
        if data:
            # Extract the rainrate parameter
            rainrate = extract_rainrate(data)
            if rainrate is not None:
                # Save the rainrate value to a variable
                saved_rainrate = rainrate

                # Set the rainrate value in ioBroker using the Simple API
                set_rainrate(saved_rainrate)
            else:
                print('No rainrate parameter found in request:', data)

        # Close the client connection
        client_socket.close()

# Start the server
start_server()