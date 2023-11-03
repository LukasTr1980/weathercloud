import requests
import dns.resolver
import logging
import sys
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

def resolve_hostname(hostname):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ['8.8.8.8']
        answer = resolver.resolve(hostname, 'A')
        return str(answer[0])
    except Exception as e:
        logging.error(f'Error resolving hostname {hostname}: {e}')
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
        query_params = parse_qs(urlparse(query_string).query)
        for key, value in query_params.items():
            if key.startswith('wid'):
                params['wid'] = value[0]
            elif key in params:
                params[key] = value[0]

        logging.info(f'URL: {url}')
        logging.info(f'Params: {params}')
        logging.info(f'Headers: {headers}')

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        logging.info('Data sent successfully to Weathercloud.')
    except requests.exceptions.RequestException as e:
        logging.error(f'Network error sending data to Weathercloud: {e}')
    except Exception as e:
        logging.error(f'Unexpected error sending data to Weathercloud: {e}')
