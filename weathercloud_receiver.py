import socket
import requests
import logging
import time
import sys
from send_api_weathercloud_net import resolve_hostname, send_weathercloud

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

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

def send_to_iobroker(rainrate, max_retries=10):
    adapter_url = 'http://localhost:8087'
    state_id = 'javascript.0.Wetterstation.Weathercloud_Regenrate'
    url = f"{adapter_url}/set/{state_id}?value={rainrate}&ack=true"

    for _ in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info('Rainrate sent to ioBroker successfully.')
                return
            else:
                logging.warning(f'Failed to send data to ioBroker. Error: {response.status_code}')
        except requests.RequestException as e:
            logging.error(f'Network error: {e}')

        logging.info(f'Retrying in 5 seconds...')
        time.sleep(5)  # Fixed delay of 5 seconds

    logging.error(f'Failed to send data to ioBroker after {max_retries} attempts.')

def start_server():
    # Define the server's host and port
    host = 'localhost'
    port = 8882

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(10)

    client_socket = None
    try:
        # Bind the socket to the host and port
        server_socket.bind((host, port))
    except socket.error as e:
        logging.error(f'Failed to bind socket: {e}')
        sys.exit(1)

    # Listen for incoming connections
    server_socket.listen(1)
    logging.info(f"Listening on {host}:{port}...")

    while True:
        try:
            # Accept a client connection
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(10)
            logging.info(f"Received connection from {client_address[0]}:{client_address[1]}")

            # Receive data from the client
            data = client_socket.recv(1024)
            if data:
                logging.info(f"Received data: {data.decode()}")

                # Send the data to Weathercloud
                hostname = 'api.weathercloud.net'
                resolved_ip = resolve_hostname(hostname)
                if resolved_ip is not None:
                    logging.info(f"Resolved IP for {hostname}: {resolved_ip}")
                    send_weathercloud(resolved_ip, data)

                # Extract the rainrate parameter
                rainrate = extract_rainrate(data)
                if rainrate is not None:
                    logging.info(f"Rainrate in mm: {rainrate}")

                    # Send the rainrate value to ioBroker
                    send_to_iobroker(rainrate)

        except socket.error as e:
            logging.error(f'Socket error: {e}')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
        finally:
            if client_socket is not None:
                client_socket.close()

start_server()