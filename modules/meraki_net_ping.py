import csv
import time

import meraki
from modules.utils.base import get_organization_id, get_devices_serial, choose_file, get_encoding
from modules.utils.colors import color_format, colors


def get_valid_device_names(file_path):
    """
    Retrieve valid device names from a CSV file.
    """
    valid_device_names = []
    encoding = get_encoding(file_path)
    if encoding:
        try:
            with open(file_path, newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    valid_device_names.append(row['Name'])
        except UnicodeDecodeError as e:
            print(f"Decoding error: {e}")
            print("There may be undecodable characters in the file.")
    return valid_device_names


def send_pings(session, targets, serial_list):
    """
    Send pings to devices in the serial list.
    """
    ngping = 0
    color_format.prsep()
    color_format.print_info(f"Starting ping requests...")
    color_format.prsep()
    for serial in serial_list:
        serial['ping_ids'] = []
        for i, target in enumerate(targets, start=1):
            while True:
                try:
                    response = session.devices.createDeviceLiveToolsPing(
                        serial['serial'], target,
                        count=5,
                    )

                except meraki.APIError as e:
                    if e.status == 429:
                        retry_after = int(
                            e.response.headers.get("Retry-After", 1))  # Temps d'attente avant de réessayer
                        print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                        time.sleep(retry_after)
                    else:
                        print(f"Failed with status code {e.status}.")
                        break
                else:
                    break
            ping_id = response['pingId']
            serial['ping_ids'].append(ping_id)
            print(f"Sending ping requests from host '{serial['name']}' to '{target}'")
            ngping += 1
    # print(serial_list)
    color_format.print_info(f"{ngping} ping requests sent, waiting for statistics...")
    color_format.prsep()


def print_ping_statistics(session, serial_list):
    """
    Print ping statistics for devices in the serial list.
    """
    errors = 0
    nbping = 0
    error_list = []
    for serial in serial_list:
        color_format.prsep()
        print(f"Device: {serial['name']} ({serial['serial']})")
        for i, ping_id in enumerate(serial['ping_ids'], start=1):
            status = 'running'
            while status in ['new', 'running', 'ready']:
                #time.sleep(0.5)
                while True:
                    try:
                        response = session.devices.getDeviceLiveToolsPing(
                            serial['serial'], ping_id
                        )
                    except meraki.APIError as e:
                        if e.status == 429:
                            retry_after = int(
                                e.response.headers.get("Retry-After", 1))  # Temps d'attente avant de réessayer
                            print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                            time.sleep(retry_after)
                        else:
                            print(f"Failed with status code {e.status}.")
                            break
                    else:
                        break

                status = response['status']
                if status == "new":
                    print(".", end="")
                if status == "ready":
                    print(":", end="")
                if status == "running":
                    print("-", end="")
            print('\n')
            if 'results' in response:
                if response['results']['received'] > 0:
                    test_status = "success"
                    print(f"  {colors.VERT}Success : Ping Status ({i}){colors.RESET}")
                else:
                    test_status = "fail"
                    print(f"  {colors.ROUGE}Error   :   Ping Status ({i}): Failed{colors.RESET}")
                    errors += 1
                    error_list.append(serial)

                print(f"  Destination host: {response['request']['target']}")
                print("\tPing Statistics:")
                if response['status'] == 'complete':
                    print("\tPing Results:")
                    print(f"\t  Sent: {response['results']['sent']}")
                    print(f"\t  Received: {response['results']['received']}")
                    print(f"\t  Loss: {response['results']['loss']['percentage']}%")
                    if test_status == 'success':
                        print("\t  Latencies:")
                        print(f"\t    Minimum: {response['results']['latencies']['minimum']} ms")
                        print(f"\t    Average: {response['results']['latencies']['average']} ms")
                        print(f"\t    Maximum: {response['results']['latencies']['maximum']} ms")
            else:
                print(f"  {colors.ROUGE}Error   :   Ping Status ({i}): Failed{colors.RESET}")
                print(f"  Destination host: {response['request']['target']}")
                print("\tNo ping results available.")
                errors += 1
            nbping += 1
        print('\n')

    if errors == 0:
        color_format.print_success(f"Successfully executed {nbping} ping request(s) with 0 errors.")
    else:
        color_format.print_warning(f"Successfully executed {nbping} ping requests but {errors} errors found.")
        error_devices = set(error_device['serial'] for error_device in error_list)
        print("Devices with errors:")
        for serial in error_devices:
            error_device_name = next(device['name'] for device in serial_list if device['serial'] == serial)
            print(f"- {error_device_name} ({serial})")


def main(API_KEY):
    color_format.print_info("Please read the above documentation before using this program.")
    session = meraki.DashboardAPI(API_KEY, suppress_logging=True, output_log=False)
    color_format.prsep()
    org_name = input("Enter Organization name : ")
    color_format.prsep()

    organization_id = get_organization_id(session, org_name=org_name)

    print('Please choose a device file, on device per line : ')
    device_names = get_valid_device_names(choose_file())
    serial_list = get_devices_serial(session, device_names, organization_id)
    while True:
        color_format.prsep()
        targets = input("Please enter the targets IP or FQDN for the ping requests, separated by commas : ").split(",")
        send_pings(session, targets, serial_list)
        color_format.prsep()
    # Uncomment the line below if you want to wait for the pings to complete before printing statistics
    # time.sleep(5)

        print_ping_statistics(session, serial_list)


if __name__ == "__main__":
    main()
