import os
import threading
import urllib.request
from bit.crypto import ECPrivateKey

from bit.format import bytes_to_wif, public_key_to_address
from tkinter import W
import tkinter as tk
from tkinter.messagebox import showinfo


# option = webdriver.ChromeOptions()
# option.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser-Beta\Application\brave.exe"
# option.add_argument("--incognito --headless")
# browser = webdriver.Chrome(executable_path="chromedriver.exe", options=option)


def generate_wallets(amount):
    # Code for generating wallets on https://walletgenerator.net/. Left in for future update to support other cryptos
    """
    Gui.update_terminal(Gui, "Generating wallets")
    # get to the wallets and create them
    browser.get("https://walletgenerator.net/")
    WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[6]/div[1]/div[1]/div[2]/div[2]/a"))).click()
    browser.find_element(By.ID, "bulkwallet").click()
    browser.find_element(By.ID, "bulklimit").send_keys(Keys.BACKSPACE, amount)  # change value later
    time.sleep(0.5)
    browser.find_element(By.ID, "bulkgenerate").click()
    # write to files
    while "Generating addresses..." in browser.find_element(By.ID, "bulktextarea").get_attribute('value'):
        continue
    Gui.update_terminal(Gui, "Saving Wallets")
    """
    # generating one key locally
    for index in range(amount):
        privkey = ECPrivateKey()
        print("Public Address: " + public_key_to_address(privkey.public_key.format()))
        print("Private Key: " + bytes_to_wif(privkey.secret, compressed=True))
        with open("unchecked_wallets.txt", 'w') as f:
            f.write(str(index + 1) + ',"' + public_key_to_address(privkey.public_key.format()) + '","' + bytes_to_wif(
                privkey.secret, compressed=True) + '"' + "\n")


def remove_traces():
    try:
        os.remove("unchecked_wallets.txt")
    except FileNotFoundError:
        pass
    # browser.quit()
    Gui.stop_gui(Gui, Gui.window)


def check_wallets(amount):
    Gui.update_terminal(Gui, "Preparing to check wallets")
    with open("unchecked_wallets.txt", 'r') as f:
        unchecked_wallets = f.read()
    offset = 0
    for index in range(1, amount + 1):
        # extract public and private addresses from bulk
        temp_public_address_start = unchecked_wallets.index(str(index), offset) + len(str(index)) + 2
        temp_public_address_end = unchecked_wallets.index('"', temp_public_address_start)
        temp_private_address_start = temp_public_address_end + 3
        temp_private_address_end = unchecked_wallets.index('"', temp_private_address_start)
        temp_public_address = unchecked_wallets[temp_public_address_start:temp_public_address_end]
        temp_private_address = unchecked_wallets[temp_private_address_start:temp_private_address_end]
        # Download source of website
        Gui.update_terminal(Gui, "Checking: " + unchecked_wallets[
                                                temp_public_address_start:temp_public_address_end])
        raw_html = urllib.request.Request(url="https://www.blockchain.com/btc/address/" + temp_public_address, headers={
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'})
        raw_html = str(urllib.request.urlopen(raw_html).read())
        html_begin = raw_html.find("times on the Bitcoin blockchain. It has received a total of") + 60
        html_end = raw_html.find("BTC", html_begin) - 1
        # Check if value is 0
        if not raw_html[html_begin:html_end] == "0.00000000":
            save_address(temp_public_address, temp_private_address)
            Gui.update_terminal(Gui, "Wallet saved!")
            Gui.change_color(Gui, "green")
            offset = temp_private_address_end
        Gui.update_terminal(Gui, "No Balance!")
        offset = temp_private_address_end


def save_address(public_address, private_address):
    with open("transacted_wallets.txt", 'a') as f:
        f.write("public: " + '"' + public_address + '"\n' + "private: " + '"' + private_address + '"\n\n')


# checks whether any wallets were found and changes color
def check_amount():
    try:
        with open("transacted_wallets.txt", 'r') as f:
            transacted_wallets = f.read()
        if transacted_wallets == "":
            Gui.change_color(Gui, "red")
            Gui.update_terminal(Gui, "No wallets found, try again")
            print("if")
        else:
            Gui.change_color(Gui, "green")
            Gui.update_terminal(Gui, "Wallets found! Check transacted_wallets.txt")
    except FileNotFoundError:
        Gui.change_color(Gui, "red")
        Gui.update_terminal(Gui, "No wallets found, try again")
        print("except")


def main(wallet_amount):
    generate_wallets(wallet_amount)
    check_wallets(wallet_amount)
    check_amount()


# separate class with gui elements and methods to put it on separate thread from the rest
class Gui(threading.Thread):
    window = tk.Tk()
    bg_color = "#f2a900"
    infinite = tk.IntVar()
    no_edit_label = tk.Label(window, bg=bg_color, text="Enter amount of wallets to be tried:", font="none 11")
    terminal_output_as_object = tk.Text(window, height=11, width=56, state="disabled")
    check_button = tk.Checkbutton(window, bg=bg_color, text='Infinite', variable=infinite)
    counters = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.wallet_amount_text = tk.Text(self.window, height=1, width=10, state="normal")
        self.window.title("Wallet Bruteforce")
        self.window.configure(bg=self.bg_color)
        self.window.geometry("460x310")
        # no_edit_label
        self.no_edit_label.place(x=0, y=15, anchor=W)
        # text field
        self.wallet_amount_text.place(x=280, y=15, anchor=W)
        self.wallet_amount_text.focus()
        # terminal output
        self.terminal_output_as_object.place(x=2, y=145, anchor=W)
        # checkbox for infinite loop
        self.check_button.place(x=388, y=15, anchor=W)
        # start button
        tk.Button(text="start",
                  command=lambda:
                  self.get_value_from_textbox(self.infinite.get(), self.wallet_amount_text.get("1.0", "end-1c")),
                  height=1, width=25).place(
            x=10, y=285, anchor=W)
        # stop button
        tk.Button(text="stop program", command=remove_traces, height=1, width=25).place(
            x=240, y=285, anchor=W)
        tk.mainloop()

    def update_terminal(self, terminal_input):
        self.terminal_output_as_object.configure(state="normal")
        self.terminal_output_as_object.insert("end", terminal_input + "\n")
        self.terminal_output_as_object.see("end")
        self.window.update()
        self.terminal_output_as_object.configure(state="disabled")
        self.counters += 1

    def get_value_from_textbox(self, infinite, wallet_amount):
        print("getting value")
        self.change_color(self.bg_color),
        if infinite == 1:
            while True:
                main(1000)
        else:
            try:
                wallet_amount_as_int = int(wallet_amount)
                main(wallet_amount_as_int)
                self.wallet_amount_text.configure(state="disabled")
            except ValueError:
                showinfo("Error", "Enter a valid number or check infinite box")

    def stop_gui(self, window):
        window.destroy()

    def change_color(self, color):
        print(color)
        self.window.configure(bg=color)
        self.no_edit_label.configure(bg=color)
        self.check_button.configure(bg=color)
        self.window.update()


ui = Gui()
ui.start()
