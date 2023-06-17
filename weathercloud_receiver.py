import urllib.parse
import requests
import socket
import dns.resolver

# Specify the IP address of the DNS server you want to use
dns_server = '8.8.8.8'

# Configure a custom resolver using the specified DNS server
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [dns_server]

# Use the custom resolver in the requests module
requests.adapters.DEFAULT_RETRIES = 3  # Increase the number of retries
requests.adapters.DEFAULT_NAMESERVERS = resolver.nameservers

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

def forward_to_weathercloud(request):
    # Extract the parameters from the HTTP GET request
    parsed_request = urllib.parse.urlparse(request.decode())
    params = urllib.parse.parse_qs(parsed_request.query)

    wid = params.get('wid', [''])[0]
    key = params.get('key', [''])[0]
    date = params.get('date', [''])[0]
    time = params.get('time', [''])[0]
    tempin = params.get('tempin', [''])[0]
    humin = params.get('humin', [''])[0]
    temp = params.get('temp', [''])[0]
    hum = params.get('hum', [''])[0]
    temp1 = params.get('temp1', [''])[0]
    hum1 = params.get('hum1', [''])[0]
    dewin = params.get('dewin', [''])[0]
    dew = params.get('dew', [''])[0]
    dew1 = params.get('dew1', [''])[0]
    chill = params.get('chill', [''])[0]
    chill1 = params.get('chill1', [''])[0]
    heatin = params.get('heatin', [''])[0]
    heat = params.get('heat', [''])[0]
    heat1 = params.get('heat1', [''])[0]
    thw = params.get('thw', [''])[0]
    thw1 = params.get('thw1', [''])[0]
    bar = params.get('bar', [''])[0]
    wspd = params.get('wspd', [''])[0]
    wspdhi = params.get('wspdhi', [''])[0]
    wdir = params.get('wdir', [''])[0]
    wspdavg = params.get('wspdavg', [''])[0]
    wdiravg = params.get('wdiravg', [''])[0]
    rainrate = params.get('rainrate', [''])[0]
    rain = params.get('rain', [''])[0]
    solarrad = params.get('solarrad', [''])[0]
    uvi = params.get('uvi', [''])[0]
    battery = params.get('battery', [''])[0]
    battery1 = params.get('battery1', [''])[0]
    ver = params.get('ver', [''])[0]
    type = params.get('type', [''])[0]

    # Send the data to Weathercloud using an HTTP GET request
    url = f'https://api.weathercloud.net/v01/set?wid={wid}&key={key}&date={date}&time={time}&tempin={tempin}&humin={humin}&temp={temp}&hum={hum}&temp1={temp1}&hum1={hum1}&dewin={dewin}&dew={dew}&dew1={dew1}&chill={chill}&chill1={chill1}&heatin={heatin}&heat={heat}&heat1={heat1}&thw={thw}&thw1={thw1}&bar={bar}&wspd={wspd}&wspdhi={wspdhi}&wdir={wdir}&wspdavg={wspdavg}&wdiravg={wdiravg}&rainrate={rainrate}&rain={rain}&solarrad={solarrad}&uvi={uvi}&battery={battery}&battery1={battery1}&ver={ver}&type={type} HTTP/1.1'
    
    print("Sending data to Weathercloud:")
    print(url)
    
    response = requests.get(url)
    print("Used IP address:", response.request.url)
    print("Response from Weathercloud:", response.status_code, response.reason)

    # Return the response from Weathercloud to the client making the original request
    return response.content

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
        try:
            # Accept a client connection
            client_socket, client_address = server_socket.accept()
            print(f"Received connection from {client_address[0]}:{client_address[1]}")

            # Receive data from the client
            data = client_socket.recv(1024)
            if data:
                print("Received data:")
                print(data.decode())

                # Extract the rainrate parameter
                rainrate = extract_rainrate(data)
                if rainrate is not None:
                    print("Rainrate in mm:", rainrate)

                    try:
                        # Send the rainrate value to ioBroker
                        send_to_iobroker(rainrate)
                    except Exception as e:
                        print(f"An error occurred while sending to ioBroker: {str(e)}")
                        # Handle the exception for sending to ioBroker here

                    try:
                        # Send all data to weathercloud.net via HTTPS
                        response = forward_to_weathercloud(data)

                        # Send the response from Weathercloud back to the client
                        client_socket.send(response)
                    except Exception as e:
                        print(f"An error occurred while forwarding to Weathercloud: {str(e)}")
                        # Handle the exception for forwarding to Weathercloud here

            # Close the client connection
            client_socket.close()

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # Handle other exceptions here if needed

# Start the server
start_server()
