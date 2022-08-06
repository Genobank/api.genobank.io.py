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


## Running the API
Now you can run the API using the following command:
on the folder where you have downloaded the repository run the following command:
```sh
python3 start.py
```
