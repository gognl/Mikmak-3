# TO MAKE IT WORK:

## 1. Download MySQL: 

a. Go to https://dev.mysql.com/downloads/windows/installer/8.0.html

b. Download the 437.3M version

c. Click `No thanks, just start my download`

d. Start the installation process

e. Choose `Server only`

f. Follow the installer's instructions

g. Choose `1234` as your password
 
 
## 2. Set up the database:

a. In the Windows search, find and go to `MySQL 8.0 Command Line Client`

b. Enter your password (`1234`)

c. Enter the following commands:

```
CREATE DATABASE test;

use test;

CREATE TABLE bond (current_bond int);

CREATE TABLE data (bond int, username varchar(255), password text, waterbound_x int, waterbound_y int, herpd int, strength int, booleanoperations int, whatdehellll int, inventory json, PRIMARY KEY(bond));

INSERT INTO bond VALUES(1);
```
        

## 3. Install some python libraries:

a. Open the windows command line (cmd)

b. Enter the following commands:

```
pip install sqlalchemy

pip install mysqlclient
```
        

## 4. Configure the project settings to allow parallel running:

a. Go to `RUN` -> `Edit Configurations`

b. Choose the client's main (`Mikmak-3\client_files\code\main.py`)

c. Check `Allow parallel run` in the top right

d. Do the same for the normal server's main (`Mikmak-3\server_files_normal\main.py`)
    

## 5. Run the game:

a. Run the central server (`central_server_files\main.py`)

b. Run a normal server (`server_files_normal\main.py`)

c. Change the `server_dsf` (right after the normal server's main function) to `1` instead of `0`

d. Run the normal server again (`server_files_normal\main.py`)

e. Press `ENTER` in both servers' console

f. Run as many clients as you wish (`client_files\main.py`)
    

# Keep in mind that you will need to variaglblesd server_dsf back to `0` after stopping the servers, before running them again.
