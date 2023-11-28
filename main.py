import json
from tkinter import *
from tkinter.simpledialog import askstring
from tkinter import messagebox
from cryptography.fernet import Fernet
import random
import pyperclip
import atexit

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']


def gen_password():
    password_entry.delete(0, END)

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)

    password_letters = [random.choice(letters) for _ in range(nr_letters)]
    password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
    password_numbers = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    password = "".join(password_list)
    password_entry.insert(0, password)
    pyperclip.copy(password)
    messagebox.showinfo(title="Info", message="Password copied to clipboard.")


# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    new_data = {
        website: {
            "email": username,
            "password": password,
        }
    }

    if website == "" or password == "":
        messagebox.showwarning(title="Oops", message="Please don't leave any fields empty!")
    else:
        confirm_entry = messagebox.askokcancel(title=website, message=f"Confirm new password:\n"
                                                                      f"Username/Email: {username}\n"
                                                                      f"Password: {password}")
        if confirm_entry:
            try:
                with open(file="data.json", mode="r") as passwords:
                    # Reading old data
                    data = json.load(passwords)
                    # Updating old data with new data
                    data.update(new_data)

            except:
                with open(file="data.json", mode="w") as passwords:
                    # Saving new data
                    json.dump(new_data, passwords, indent=4)

            else:

                with open(file="data.json", mode="w") as passwords:
                    json.dump(data, passwords, indent=4)

            finally:
                website_entry.delete(0, END)
                password_entry.delete(0, END)


# ---------------------------- SEARCH PASSWORD ------------------------------- #
def search():
    website = website_entry.get()
    passwordFound = False

    if website == "":
        messagebox.showwarning(title="Oops!", message="Please don't leave any fields empty!")
    else:
        try:
            with open(file="data.json", mode="r") as passwords:
                data = json.load(passwords)
        except FileNotFoundError:
            messagebox.showwarning(title="Error", message="No Data File Found")
        else:
            for entry in data:
                if website.lower() == entry.lower():
                    passwordFound = True
                    messagebox.showinfo(title=f"{website}", message=f"Your {entry} "
                                                                    f"password is: {data[entry]['password']}")
            if not passwordFound:
                messagebox.showwarning(title="Error", message=f"No details for {website.title()} exists.")

# ---------------------------- ENCRYPT/DECRYPT PASSWORDS ------------------------------- #
def write_key():
    key = Fernet.generate_key()
    with open(file="filekey.key", mode='wb') as filekey:
        filekey.write(key)


def load_key():
    with open(file="filekey.key", mode="rb") as filekey:
        return filekey.read()


try:
    key = load_key()
except FileNotFoundError:
    write_key()
    key = load_key()


# Encrypt Data
def encrypt():
    with open(file="data.json", mode="rb") as file:
        data = file.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(file="data.json", mode="wb") as encrypted_file:
        encrypted_file.write(encrypted)


# Decrypt Data
def decrypt():
    with open(file="data.json", mode="rb") as encrypted_file:
        encrypted = encrypted_file.read()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)
    with open(file="data.json", mode="wb") as decrypted_file:
        decrypted_file.write(decrypted)


# Validate Master Password
guessCount = 3
try:
    with open(file="masterkey.key", mode='r') as masterkey:
        master_key = masterkey.read()
        while True:
            user_guess = askstring(title="KeySafe Password Manager", prompt="Please enter the Master Password:")
            if user_guess != master_key:
                guessCount -= 1
                messagebox.showwarning(title="Error!", message=f"Incorrect Password.\n\n{guessCount} tries remaining.")
                if guessCount == 0:
                    exit()
                else:
                    try:
                        decrypt()
                        break
                    except FileNotFoundError:
                        break
except FileNotFoundError:
    with open(file="masterkey.key", mode="w") as masterkey:
        master_key = askstring(title="KeySafe Password Manager",
                               prompt="No Master Password found!\n\nPlease enter a new Master Password:")
        masterkey.write(master_key)

# Re-Encrypt Data on exit
atexit.register(encrypt)

# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("KeySafe Password Manager")
window.config(padx=50, pady=50)

# Logo
canvas = Canvas(width=200, height=200)
logo = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo)
canvas.grid(row=0, column=1)

# Labels
website_label = Label(text="Website:")
username_label = Label(text="Email/Username:")
password_label = Label(text="Password:")

# Entries
website_entry = Entry(width=33, justify="left")
website_entry.focus()
username_entry = Entry(width=52, justify="left")
username_entry.insert(0, "example.email@gmail.com")
password_entry = Entry(width=33, justify="left")

# Buttons
search_button = Button(text="Search", width=15, command=search)
generate_button = Button(text="Generate Password", command=gen_password)
add_button = Button(text="Add", width=44, command=save)

# Grids
website_label.grid(row=1, column=0)
username_label.grid(row=2, column=0)
password_label.grid(row=3, column=0)

website_entry.grid(row=1, column=1)
username_entry.grid(row=2, column=1, columnspan=2)
password_entry.grid(row=3, column=1)

search_button.grid(row=1, column=2)
generate_button.grid(row=3, column=2)
add_button.grid(row=4, column=1, columnspan=2)

window.mainloop()
