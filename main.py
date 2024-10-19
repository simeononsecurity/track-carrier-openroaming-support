from mccmnc import find_matches, print_matches, update
import json
import os
import dns.resolver
from tqdm import tqdm
import mccmnc  # Import the mccmnc module to find its installation path
import time

def get_mccmnc_json_path():
    """
    Dynamically locate the path to the mccmnc.json file based on where the mccmnc module is installed.

    Returns:
        str: Path to the mccmnc.json file.
    """
    mccmnc_dir = os.path.dirname(mccmnc.__file__)
    json_path = os.path.join(mccmnc_dir, 'mccmnc.json')
    return json_path

def load_json_file(json_path):
    """
    Load data from the specified JSON file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        dict: Loaded JSON data.
    """
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {}

def save_json_file(data, json_path):
    """
    Save data to the specified JSON file.

    Args:
        data (dict): Data to be saved.
        json_path (str): Path to the JSON file.
    """
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"JSON data updated in {json_path}")

def construct_realm_url(mcc, mnc, nid=None, service_id=None, use_pub=False):
    """
    Construct the realm URL using MCC, MNC, NID, and service ID values.
    If use_pub is True, use 'pub.3gppnetwork.org' instead of '3gppnetwork.org'.

    Args:
        mcc (int): Mobile Country Code (3-digit).
        mnc (int): Mobile Network Code (2 or 3-digit).
        nid (str, optional): NID identifying a Stand-alone Non-Public Network (SNPN).
        service_id (str, optional): Service ID that describes the service or operation.
        use_pub (bool, optional): Whether to use 'pub.3gppnetwork.org' instead of '3gppnetwork.org'.

    Returns:
        str: Constructed realm URL.
    """
    realm_suffix = "pub.3gppnetwork.org" if use_pub else "3gppnetwork.org"
    mnc_str = f"{mnc:03d}"
    mcc_str = f"{mcc:03d}"

    if nid:
        realm = f"wlan.nid{nid}.mnc{mnc_str}.mcc{mcc_str}.{realm_suffix}"
    else:
        realm = f"wlan.mnc{mnc_str}.mcc{mcc_str}.{realm_suffix}"

    if service_id:
        realm = f"{service_id}.{realm}"

    return realm

def validate_host(host):
    """
    Validate host format.

    Args:
        host (str): Hostname to be validated.

    Returns:
        bool: True if the host format is valid, False otherwise.
    """
    return all(c.isalnum() or c in '-._' for c in host)

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
            if validate_host(rdata.target.to_text().strip('.')):
                return rdata.target.to_text().strip('.'), rdata.port
        print(f"No valid SRV record found for {host}")
    except Exception as e:
        print(f"Error during SRV lookup for {host}: {e}")
    return None, None

def check_realm_existence(mcc, mnc, resolvers):
    """
    Check if the realm exists by performing NAPTR and SRV lookups.

    Args:
        mcc (int): Mobile Country Code (3-digit).
        mnc (int): Mobile Network Code (2 or 3-digit).
        resolvers (list): List of DNS resolvers to use for lookups.

    Returns:
        tuple: A tuple containing a boolean indicating success, the host, and the port.
    """
    # Construct initial realm URL for the .pub domain
    realm_url_pub = construct_realm_url(mcc, mnc, use_pub=True)

    # Rotate through DNS resolvers to balance the load
    for resolver in resolvers:
        srv_host = naptr_lookup(realm_url_pub, resolver)
        if srv_host:
            host, port = srv_lookup(srv_host, resolver)
            if host and port:
                print(f"Successful lookup: {realm_url_pub} -> {host}:{port} using resolver {resolver.nameservers[0]}")
                return True, host, port  # Stop as soon as we find a valid result

        # Introduce a short delay between queries to avoid rate limiting
        time.sleep(0.2)

    return False, None, None

def get_all_active_mcc_mnc():
    """
    Update the database, load existing data, and check realm existence
    for each MCC-MNC combination with a progress indicator, updating only new or changed data.
    """
    # Update the local database to ensure we have the latest data
    update()

    # Paths to JSON files
    original_json_path = get_mccmnc_json_path()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_json_path = os.path.join(current_dir, 'data', 'mccmnc.json')

    # Load data from the original and local JSON files
    original_data = load_json_file(original_json_path)
    local_data = load_json_file(local_json_path)

    # Setup DNS resolvers with specified DNS servers
    resolvers = setup_resolvers()
    
    # Progress indicator setup
    total = len(original_data)
    with tqdm(total=total, desc="Processing MCC-MNC combinations") as pbar:
        for key, value in original_data.items():
            mcc = int(value['MCC'])
            mnc = int(value['MNC'])

            # Always perform the lookup to ensure latest results
            realm_exists, host, port = check_realm_existence(mcc, mnc, resolvers)
            local_data[key] = value  # Update entry with MCC and MNC details
            local_data[key]['lookup_success'] = realm_exists

            if realm_exists:
                local_data[key]['host'] = host
                local_data[key]['port'] = port
                print(f"Success: {construct_realm_url(mcc, mnc, use_pub=True)} -> {host}:{port}")

            # Update progress bar
            pbar.update(1)

    # Save updated local data back to the local JSON file
    save_json_file(local_data, local_json_path)

if __name__ == "__main__":
    get_all_active_mcc_mnc()
