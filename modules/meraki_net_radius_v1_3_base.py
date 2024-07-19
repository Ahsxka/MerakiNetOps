import sys
import meraki
import csv

from modules.utils.colors import color_format
from modules.utils.base import choose_file, get_network_id, get_organization_id, get_encoding


def get_valid_data(file_path):
    valid_data = []
    encoding = get_encoding(file_path)
    print(encoding)

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


def main(API_KEY):
    color_format.print_info("Please read the above documentation before using this program.")
    session = meraki.DashboardAPI(API_KEY, output_log=False, suppress_logging=True)

    color_format.prsep()
    org_name = input("Enter the *exact* organization name : ")
    organization_id = get_organization_id(session, org_name)
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
                    color_format.prsep()
            except meraki.APIError as error:
                color_format.print_error(f"Failed to configure device {e['Name']} with error {error}")

    else:
        color_format.print_warning("Aborting session...")
        color_format.prsep()


if __name__ == "__main__":
    main()
