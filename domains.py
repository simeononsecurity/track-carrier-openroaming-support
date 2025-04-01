import json
import os
import dns.resolver
import time
from tqdm import tqdm

def setup_resolvers():
    """
    Setup DNS resolvers with custom DNS servers, rotating through them.

    Returns:
        list: List of configured DNS resolvers.
    """
    resolver_list = []
    dns_servers = ['1.1.1.1', '8.8.8.8', '9.9.9.9', "208.67.222.222", "8.26.56.26", "76.76.2.0"]
    for server in dns_servers:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]
        resolver_list.append(resolver)
    return resolver_list

def naptr_lookup(realm, resolver):
    """
    Perform NAPTR DNS lookup on the given realm using a specified resolver.

    Args:
        realm (str): The realm to perform the NAPTR lookup on.
        resolver (dns.resolver.Resolver): The DNS resolver to use for the lookup.

    Returns:
        str: Replacement value from the NAPTR record if found, otherwise None.
    """
    try:
        print(f"Performing NAPTR lookup for {realm} using resolver {resolver.nameservers[0]}")
        answers = resolver.resolve(realm, 'NAPTR', lifetime=5)
        for rdata in answers:
            print(f"Found NAPTR record: {rdata}")
            # Use bytes literal for comparison
            if b'aaa+auth:radius.tls.tcp' in rdata.service.lower():
                return rdata.replacement.to_text().strip('.')
        print(f"No valid NAPTR record found for {realm}")
    except Exception as e:
        print(f"Error during NAPTR lookup for {realm}: {e}")
    return None

def srv_lookup(host, resolver):
    """
    Perform SRV DNS lookup on the given host using a specified resolver.

    Args:
        host (str): The hostname to perform the SRV lookup on.
        resolver (dns.resolver.Resolver): The DNS resolver to use for the lookup.

    Returns:
        tuple: A tuple containing the target host and port if found, otherwise (None, None).
    """
    try:
        print(f"Performing SRV lookup for {host} using resolver {resolver.nameservers[0]}")
        answers = resolver.resolve(host, 'SRV', lifetime=5)
        for rdata in sorted(answers, key=lambda r: r.priority):
            print(f"Found SRV record: {rdata}")
            return rdata.target.to_text().strip('.'), rdata.port
        print(f"No valid SRV record found for {host}")
    except Exception as e:
        print(f"Error during SRV lookup for {host}: {e}")
    return None, None

def create_json_dict_for_domains(domains, resolvers, fallback_records):
    """
    Perform NAPTR and SRV lookups for given domains and create a JSON dictionary for them.
    If no NAPTR or SRV record is found, use fallback records if available.

    Args:
        domains (list): List of domains to perform lookups for.
        resolvers (list): List of DNS resolvers to use for lookups.
        fallback_records (dict): Dictionary of fallback records for domains without NAPTR.

    Returns:
        dict: JSON dictionary with lookup results.
    """
    domain_results = {}

    # Progress indicator setup
    with tqdm(total=len(domains), desc="Processing domains") as pbar:
        for domain in domains:
            srv_host, srv_port = None, None

            # Rotate through DNS resolvers to balance the load
            for resolver in resolvers:
                srv_host = naptr_lookup(domain, resolver)
                if srv_host:
                    # Try SRV lookup after NAPTR if a host is found
                    srv_host, srv_port = srv_lookup(srv_host, resolver)
                    if srv_host and srv_port:
                        break
                # Introduce a short delay between queries to avoid rate limiting
                time.sleep(0.1)

            if srv_host and srv_port:
                domain_results[domain] = {"host": srv_host, "port": srv_port}
            elif domain in fallback_records:
                domain_results[domain] = {"host": fallback_records[domain]["host"], "port": fallback_records[domain]["port"]}
                print(f"Using fallback record for {domain}: {fallback_records[domain]}")
            else:
                domain_results[domain] = {"host": None, "port": None, "note": "No NAPTR or SRV record found and no fallback available"}
                print(f"No NAPTR or SRV record or fallback available for {domain}")

            # Update progress bar
            pbar.update(1)

    return domain_results

def save_json_file(data, json_path):
    """
    Save data to the specified JSON file.

    Args:
        data (dict): Data to be saved.
        json_path (str): Path to the JSON file.
    """
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"JSON data saved in {json_path}")

def main():
    # List of domains to perform lookups for
    domains = [
        "wlan.mnc260.mcc310.3gppnetwork.org",
        "wlan.mnc240.mcc310.3gppnetwork.org",
        "wlan.mnc310.mcc310.3gppnetwork.org",
        "wlan.mnc314.mcc330.3gppnetwork.org",
        "samsung.openroaming.net",
        "openroaming.goog",
        "spectrum.net",
        "wifi.fi.google.com",
        "prod.premnet.wefi.com",
        "globalro.am",
        "dummy.openroaming.wefi.com",
        "prod.openroaming.wefi.com",
        "charter.net",
        "gmail.com",
        "aka.xfinitymobile.com",
        "rr.com",
        "wba.3af521.net",
        "sdk.openroaming.net",
        "xfinitymobile.com",
        "w-jp2.wi2.cityroam.jp",
        "openroaming.securewifi.io",
        "yahoo.com",
        "profile.guglielmo.biz",
        "ciscoid.openroaming.net",
        "test.orportal.org",
        "icloud.com",
        "tulane.edu",
        "apple.openroaming.net",
        "umich.edu",
        "google.openroaming.net",
        "wisc.edu",
        "clus.openroaming.net",
        "hotmail.com",
        "uconnect.utah.edu",
        "tokyo.wi2.cityroam.jp",
        "kwikboost.com",
        "swarthmore.edu",
        "naturalbornorganizers.com",
        "outlook.com",
        "rioog.com",
        "almhem.net",
        "mac.com",
        "castlecegal.com",
        "delhaize.openroaming.net",
        "xfinity.com",
        "w-jp1.wi2.cityroam.jp",
        "wayru.io",
        "jwa.bemap.cityroam.jp",
        "or1.guglielmo.biz",
        "wayfiwireless.com",
        "dogwood120.net",
        "orionwifi.com",
        "orion.area120.com",
        "ironwifi.net",
        "securewifi.purple.ai"
    ]

    # Fallback records for domains without NAPTR
    fallback_records = {
        "wlan.mnc260.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc240.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc310.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc314.mcc330.3gppnetwork.org": {"host": ["52.37.147.195", "44.229.62.214", "44.241.107.197"], "port": 2083},
        "freedomfi.com": {"host": ["52.37.147.195", "44.229.62.214", "44.241.107.197"], "port": 2083},
        "hellohelium.com": {"host": ["52.37.147.195", "44.229.62.214", "44.241.107.197"], "port": 2083}
    }

    # Setup DNS resolvers with specified DNS servers
    resolvers = setup_resolvers()

    # Perform lookups and create JSON dictionary
    domain_results = create_json_dict_for_domains(domains, resolvers, fallback_records)

    # Save results to a JSON file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'data', 'domain_lookup_results.json')
    save_json_file(domain_results, json_path)

if __name__ == "__main__":
    main()
