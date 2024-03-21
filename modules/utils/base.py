import sys
import csv
import tkinter as tk
from tkinter import filedialog
from modules.utils.colors import color_format


def choose_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', 1)
    archivo = filedialog.askopenfilename()
    return archivo


def get_network_id(session, org_id, network_name):
    networks = session.organizations.getOrganizationNetworks(org_id)
    for network in networks:
        if network['name'] == network_name:
            return network['id']
    else:
        color_format.print_error(f"Cannot find network {network_name}")
        return None


def get_organization_id(session, org_name):
    if len(org_name) == 0:
        color_format.print_error(f"Please provide a valid organisation.\n"
                                 f"{10 * ' '}Aborting session...")
        sys.exit()
    organizations = session.organizations.getOrganizations()
    for organization in organizations:
        if organization['name'] == org_name:
            organization_id = organization['id']
            return organization_id
    else:
        color_format.print_error(f"Organization '{org_name}' not found, please provide a valid organisation.\n"
                                 f"{10 * ' '}Aborting session...")
        sys.exit()


def get_devices_serial(session, devices_list, organization_id):
    devices = session.organizations.getOrganizationDevices(
        organization_id, total_pages='all'
    )
    device_serial_list = []
    for device in devices:
        if device['name'] in devices_list:
            device_info = {'name': device['name'], 'serial': device['serial']}
            device_serial_list.append(device_info)
    return device_serial_list


def menu_builder(menu_title="Menu", options=['Option 1', 'Option 2']):
    selected_options = []
    while True:
        color_format.prsep()
        print(menu_title)
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")
        choices = input("Enter the numbers of the roles separated by commas: ")
        selected_options = get_option(choices.split(','), options)
        if selected_options:
            invalid_choices = [choice for choice in choices.split(',') if
                               choice not in map(str, range(1, len(options) + 1))]
            if not invalid_choices:
                break
            else:
                color_format.prsep()
                color_format.print_warning("Invalid choice(s) detected. Please enter valid option numbers.")
        else:
            color_format.prsep()
            color_format.print_warning("Invalid choice. Please enter valid option numbers.")
    return selected_options


def get_option(choices, options):  # Function used by menu_builder
    option_dict = {str(index): option for index, option in enumerate(options, start=1)}
    return [option_dict[choice] for choice in choices if choice in option_dict]


def get_encoding(file_path):
    encodings_to_try = ['utf-8', 'windows-1252', 'latin-1', 'ISO-8859-1', 'UTF-16', 'cp1252', 'ascii', 'mac_roman']
    for encoding in encodings_to_try:
        try:
            with open(file_path, newline='', encoding=encoding) as csvfile:
                csv.DictReader(csvfile)
                for row in csvfile:  # Very important to keep this line for the test to occur
                    pass
            color_format.print_success(f"Opening '{file_path}' with encoding '{encoding}'.")
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            color_format.print_warning(f"Failed to open '{file_path}' with encoding '{encoding}'.")


def printfile(filepath):
    with open(filepath, "r") as f:
        for l in f:
            print(l, end='')
        print('\n')
