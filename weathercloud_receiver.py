import urllib.parse
import requests
import socket
from dns_resolver import resolve_dns

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

def forward_to_weathercloud(ip_address, request):
    # Extract the parameters from the HTTP GET request
    params = urllib.parse.parse_qs(urllib.parse.urlparse(request).query)
    wid = params['wid'][0]
    key = params['key'][0]
    date = params['date'][0]
    time = params['time'][0]
    tempin = params['tempin'][0]
    humin = params['humin'][0]
    temp = params['temp'][0]
    hum = params['hum'][0]
    temp1 = params['temp1'][0]
    hum1 = params['hum1'][0]
    dewin = params['dewin'][0]
    dew = params['dew'][0]
    dew1 = params['dew1'][0]
    chill = params['chill'][0]
    chill1 = params['chill1'][0]
    heatin = params['heatin'][0]
    heat = params['heat'][0]
    heat1 = params['heat1'][0]
    thw = params['thw'][0]
    thw1 = params['thw1'][0]
    bar = params['bar'][0]
    wspd = params['wspd'][0]
    wspdhi = params['wspdhi'][0]
    wdir = params['wdir'][0]
    wspdavg = params['wspdavg'][0]
    wdiravg = params['wdiravg'][0]
    rainrate = params['rainrate'][0]
    rain = params['rain'][0]
    solarrad = params['solarrad'][0]
    uvi = params['uvi'][0]
    battery = params['battery'][0]
    battery1 = params['battery1'][0]
    ver = params['ver'][0]
    type = params['type'][0]

    # Send the data to Weathercloud using an HTTP GET request
    url = f'http://{ip_address}/v01/set?wid={wid}&key={key}&date={date}&time={time}&tempin={tempin}&humin={humin}&temp={temp}&hum={hum}&temp1={temp1}&hum1={hum1}&dewin={dewin}&dew={dew}&dew1={dew1}&chill={chill}&chill1={chill1}&heatin={heatin}&heat={heat}&heat1={heat1}&thw={thw}&thw1={thw1}&bar={bar}&wspd={wspd}&wspdhi={wspdhi}&wdir={wdir}&wspdavg={wspdavg}&wdiravg={wdiravg}&rainrate={rainrate}&rain={rain}&solarrad={solarrad}&uvi={uvi}&battery={battery}&battery1={battery1}&ver={ver}&type={type}'
    response = requests.get(url)

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

                # Send the rainrate value to ioBroker
                send_to_iobroker(rainrate)
                
                # Get the IP address of weathercloud.net
                #ip_address = resolve_dns()

                # Send all data to weathercloud.net via HTTPS
                #forward_to_weathercloud(ip_address, data)

        # Close the client connection
        client_socket.close()

# Start the server
start_server()