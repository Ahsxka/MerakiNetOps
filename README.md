![Ahsxka-MerakiNetOps (1)](https://github.com/Ahsxka/MerakiNetOps/assets/162576190/5e484bdd-4f9d-4275-9197-abdbf0fc9fbe)


# MerakiNetOps

MerakiNetOps is a Python script designed to automate configuration tasks for Meraki devices. It offers functionalities to configure RADIUS, Syslog, and claim devices into networks.

## Features

- **Configuration Modules**: Includes modules for configuring RADIUS, Syslog, and claiming devices into networks.
- **CSV Input**: Accepts input data in CSV format for easy configuration.
- **Interactive Interface**: Provides an interactive menu for selecting the desired operation.

## Prerequisites

- Python 3.12
- [Meraki Dashboard API Key](https://developer.cisco.com/meraki/api-v1/)
- [Meraki Python Library](https://pypi.org/project/meraki/)

## Installation

1. Clone this repository to your local machine:
    ```
    git clone https://github.com/Ahsxka/MerakiNetOps.git
    ```

2. Navigate to the project directory:
    ```
    cd MerakiNetOps
    ```

3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Create a `key.py` file, containing your key, following this syntax:
    ```
    API_KEY='PASTE YOUR API KEY HERE'
    ```

## Usage

Run the `MerakiNetOps.py` script to start the application:

```
python MerakiNetOps.py
```


Follow the prompts to select the desired operation and provide necessary inputs.

## File Structure
```
MerakiNetOps/
│
├── modules/
│    ├── meraki_net_claim_v1_1_base.py
│    ├── meraki_net_radius_v1_3_base.py
│    ├── meraki_net_syslog_v1_2_base.py
│    ├── meraki_net_ping.py
|    ├── docs/
|    |    ├── claim.info
|    |    ├── ping.info
|    |    ├── radius.info
|    |    └── syslog.info
|    |
│    └── utils/
│         ├── colors.py
│         └── base.py
│
├── MerakiNetOps.py
└── README.md
```



## Configuration Modules

- **meraki_net_claim_v1_1_base.py**: Module for claiming devices into networks.
- **meraki_net_radius_v1_3_base.py**: Module for configuring RADIUS servers.
- **meraki_net_syslog_v1_2_base.py**: Module for configuring Syslog servers.
- **meraki_net_ping.py** : Module to run connectivity tests for a wide range of devices within an organization.

## About

I'm planning to continue updating and improving this script during my internship at <a href="https://www.ikusi.com/es/" target="_blank">Ikusi</a>. If you have any question or ideas, feel free to email me at apichot.it@gmail.com

![cabecera_comunicados_2](https://github.com/Ahsxka/python-automation/assets/162576190/af0864ed-84e4-453d-8948-bb23d131e54b)
