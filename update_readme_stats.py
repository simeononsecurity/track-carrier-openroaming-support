import json
import os
from tabulate import tabulate

# Paths to the JSON data and README file
json_file_path = 'data/mccmnc.json'
domain_lookup_json_path = 'data/domain_lookup_results.json'  # New JSON file for domains lookup results
readme_file_path = 'README.md'

# Load data from the mccmnc.json file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Initialize counters and lists
total_count = 0
supported_count = 0
unsupported_count = 0
supported_list = []

# Process data to calculate support stats and build the supported list
for plmnid, details in data.items():
    total_count += 1
    if details.get('lookup_success'):
        supported_count += 1
        supported_list.append([details['NETWORK'], details['COUNTRY'], details['MCC'], details['MNC'], details['host'], details['port']])
    else:
        unsupported_count += 1

# Calculate support percentages
supported_percent = (supported_count / total_count) * 100 if total_count > 0 else 0
unsupported_percent = (unsupported_count / total_count) * 100 if total_count > 0 else 0

# Create the tables
support_table = [
    ["OpenRoaming Supported", f"{supported_percent:.2f}%"],
    ["OpenRoaming Unsupported", f"{unsupported_percent:.2f}%"]
]

supported_table = supported_list

# Generate markdown tables using tabulate
support_table_md = tabulate(support_table, headers=["Status", "Percentage"], tablefmt="github")
supported_table_md = tabulate(supported_table, headers=["Network", "Country", "MCC", "MNC", "Host", "Port"], tablefmt="github")

# Load data from the domain_lookup_results.json file (New section)
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory path
domain_lookup_json_path = os.path.join(current_dir, 'data', 'domain_lookup_results.json')

# Load domain lookup data
with open(domain_lookup_json_path, 'r') as domain_file:
    domain_lookup_data = json.load(domain_file)

# Process the domain lookup data to create a table, excluding domains with null host or port,
# and duplicating rows if host contains multiple entries.
domain_results_list = []
for domain, details in domain_lookup_data.items():
    host = details.get('host')
    port = details.get('port')

    # Only add domains to the list if host and port are not None
    if host and port:
        # If host is a list, create a row for each host entry
        if isinstance(host, list):
            for individual_host in host:
                domain_results_list.append([domain, individual_host, port])
        else:
            # If host is a single value, just add it as usual
            domain_results_list.append([domain, host, port])

# Generate markdown table for domain lookup results
domain_lookup_md = tabulate(domain_results_list, headers=["Domain", "Host", "Port"], tablefmt="github")

# Read the README file
with open(readme_file_path, 'r') as file:
    readme_content = file.read()

# Prepare the updated content with tables
tables_section = f"""
## OpenRoaming Support Status
{support_table_md}

## Supported Carriers
{supported_table_md}
> Note 310:280 is also AT&T, the used data set is wrong on that one.

## Realm Lookup Results
> A few realms we've identified from public certificates, public documentation, and authentication attempts.
{domain_lookup_md}
"""

# Replace the content between the comments
start_marker = '<!-- Tables Start -->'
end_marker = '<!-- Tables End -->'
updated_content = readme_content.split(start_marker)[0] + start_marker + tables_section + end_marker + readme_content.split(end_marker)[1]

# Write the updated content back to the README file
with open(readme_file_path, 'w') as file:
    file.write(updated_content)

print("README.md has been updated with the latest OpenRoaming support tables and domain lookup results.")
