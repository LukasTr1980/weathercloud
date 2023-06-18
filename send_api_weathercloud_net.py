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
        params = {
            'wid': '',
            'key': '',
            'date': '',
            'time': '',
            'tempin': '',
            'humin': '',
            'temp': '',
            'hum': '',
            'temp1': '',
            'hum1': '',
            'dewin': '',
            'dew': '',
            'dew1': '',
            'chill': '',
            'chill1': '',
            'heatin': '',
            'heat': '',
            'heat1': '',
            'thw': '',
            'thw1': '',
            'bar': '',
            'wspd': '',
            'wspdhi': '',
            'wdir': '',
            'wspdavg': '',
            'wdiravg': '',
            'rainrate': '',
            'rain': '',
            'solarrad': '',
            'uvi': '',
            'battery': '',
            'battery1': '',
            'ver': '',
            'type': ''
        }

        query_string = data.decode().split(' ')[1]
        query_params = query_string.split('&')
        for param in query_params:
            if '=' in param:
                key, value = param.split('=')
                if key in params:
                    params[key] = value

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        print('Data sent successfully to Weathercloud.')
    except requests.exceptions.RequestException as e:
        print('Error sending data to Weathercloud:', e)
