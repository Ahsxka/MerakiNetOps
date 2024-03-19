import sys
import meraki
import csv

from modules.utils.colors import color_format
from modules.utils.base import choose_file, menu_builder, get_network_id, get_organization_id
try:
    from key import API_KEY
except:
    color_format.print_error("No API KEY FOUND. Please provide a 'key.py' file with a correct API_KEY value."
                             "\nAborting session...")
    sys.exit()


def get_valid_data(file_path):
    valid_data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_entry = {
                'Network': row['Network']
            }
            valid_data.append(data_entry)
        if len(valid_data) == 0:
            color_format.print_error(f"File '{file_path}' is empty ! Please choose another file."
                                     f"\n{10 * ' '}Aborting session...")
            sys.exit()
        return valid_data


def main():
    print("""
    File Format:
    The script expects a CSV (or .txt) file with a list of network names. The first line of the file should contain the header "Network", followed by each network name on a separate line.

    - The first line represents the header.
    - Each subsequent line represents a network name.

    Example file:
    Network
    Network1
    Network2
    Network3

    Please ensure the file contains the header "Network" in the first line, followed by the names of the networks to which you want to apply syslog configuration, with each network name on a separate line.
    """)

    color_format.print_info("Please read the above documentation before using this program.")
    org_name = input("Enter the *exact* organization name : ")
    session = meraki.DashboardAPI(API_KEY, output_log=False, suppress_logging=True)

    organization_id = get_organization_id(session, org_name)
    print("Please choose your network files, one network per line : ")
    valid_data = get_valid_data(choose_file())

    servers = []
    while True:
        syslog_server = input("Enter syslog server IP (leave blank to finish) : ")
        if not syslog_server:
            if not servers:
                print("No syslog servers entered. Exiting.")
                sys.exit()
            else:
                print("No more syslog servers to add. Exiting.")
                break

        syslog_port = int(input("Enter syslog server port : "))
        syslog_roles = menu_builder("Syslog Roles :", ["Switch event log",
                                                       "Flows",
                                                       "URLs",
                                                       "Security events",
                                                       "WAN Appliance event log",
                                                       "Air Marshal events",
                                                       "Wireless event log"]
                                    )
        # In the cisco meraki dashboard, the terminology is "WAN Appliance event log",
        # with the API, the same option is called "Appliance event log",
        # That's why I have to hardcode replace it here :
        syslog_roles = ["Appliance event log" if option == "WAN Appliance event log" else option for option in
                        syslog_roles]
        server = {'host': syslog_server, 'port': syslog_port, 'roles': syslog_roles}
        servers.append(server)

    for e in valid_data:
        network_name = e['Network']
        try:
            color_format.print_info(f"Applying syslog config to network '{network_name}'...")
            network_id = get_network_id(session, organization_id, network_name)
            session.networks.updateNetworkSyslogServers(
                network_id, servers
            )
            color_format.print_success(f"Successfully applied syslog config to network '{network_name}'.")
        except meraki.APIError as error:
            color_format.print_error(f"Failed to configure network '{network_name}' :\n{10 * ' '}|__ {error}")



if __name__ == "__main__":
    main()
