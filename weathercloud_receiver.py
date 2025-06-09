import socket
import requests
import logging
import time
import sys
import threading
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from send_api_weathercloud_net import resolve_hostname, send_weathercloud

load_dotenv()

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

    user = os.getenv('IOBROKER_USER')
    password = os.getenv('IOBROKER_PASSWORD')

    #----- Check if the environment variables are set
    for var, val in [('IOBROKER_USER', user), ('IOBROKER_PASSWORD', password)]:
        if not val:
            logging.warning(f"{var} is not set. Please check your .env file.")
        elif "PASS" in var:
            logging.info(f"{var}: {'*'*len(val)} (Len {len(val)})")
        else:
            logging.info(f"{var}: {val}")

    #----- Prepare the URL with authentication if needed
    params = {"value": rainrate, "ack": "true"}
    if user and password:
        params.update({"user": user, "pass": password})
    
    url = f"{adapter_url}/set/{state_id}"
    masked_url = f"{url}?{urlencode(params).replace(password or '', '*'*len(password or ''))}"
    logging.info(f"-> Call (PW masked): {masked_url}")

    auth_params = f"&user={user}&pass={password}" if user and password else ''
    url = f"{adapter_url}/set/{state_id}?value={rainrate}&ack=true{auth_params}"

    for _ in range(max_retries):
        try:
            response = requests.get(url, timeout=10)  # Added timeout
            if response.status_code == 200:
                logging.info('Rainrate sent to ioBroker successfully.')
                return
            else:
                logging.warning(f'Failed to send data to ioBroker. Error: {response.status_code}')
        except requests.RequestException as e:
            logging.error(f'Network error: {e}')

        logging.info(f'Retrying in 5 seconds...')
        time.sleep(5)

    logging.error(f'Failed to send data to ioBroker after {max_retries} attempts.')

def start_server():
    host = 'localhost'
    port = 8882

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = None

    try:
        server_socket.bind((host, port))
    except socket.error as e:
        logging.error(f'Failed to bind socket: {e}')
        sys.exit(1)

    server_socket.listen(1)
    logging.info(f"Listening on {host}:{port}...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(10)
            logging.info(f"Received connection from {client_address[0]}:{client_address[1]}")

            data = client_socket.recv(1024)
            if data:
                logging.info(f"Received data: {data.decode()}")

                hostname = 'api.weathercloud.net'
                resolved_ip = resolve_hostname(hostname)
                if resolved_ip is not None:
                    logging.info(f"Resolved IP for {hostname}: {resolved_ip}")
                    threading.Thread(target=send_weathercloud, args=(resolved_ip, data)).start()  # Using threading

                rainrate = extract_rainrate(data)
                if rainrate is not None:
                    logging.info(f"Rainrate in mm: {rainrate}")
                    send_to_iobroker(rainrate)

        except socket.error as e:
            logging.error(f'Socket error: {e}')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
        finally:
            if client_socket is not None:
                client_socket.close()

if __name__ == "__main__":
    start_server()
