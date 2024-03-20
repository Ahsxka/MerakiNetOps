import sys
import meraki
import csv

from modules.utils.colors import color_format
from modules.utils.base import choose_file, get_network_id, get_organization_id, get_encoding
try:
    from key import API_KEY
except:
    color_format.print_error("No API KEY FOUND. Please provide a 'key.py' file with a correct API_KEY value."
                             "\nAborting session...")
    sys.exit()


def get_valid_data(file_path):
    valid_data = []
    encoding = get_encoding(file_path)

    with open(file_path, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_entry = {
                'Name': row['Name'],
                'Network': row['Network'],
                'RadiusServers': [
                    {'host': row['RADIUS 1'], 'port': row['PORT']},
                    {'host': row['RADIUS 2'], 'port': row['PORT2']}
                ],
                'AccountingServers': [
                    {'host': row['ACCOUNTING 1'], 'port': row['PORT3']},
                    {'host': row['ACCOUNTING 2'], 'port': row['PORT4']}
                ]
            }
            valid_data.append(data_entry)
    return valid_data


def get_policy_number(session, network_id, policy_name):
    policies = session.switch.getNetworkSwitchAccessPolicies(
        network_id
    )
    for e in policies:
        if e['name'] == policy_name:
            policy_number = e['accessPolicyNumber']
            return policy_number


def main():
    print("""
    File Format:
    The script expects a CSV (or .txt) file separated with commas with the following format:

    - Each row represents a device configuration.
    - The CSV file should contain the following columns:
        - 'Name': Name of the device.
        - 'Network': Name of the network the device should be configured in.
        - 'RADIUS 1': Hostname or IP address of the primary RADIUS server.
        - 'RADIUS 2': Hostname or IP address of the secondary RADIUS server.
        - 'PORT': Port number for RADIUS servers.
        - 'ACCOUNTING 1': Hostname or IP address of the primary accounting server.
        - 'ACCOUNTING 2': Hostname or IP address of the secondary accounting server.
        - 'PORT3': Port number for accounting servers.
        - 'PORT4': Port number for accounting servers.

    Example file:
    Name,Network,RADIUS 1,RADIUS 2,PORT,ACCOUNTING 1,ACCOUNTING 2,PORT3,PORT4
    Device1,Network1,192.168.1.100,192.168.1.101,1812,192.168.2.100,192.168.2.101,1813,1813
    Device2,Network2,10.0.0.100,10.0.0.101,1812,10.0.1.100,10.0.1.101,1813,1813
    Device3,Network3,172.16.0.100,172.16.0.101,1812,172.16.1.100,172.16.1.101,1813,1813

    Please ensure the CSV file adheres to this format for the script to function correctly.
    """)
    color_format.print_info("Please read the above documentation before using this program.")
    session = meraki.DashboardAPI(API_KEY, output_log=False, suppress_logging=True)
    color_format.prsep()
    org_name = input("Enter the *exact* organization name : ")
    policy_name = input("Enter policy name to modify : ")
    if not policy_name:
        policy_name = "Access policy #1"
    print("Choose your device file : ")
    device_file = choose_file()
    color_format.prsep()
    password = input("Enter RADIUS password : ")
    color_format.prsep()
    verbose = str(input("Verbose mode [y/N] : ")).lower()
    if not verbose:
        verbose = 'n'
    organization_id = get_organization_id(session, org_name)
    var = (organization_id)
    color_format.prsep()
    color_format.print_info("Current settings :")
    print("Verbose mode : on" if verbose == "y" else "Verbose mode : off")
    print(f"Organization : {org_name}")
    print(f"Policy       : {policy_name}")
    print(f"Password     : {password}")
    color_format.prsep()
    color_format.print_warning("Do you want to continue with these settings? [y/N] : ", end="")
    confirmation = input().lower() or "n"  #
    color_format.prsep()

    if confirmation == "y":
        for e in get_valid_data(device_file):
            try:
                network_id = get_network_id(session, organization_id, e['Network'])
                if verbose == "y":
                    color_format.print_info(f"Configuring {e['Name']} in network {e['Network']}...")
                radius_servers = []
                for radius_server in e['RadiusServers']:
                    radius_servers.append({
                        'host': radius_server['host'],
                        'port': radius_server['port'],
                        'secret': password
                    })
            except meraki.APIError as error:
                color_format.print_error(f"Network {e['Network']} not found with error\n{10 * ' '}{error}")

            accounting_servers = []
            for accounting_server in e['AccountingServers']:
                accounting_servers.append({
                    'host': accounting_server['host'],
                    'port': accounting_server['port'],
                    'secret': password
                })

            access_policy_number = get_policy_number(session, network_id, policy_name)
            try:
                session.switch.updateNetworkSwitchAccessPolicy(
                    network_id, access_policy_number,
                    name=policy_name,
                    radiusServers=radius_servers,
                    radiusAccountingServers=accounting_servers,
                )
                if verbose == "y":
                    color_format.print_success(f"Successfully configured {e['Name']} :")
                    print(f"{4 * ' '}Radius server(s) :")
                    for i in e['RadiusServers']:
                        print(f"{8 * ' '}host : {i['host']}   port : {i['port']}")
                    print(f"{4 * ' '}Accounting server(s) :")
                    for i in e['AccountingServers']:
                        print(f"{8 * ' '}host : {i['host']}   port : {i['port']}")
                    print(f"{80 * "-"}")
            except meraki.APIError as error:
                color_format.print_error(f"Failed to configure device {e['Name']} with error {error}")

    else:
        color_format.print_warning("Aborting session...")
        print(f"{80 * "-"}")


if __name__ == "__main__":
    main()
