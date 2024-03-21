# Utils Modules
from modules.utils.colors import color_format
from modules.utils.base import menu_builder, printfile

# Configuration Modules :
from modules.meraki_net_radius_v1_3_base import main as configure_radius
from modules.meraki_net_syslog_v1_2_base import main as configure_syslog
from modules.meraki_net_claim_v1_1_base import main as claim_device
from modules.meraki_net_ping import main as bulk_ping


def main():
    options = ["Configure RADIUS", "Configure Syslog", "Claim Device", "Bulk ping"]
    choice = menu_builder("Welcome to MerakiNetOps!", options)[0]

    if choice == "Configure RADIUS":
        printfile("modules/docs/radius.info")
        configure_radius()
    elif choice == "Configure Syslog":
        printfile("modules/docs/syslog.info")
        configure_syslog()
    elif choice == "Claim Device":
        printfile("modules/docs/claim.info")
        claim_device()
    elif choice == "Bulk ping":
        printfile("modules/docs/ping.info")
        bulk_ping()
    else:
        color_format.print_warning("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
