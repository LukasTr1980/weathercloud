import requests
import dns.resolver

def resolve_hostname(hostname):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ['8.8.8.8']
        answer = resolver.resolve(hostname, 'A')
        return str(answer[0])
    except:
        print(f'Error resolving hostname {hostname}')
        return None

def send_weathercloud(ip_address, data):
    endpoint = '/v01/set'

    url = f'http://{ip_address}{endpoint}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }

    try:
        # Extract the query string parameters from the received data
        params = {}
        query_string = data.decode().split(' ')[1]  # Get the query string from the HTTP GET request
        query_params = query_string.split('&')  # Split the query string into individual parameters
        for param in query_params:
            key, value = param.split('=')
            params[key] = value

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception if the status code indicates an error
        print('Data sent successfully to Weathercloud.')
    except requests.exceptions.RequestException as e:
        print('Error sending data to Weathercloud:', e)
