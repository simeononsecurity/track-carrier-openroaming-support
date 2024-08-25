import dns.resolver
import time

def naptr_lookup(realm, resolver):
    """
    Perform NAPTR DNS lookup on the given realm using a specified resolver.
    """
    try:
        print(f"Performing NAPTR lookup for {realm} using resolver {resolver.nameservers[0]}")
        answers = resolver.resolve(realm, 'NAPTR', lifetime=5)
        for rdata in answers:
            print(f"Found NAPTR record: {rdata}")
            # Directly compare with a bytes literal
            if b'aaa+auth:radius.tls.tcp' in rdata.service.lower():
                return rdata.replacement.to_text().strip('.')
        print(f"No valid NAPTR record found for {realm}")
    except Exception as e:
        print(f"Error during NAPTR lookup for {realm}: {e}")
    return None

def srv_lookup(host, resolver):
    """
    Perform SRV DNS lookup on the given host using a specified resolver.
    """
    try:
        print(f"Performing SRV lookup for {host} using resolver {resolver.nameservers[0]}")
        answers = resolver.resolve(host, 'SRV', lifetime=5)
        for rdata in sorted(answers, key=lambda r: r.priority):
            print(f"Found SRV record: {rdata}")
            if validate_host(rdata.target.to_text().strip('.')):
                return rdata.target.to_text().strip('.'), rdata.port
        print(f"No valid SRV record found for {host}")
    except Exception as e:
        print(f"Error during SRV lookup for {host}: {e}")
    return None, None

def validate_host(host):
    """
    Validate host format.
    """
    return all(c.isalnum() or c in '-._' for c in host)

def setup_resolvers():
    """
    Setup DNS resolvers with both system defaults and custom DNS servers.
    """
    resolver_list = []
    # Use system default resolver
    resolver_list.append(dns.resolver.Resolver())
    # Add custom DNS servers
    dns_servers = ['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4', '9.9.9.9']
    for server in dns_servers:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]
        resolver_list.append(resolver)
    return resolver_list

def check_realm_existence(resolvers):
    """
    Check if the specific realm 'wlan.mnc280.mcc310.pub.3gppnetwork.org' exists by performing NAPTR and SRV lookups.
    Returns True if a valid realm is found, along with the host and port.
    """
    # Hardcoded realm URL for testing
    realm_url_pub = "wlan.mnc280.mcc310.pub.3gppnetwork.org"

    # Rotate through DNS resolvers to balance the load
    for resolver in resolvers:
        srv_host = naptr_lookup(realm_url_pub, resolver)
        if srv_host:
            host, port = srv_lookup(srv_host, resolver)
            if host and port:
                print(f"Successful lookup: {realm_url_pub} -> {host}:{port} using resolver {resolver.nameservers[0]}")
                return True, host, port  # Stop as soon as we find a valid result

        # Introduce a short delay between queries to avoid rate limiting
        time.sleep(1)

    return False, None, None

def main():
    # Setup DNS resolvers with both system default and specified DNS servers
    resolvers = setup_resolvers()

    # Check the specific realm existence
    realm_exists, host, port = check_realm_existence(resolvers)

    if realm_exists:
        print(f"Success: wlan.mnc280.mcc310.pub.3gppnetwork.org -> {host}:{port}")
    else:
        print("No valid NAPTR/SRV records found for wlan.mnc280.mcc310.pub.3gppnetwork.org")

if __name__ == "__main__":
    main()
