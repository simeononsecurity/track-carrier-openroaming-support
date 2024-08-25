import json
from tabulate import tabulate

# Paths to the JSON data and README file
json_file_path = 'data/mccmnc.json'
readme_file_path = 'README.md'

# Load data from the JSON file
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
        supported_list.append([details['NETWORK'], details['COUNTRY'], details['MCC'], details['MNC']])
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
supported_table_md = tabulate(supported_table, headers=["Network", "Country", "MCC", "MNC"], tablefmt="github")

# Read the README file
with open(readme_file_path, 'r') as file:
    readme_content = file.read()

# Prepare the updated content with tables
tables_section = f"""
## OpenRoaming Support Status
{support_table_md}

## Supported Carriers
{supported_table_md}
"""

# Replace the content between the comments
start_marker = '<!-- Tables Start -->'
end_marker = '<!-- Tables End -->'
updated_content = readme_content.split(start_marker)[0] + start_marker + tables_section + end_marker + readme_content.split(end_marker)[1]

# Write the updated content back to the README file
with open(readme_file_path, 'w') as file:
    file.write(updated_content)

print("README.md has been updated with the latest OpenRoaming support tables.")
