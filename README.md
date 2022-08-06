# api.genobank.io

This is the API documentation for the [Genobank](https://genobank.io) API.

This API is ONLY for use by the Genobank team.
This API is ONLY to create new Permittees on the Test and Production Environment.

## Installing the dependencies
Before to download this repository, you need to install the following dependencies:
```sh
npm install
```
If this not works you can try with
```sh
sudo apt install npm
```
To start this API you need install virtual env using the following command:
```sh
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
```

Next to this, you need to create a virtual enviroment using the following command:
Firs create a folder, enter on it and run the following command:

```sh
virtualenv <name_of_enviroment>
```

The '<name_of_enviroment>' can be any name you want.
This will create a folder, enter it and create a folder with the name you want and enter it.
Now download the repository using the following command:

```sh
git init
git remote add origin https://github.com/FranciscoTun2/api.genobank.io.git
git pull origin master
```


Then you need to activate the virtual env using the following command:

```sh
. ../bin/activate
```

Install all the dependencies using the following command:
```sh
pip install -r requirements.txt
```
## Configuring the env for the file
First, create a new `.env` file with the content below. Make sure that each variable is set to the correct value.
```sh
# GENERAL SETTINGS
ENVIROMENT = "PRODUCTION"
TEST_ENVIROMENT = "TEST"
TEST_APP_SECRET = <YOUR_TEST_SECRET_APPLICATION>
APP_SECRET = <YOUR_PRODUCTION_SECRET_APPLICATION>

# API(S)
API_PERMITTEES = <YOUR_PRODUCTION_API_PERMITTEE_APPLICATION>
TEST_API_PERMITTEES = <YOUR_PRODUCTION_API_PERMITTEE_APPLICATION>

# DATABASE CONF (mongo db)
MONGO_DB_HOST = <YOUR_PRODUCTION_DATABASE_URL_CONECTION>
DB_NAME = <THE_PRODUCTION_DATABASE_NAME>
TEST_MONGO_DB_HOST = <YOUR_TEST_DATABASE_URL_CONECTION>
TEST_DB_NAME = <TEST_DATABASE_NAME>

# BLOCKCHAIN CONFIGURATIONS
PROVIDER = <YOUR RINKEBY NODE WITH KEY>

# SMARTCONTRACT
SMART_CONTRACT = <PRODUCTION_SMARTCONTRACT_ADDRESS>
TEST_SMART_CONTRACT = <TEST_SMARTCONTRACT_ADDRESS>

# WALLET EXECUTOR
ROOT_KEY_EXECUTOR = <PRODUCTION_EXECUTOR_PRIVATE_KEY>
TEST_ROOT_KEY_EXECUTOR = <TEST_EXECUTOR_PRIVATE_KEY>

# ABI ROUTE
ABI_SM_PATH = <./IN/PROJECT/SMARTCONTRACT_JSONINTERFACE/FILE/PATH.json>

# FILE ROUTES (Static values, Do not modify)
PERMITEE_INSERTS = "./storage/permittee_prod_inserts.json"
TEST_PERMITEE_INSERTS = "./storage/permittee_test_inserts.json"
```

## Running the API
Now you can run the API using the following command:
on the folder where you have downloaded the repository run the following command:
```sh
python3 start.py
```
to check if the repository is running, open yor favourite web browser and go to http://localhost:8081/

## Pushing the repository
If you want to push the repository, does you will need configure the `.gitignore` file as the follow:

```sh
.env
.gitignore
```
