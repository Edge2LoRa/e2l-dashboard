#  Edge2LoRa Dashboard

The Edge2LoRa Dashboard aims to shows the data stream for Edge2LoRa. The Dashboard has been created to support the Demo presented at the MobiCom 2023 in Madrid the 2nd of October. [LINK](https://doi.org/10.1145/3570361.3614074)

## Clone the repository

To clone the repository run the following command:

```bash
git clone https://github.com/Edge2LoRa/e2l-dashboard.git 
```

or:

```bash
git clone git@github.com:Edge2LoRa/e2l-dashboard.git
```

## Create & activate a Virtual Enviroment (Optional, but recommended)

It is reccommended to create a python virtual enviroment to avoid creating conflicts between the different packages that could be installed in your system. To do so, run:
```bash
cd e2l-dashboard/
python3 -m venv vnev
```

To activate the virtual enviroement run (to repeat each time):
```basj
. venv/bin/activate
```

## Install the requirements

To install the needed python packages run:

```bash
pip3 install wheel
pip3 install -r requirements.txt
```

## Run the Dashboard

To run the Dashboard run:

```bash
cd server-modules-final/
python3 main.py
```

## Availables endpoints

The HTTP endpoint hosting the GUI is available on the port 8050.

The RPC endpoint to which the [e2l-distributed-module](https://github.com/Edge2LoRa/e2l-distributed-module) shall connect is available on the port 23333.



