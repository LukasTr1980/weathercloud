import dns.resolver

def resolve_dns():
    # Define the domain name to resolve
    domain_name = 'api.weathercloud.net'

    # Create a resolver object
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']

    try:
        # Make the DNS query for the A record of the domain
        response = resolver.resolve(domain_name, 'A')
        ip_addresses = [str(rdata) for rdata in response]
        print(f"The IP addresses of {domain_name} are: {', '.join(ip_addresses)}")
    except dns.resolver.NXDOMAIN:
        print(f"The domain {domain_name} does not exist.")
    except dns.exception.DNSException as e:
        print(f"An error occurred: {e}")

resolve_dns()