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
    dns_servers = ['1.1.1.1', '8.8.8.8', '9.9.9.9']
    for server in dns_servers:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]
        resolver_list.append(resolver)
    return resolver_list

def naptr_lookup(domain, resolver):
    """
    Perform NAPTR DNS lookup on the given domain using a specified resolver.

    Args:
        domain (str): The domain to perform the NAPTR lookup on.
        resolver (dns.resolver.Resolver): The DNS resolver to use for the lookup.

    Returns:
        str: Replacement value from the NAPTR record if found, otherwise None.
    """
    try:
        print(f"Performing NAPTR lookup for {domain} using resolver {resolver.nameservers[0]}")
        answers = resolver.resolve(domain, 'NAPTR', lifetime=5)
        for rdata in answers:
            print(f"Found NAPTR record: {rdata}")
            if b'aaa+auth:radius.tls.tcp' in rdata.service.lower():
                return rdata.replacement.to_text().strip('.')
        print(f"No valid NAPTR record found for {domain}")
    except Exception as e:
        print(f"Error during NAPTR lookup for {domain}: {e}")
    return None

def create_json_dict_for_domains(domains, resolvers, fallback_records):
    """
    Perform NAPTR lookups for given domains and create a JSON dictionary for them.
    If no NAPTR record is found, use fallback records if available.

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
                    srv_port = 2083  # Default port for radius.tls.tcp
                    break
                # Introduce a short delay between queries to avoid rate limiting
                time.sleep(0.2)

            if srv_host:
                domain_results[domain] = {"host": srv_host, "port": srv_port}
            elif domain in fallback_records:
                domain_results[domain] = {"host": fallback_records[domain]["host"], "port": fallback_records[domain]["port"]}
                print(f"Using fallback record for {domain}: {fallback_records[domain]}")
            else:
                domain_results[domain] = {"host": None, "port": None, "note": "No NAPTR record found and no fallback available"}
                print(f"No NAPTR record or fallback available for {domain}")

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
        "c2k2q8e2pcs2udar1pa0.orion.area120.com",
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
        "c1np0kb17dk2elvk96a0.orion.area120.com",
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
    ]

    # Fallback records for domains without NAPTR
    fallback_records = {
        "wlan.mnc260.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc240.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc310.mcc310.3gppnetwork.org": {"host": "aaa.geo.t-mobile.com", "port": 2083},
        "wlan.mnc314.mcc330.3gppnetwork.org": {"host": ["52.37.147.195", "44.229.62.214", "44.241.107.197"], "port": 2083}
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
