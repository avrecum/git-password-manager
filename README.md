# gpm - git password manager

Why store your passwords in a fancy password manager, when you can just encrypt and store them (publicly) in a repository?
(I'm not a cryptographer, so I can't guarantee that there are is absolutely no way to break the crypto. Use this with caution.)

## Install
Clone the repo, cd into the directory and create a virtual environment with Python 3.7:
```
$ python3 -m venv venv
```
Activate the virtual environment:
```
$ source venv/bin/activate
```
Install all requirements:
```
$ pip install requirements.txt
```
Initialize the database:
```
python3 gpm.py -i
```
You'll be asked to enter a master password. Don't forget it! If you lose it, you will not be able to decrypt your passwords.

## Usage
You can either add a shortcut for your terminal or access the password manager by running `python3 gpm.py` inside this repository.
Once you start gpm, you will be asked for your master password. Type it in and hit enter.

Interaction with gpm happens through a command line interface.
For every password you store, you must specify a service, e.g. "google", and a password, e.g. "example@gmail.com".
After every change, the database is re-encrypted and written to disk.
### copy
To copy a password to the clipboard, type
```
gpm $ copy <service> <username>
```
### paste
To paste a password into the database directly from the clipboard, type 
```
gpm $ paste <service> <username>
```
### get
To get a password, type
```
gpm $ get <service> <username>
```
### set
To set a password, type
```
gpm $ set <service> <username>
```
You will be asked to enter a password and repeat it.

### ls
To list all service, type
```
gpm $ ls
```

To list all usernames for a given service, type

```
gpm $ ls <service>
```
### passwd
To change your master password, type
```
gpm $ passwd
```
You will be asked to enter your old password. If it matches, you'll be able to enter and confirm your new password.
Note that if your master password has been compromised, it is best to change all your passwords since the attacker will be able to decrypt the database.
### exit
Once you're done, type
```
gpm $ exit
```

### help
If you forget a command, type
```
gpm $ help
```
