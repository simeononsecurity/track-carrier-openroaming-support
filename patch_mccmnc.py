"""
Patches the installed mccmnc package's update() function to work with the
current mcc-mnc.com website, which is now a React SPA.
The original update() used BeautifulSoup to scrape an HTML <table> that no
longer exists in the static HTML. The patched version fetches the JS bundle
and extracts MCC-MNC data from the embedded JS array.

Run this script once after `pip install mccmnc` to apply the patch:
    python patch_mccmnc.py
"""

import importlib
import importlib.util
import os
import sys


PATCHED_UPDATE = '''
def update():
    import re as _re
    try:
        # Step 1: Fetch the homepage to find the current JS bundle URL
        # (the site is now a SPA — data is embedded in the JS bundle)
        with urlopen(MCC_MNC_URL) as raw:
            print(f"Decoding raw HTML from {MCC_MNC_URL}")
            html = raw.read().decode("utf-8")

        bundle_match = _re.search(r\'/assets/[a-zA-Z0-9_.-]+\\.js\', html)
        if not bundle_match:
            print("Could not find JS bundle URL in homepage HTML")
            sys.exit(1)

        bundle_url = MCC_MNC_URL.rstrip(\'/\') + bundle_match.group(0)
        print(f"Fetching JS bundle from {bundle_url}")

        # Step 2: Fetch the JS bundle
        with urlopen(bundle_url) as raw:
            content = raw.read().decode("utf-8")

        # Step 3: Extract MCC-MNC objects from the JS data array
        # Format: {mcc:"289",mnc:"67",iso:"ab",country:"Abkhazia",countryCode:"794",network:"Aquafon"}
        pattern = (
            r\'\\\\{mcc:"([^"]*)",mnc:"([^"]*)"\'
            r\',iso:"([^"]*)",country:"([^"]*)"\'
            r\',countryCode:"([^"]*)",network:"([^"]*)"}\'
        )
        matches = _re.findall(pattern, content)

        if not matches:
            print("Could not find MCC-MNC data in JS bundle")
            sys.exit(1)

        print(f"Found {len(matches)} MCC-MNC entries in JS bundle.")

        if os.path.exists(JSON_PATH):
            print(f"Removing old JSON dictionary {JSON_PATH}.")
            os.remove(JSON_PATH)

        print(f"Creating new JSON dictionary {JSON_PATH}.")
        json_data = {}
        total_rows = len(matches)
        progress_bar = tqdm(
            total=total_rows,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            colour="blue",
        )

        for i, (mcc, mnc, iso, country, country_code, network) in enumerate(matches, start=1):
            plmn = mcc + mnc  # MCC + MNC
            json_data[plmn] = {
                "MCC": mcc,
                "MNC": mnc,
                "ISO": iso,
                "COUNTRY": country,
                "CC": country_code,
                "NETWORK": network.strip() if network else "unknown",
            }
            progress_bar.set_description(f"Processing row {i}/{total_rows}")
            progress_bar.update(1)

        progress_bar.close()

        with open(JSON_PATH, "w+") as json_file:
            print(f"\\nSaving JSON dictionary to {JSON_PATH}.")
            json.dump(json_data, json_file, indent=4, sort_keys=True)

    except URLError as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)
'''


def main():
    # Find the installed mccmnc package location
    spec = importlib.util.find_spec("mccmnc")
    if spec is None:
        print("ERROR: mccmnc package not found. Run: pip install mccmnc")
        sys.exit(1)

    # The package is a namespace package; find mccmnc.py inside it
    pkg_dir = os.path.dirname(spec.submodule_search_locations[0]
                              if spec.submodule_search_locations
                              else spec.origin)
    mccmnc_py = os.path.join(spec.submodule_search_locations[0], "mccmnc.py") \
        if spec.submodule_search_locations \
        else spec.origin

    if not os.path.exists(mccmnc_py):
        # Try alternate location
        import mccmnc as _m
        mccmnc_py = os.path.join(os.path.dirname(_m.__file__), "mccmnc.py")

    if not os.path.exists(mccmnc_py):
        print(f"ERROR: Could not locate mccmnc/mccmnc.py (looked at {mccmnc_py})")
        sys.exit(1)

    print(f"Patching: {mccmnc_py}")

    with open(mccmnc_py, "r", encoding="utf-8") as f:
        source = f.read()

    # Check if already patched
    if "JS bundle" in source:
        print("Already patched — nothing to do.")
        return

    # Replace the update() function
    import re
    new_source = re.sub(
        r'\ndef update\(\):.*?(?=\n\ndef |\Z)',
        '\n' + PATCHED_UPDATE.strip() + '\n',
        source,
        flags=re.DOTALL
    )

    if new_source == source:
        print("WARNING: Could not locate update() function to patch. The file may "
              "have changed. Please apply the patch manually.")
        sys.exit(1)

    with open(mccmnc_py, "w", encoding="utf-8") as f:
        f.write(new_source)

    print("Patch applied successfully.")


if __name__ == "__main__":
    main()
