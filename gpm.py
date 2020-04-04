import sys
import os
import json
import shutil
import base64
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import pyperclip

PASSWORD_LENGTH = 1
MIN_BLOCK_SIZE = 256  # Must be a positive nonzero multiple of 16
PASSWORD = ""
DB = {}


def help():
    print("Welcome to gpm (git password manager).")
    print("gpm supports 6 main queries: copy, paste, get, set, ls and passwd")
    print("To copy a value from the store to your clipboard, type copy <service> <username>")
    print("To paste a value from the clipboard and store it in the database, type paste <service> <username>")
    print("To get a value from the store and print it to the console, type get <service> <username>")
    print("To set a value, type set <service> <username>. You will be asked to type in a value and repeat it.")
    print("To list all services, type \"ls\"")
    print("To change your password, type passwd")
    print("To list all usernames for a given service, type ls <service>")
    print("After you set a value, the changes are immediately written to disk and encrypted, and the iv file is updated.")
    print("To exit, type \"exit\".")


def pad(byte):
    return byte.ljust(len(byte)+(MIN_BLOCK_SIZE - (len(byte) % (MIN_BLOCK_SIZE))), b' ')


def password_valid(password):
    # Define password rules here
    return len(password) >= PASSWORD_LENGTH


def get_hash(password):
    # Define hash function here (must return 32 byte hash)
    hashed = SHA256.new(password.encode("utf-8"))
    return hashed.digest()


def gen_iv():
    return get_random_bytes(16)


def write_iv(iv):
    open("iv.gpm", "wb").write(base64.b64encode(iv))


def get_iv():
    return base64.b64decode(open("iv.gpm", "rb").readlines()[0])


def decrypt(string):
    key = get_hash(PASSWORD)
    obj = AES.new(key, AES.MODE_CBC, get_iv())
    return obj.decrypt(string)


def encrypt(string):
    key = get_hash(PASSWORD)
    obj = AES.new(key, AES.MODE_CBC, get_iv())
    return obj.encrypt(string)


def create_backup():
    shutil.copyfile("db.gpm", "db.bak.gpm")


def remove_backup():
    os.remove("db.bak.gpm")


def commit():
    new_iv = gen_iv()
    write_iv(new_iv)
    try:
        f = open("db.gpm", "wb")
    except FileNotFoundError:
        f = open("db.gpm", "xb")
    create_backup()
    f.write(base64.b64encode(
        encrypt(pad(bytes(json.dumps(DB), "utf-8")))))
    remove_backup()


def load():
    global DB
    try:
        db_bytes = decrypt(base64.b64decode(
            open("db.gpm", "rb").readlines()[0]))
        DB = json.loads(
            db_bytes)
    except:
        print("Decryption failed. Aborting.")
        sys.exit(0)


def cli():
    def invalid():
        print('Invalid command. For help type "help".')
    global DB, PASSWORD
    while True:
        print("gpm $ ", end="")
        try:
            query = input().split(" ")
        except KeyboardInterrupt:
            print("\nExiting...")
            return
        if query[0] == "help":
            help()
        elif query[0] == "get":
            if len(query) == 3:
                try:
                    print(DB.get(query[1]).get(query[2]))
                except:
                    print("Not found")
            else:
                invalid()
        elif query[0] == "copy":
            if len(query) == 3:
                try:
                    pyperclip.copy(DB.get(query[1]).get(query[2]))
                    print(f"Password for {query[2]} copied to clipboard!")
                except:
                    print("Not found")
            else:
                invalid()
        elif query[0] == "set":
            if len(query) == 3:
                service = query[1]
                username = query[2]
                if DB.get(service) == None:
                    DB[service] = {}
                while True:
                    value = getpass("Type in or paste a password: ")
                    confirm = getpass("Repeat: ")
                    if value == confirm:
                        DB.get(service)[username] = value
                        commit()
                        break
            else:
                invalid()
        elif query[0] == "paste":
            if len(query) == 3:
                service = query[1]
                username = query[2]
                if DB.get(service) == None:
                    DB[service] = {}
                DB.get(service)[username] = pyperclip.paste()
                commit()
                print(f"Password for {query[2]} pasted from clipboard!")
            else:
                invalid()
        elif query[0] == "ls":
            if(len(query) == 1):
                for key in DB.keys():
                    print(key)
            elif(len(query) == 2):
                try:
                    for key in DB.get(query[1]).keys():
                        print(key)
                except:
                    print(f"service \"{query[1]}\" not found")
            else:
                invalid()
        elif query[0] == "passwd":
            try:
                oldpass = getpass("Type your old password: ")
                if oldpass == PASSWORD:
                    new_password = getpass("Type new password: ")
                    confirm = getpass("Confirm new password: ")
                    if(new_password == confirm):
                        PASSWORD = new_password
                        commit()
                    else:
                        print("passwords did not match")
                else:
                    print("passwords did not match")
            except KeyboardInterrupt:
                pass
        elif query[0] == "exit":
            break
        else:
            invalid()


def main(args):
    global PASSWORD, DB
    init = True if "-i" in args else False
    try:
        open("db.gpm", "rb")
    except FileNotFoundError:
        if(init):
            print("Initializing...")
            confirm = ""
            while not (password_valid(PASSWORD) and PASSWORD == confirm):
                PASSWORD = getpass(
                    prompt=f"Set your master password (must be at least {PASSWORD_LENGTH} characters long): ")
                confirm = getpass(prompt="Type your password again: ")
            commit()
        else:
            print(
                "Database not initialized. If you're using gpm for the first time, try \"gpm -i\"")
            sys.exit(0)
    PASSWORD = getpass(prompt="Type your master password: ")
    load()
    cli()
    DB = None
    PASSWORD = None


if __name__ == "__main__":
    main(sys.argv)
