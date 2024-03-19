import sys
import meraki
import csv

from modules.utils.colors import color_format
from modules.utils.base import choose_file, get_network_id
try:
    from key import API_KEY
except:
    color_format.print_error("No API KEY FOUND. Please provide a 'key.py' file with a correct API_KEY value."
                             "\nAborting session...")
    sys.exit()


def get_valid_data(file_path):
    valid_orgs = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            org_name = row['Organization']
            network_name = row['Network']
            serial = row['Serial']
            name = row['Name']
            if org_name not in valid_orgs:
                valid_orgs[org_name] = {'networks': {}, 'serials': {}}
            if network_name not in valid_orgs[org_name]['networks']:
                valid_orgs[org_name]['networks'][network_name] = []
            valid_orgs[org_name]['networks'][network_name].append(serial)
            valid_orgs[org_name]['serials'][serial] = name
    return valid_orgs


def claim_devices(session, org_name, serials):
    organizations = session.organizations.getOrganizations()
    claimed_successfully = False
    for organization in organizations:
        if organization['name'] == org_name:
            organization_id = organization['id']
            print(organization_id)
            try:
                session.organizations.claimIntoOrganizationInventory(organization_id, serials=serials)
                print(f"Claim executed for organization '{org_name}' with Serials {serials}")
                claimed_successfully = True
            except meraki.APIError as e:
                print(f"Claim failed for organization '{org_name}' with Serials {serials}: {e}")
            break
    if not claimed_successfully:
        print(f"Unable to find organization '{org_name}'.")


def add_devices_to_networks(session, org_name, networks_and_serials):
    organizations = session.organizations.getOrganizations()
    org_id = None
    for org in organizations:
        if org['name'] == org_name:
            org_id = org['id']
            break
    if org_id:
        for network_name, serials in networks_and_serials.items():
            network_id = get_network_id(session, org_id, network_name)
            if network_id:
                try:
                    session.networks.claimNetworkDevices(network_id, serials)
                    print(
                        f"Devices added to network '{network_name}' in organization '{org_name}' with Serials {serials}")
                except meraki.APIError as e:
                    print(
                        f"Failed to add devices to network '{network_name}' in organization '{org_name}' with Serials {serials}: {e}")
            else:
                print(f"Network '{network_name}' not found in organization '{org_name}'.")
    else:
        print(f"Organization '{org_name}' not found.")


def change_device_name(session, serial, name):
    session.devices.updateDevice(serial, name=name)


def main():
    print("""
    File Format:
    The script expects a CSV (or .txt) file separated with comma with the following format:

    - Each row represents a device.
    - The CSV file should contain the following columns:
        - 'Organization': Name of the organization the device belongs to.
        - 'Network': Name of the network the device should be added to.
        - 'Serial': Serial number of the device.
        - 'Name': Desired name for the device.

    Example file:
    Organization,Network,Serial,Name
    Org1,Net1,XXXX-XXXX-XXXX,Device1
    Org1,Net2,YYYY-YYYY-YYYY,Device2
    Org2,Net3,ZZZZ-ZZZZ-ZZZZ,Device3

    Please ensure the CSV file adheres to this format for the script to function correctly.
    """)

    color_format.print_info("Please read the above documentation before using this program.")
    session = meraki.DashboardAPI(API_KEY, output_log=False, suppress_logging=False)
    print("Please choose a valid config files, one device per line : ")
    valid_orgs_networks_and_equipments = get_valid_data(choose_file())
    for org_name, data in valid_orgs_networks_and_equipments.items():
        claim_devices(session, org_name, list(data['serials'].keys()))
        add_devices_to_networks(session, org_name, data['networks'])
        for serial in data["serials"]:
            print(serial)
            print(data["serials"][serial])
            change_device_name(session, serial, data["serials"][serial])





if __name__ == "__main__":
    main()
