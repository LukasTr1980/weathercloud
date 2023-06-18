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
        response = requests.get(url, params=data, headers=headers)
        response.raise_for_status()  # Raise an exception if the status code indicates an error
        print('Data sent successfully')
    except requests.exceptions.RequestException as e:
        print('Error sending data:', e)