from random import randint
import sqlite3

class BankAccount:
    # all_accounts = []

    def __init__(self):
        self.account = None
        self.account_pin = None
        self.balance = 0
        self.authorized = False
        # db_file = open('card.s3db', 'a')
        # db_file.close()
        self.connection = sqlite3.connect('card.s3db')
        self.cursor = self.connection.cursor()
        # self.cursor.execute('CREATE DATABASE card;')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS card (
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0);''')
        self.connection.commit()
        self.manage_by_menu()

    def manage_by_menu(self):
        while not self.authorized:
            print("1. Create an account\n2. Log into account\n0. Exit\n")
            user_input = input()
            if user_input == "1":
                self.create_an_account()
            elif user_input == "2":
                self.log_into_account()
            elif user_input == "0":
                self.exit()
                break
            else:
                print("\nPlease, enter appropriate number of menu item (from 0 till 2)\n")

        while self.authorized:
            print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
            user_input = input()
            if user_input == "1":
                self.get_the_balance()
            elif user_input == "2":
                self.add_income()
            elif user_input == "3":
                self.do_transfer()
            elif user_input == "4":
                self.close_account()
            elif user_input == "5":
                self.log_out()
                self.manage_by_menu()
            elif user_input == "0":
                self.exit()
                break
            else:
                print("\nPlease, enter appropriate number of menu item (from 0 till 2)\n")


    def add_income(self):
        income = input("\nEnter income:\n")
        self.cursor.execute('UPDATE card SET balance = balance + ? WHERE number = ?;', (income, self.account))
        self.connection.commit()
        print("Income was added!\n")


    def do_transfer(self):
        where_transfer = input("\nTransfer\nEnter card number:\n")
        if where_transfer == self.account:
            print("You can't transfer money to the same account!\n")
            return None
        if not self.check_through_luhn_algorithm(where_transfer):
            print("Probably you made mistake in the card number. Please try again!\n")
            return None
        if self.check_for_unique(where_transfer):
            print("Such a card does not exist.\n")
            return None
        else:
            transfer_sum = int(input("\nEnter how much money you want to transfer:\n"))
            if transfer_sum > self.get_the_balance(print_result=False):
                print("Not enough money!\n")
                return None
            self.cursor.execute('UPDATE card SET balance = balance - ? WHERE number = ?;', (transfer_sum, self.account))
            self.cursor.execute('UPDATE card SET balance = balance + ? WHERE number = ?;', (transfer_sum, where_transfer))
            self.connection.commit()
            print("Success!\n")


    def close_account(self):
        self.cursor.execute('DELETE FROM card WHERE number = ?;', (self.account,))
        self.connection.commit()
        print("The account has been closed!\n")


    def check_for_unique(self, temporary_account):
        self.cursor.execute('SELECT number FROM card WHERE number = ?;', (temporary_account,))
        if self.cursor.fetchone() == None:
            return True
        return False
        # checking_result = True
        # for instance in BankAccount.all_accounts:
        #     if instance.account == temporary_account:
        #         checking_result = False
        # return checking_result

    def check_through_luhn_algorithm(self, account_number):
        account_sum = int(account_number[-1])
        is_odd = True
        for number in reversed(account_number[:-1]):
            number = int(number)
            if is_odd:
                number *= 2
                if number > 9:
                    number -= 9
            account_sum += number
            is_odd = not is_odd
        return account_sum % 10 == 0

    def find_the_checksum(self, temporary_account):
        account_sum = 0
        is_odd = True
        for number in reversed(temporary_account):
            number = int(number)
            if is_odd:
                number *= 2
                if number > 9:
                    number -= 9
            account_sum += number
            is_odd = not is_odd
        remainder = account_sum % 10
        if remainder == 0:
            return temporary_account + "0"
        else:
            return temporary_account + str(10 - remainder)

    def create_an_account(self):
        while True:
            temporary_account = "400000{}".format(randint(100000000, 999999999))
            temporary_account = self.find_the_checksum(temporary_account)
            if self.check_for_unique(temporary_account):
                break
        temporary_pin = self.generate_a_pin()
        self.cursor.execute('INSERT INTO card (number, pin) VALUES (?, ?);', (temporary_account, temporary_pin))
        self.connection.commit()
        print(f"\nYour card has been created\nYour card number:\n{temporary_account}\nYour card PIN:\n{temporary_pin}\n")
        # self.account = temporary_account
        # self.generate_a_pin()
        # BankAccount.all_accounts.append(self)
        # print(f"\nYour card has been created\nYour card number:\n{self.account}\nYour card PIN:\n{self.account_pin}\n")

    def generate_a_pin(self):
        account_pin = ''
        for _ in range(4):
            account_pin += str(randint(0, 9))
        return account_pin

    def log_into_account(self):
        card_number = input("Enter your card number:\n")
        pin_ = input("Enter your PIN:\n")
        self.cursor.execute('SELECT number, pin FROM card WHERE number = ? AND pin = ?;', (card_number, pin_))
        query_result = self.cursor.fetchone()
        if query_result:
            self.account, self.account_pin = query_result
            self.authorized = True
            print("\nYou have successfully logged in!\n")
            return None
        print("\nWrong card number or PIN!\n")
        return None
        # for instance in BankAccount.all_accounts:
        #     if instance.account == card_number and instance.account_pin == pin:
        #         self.authorized = True
        #         print("\nYou have successfully logged in!\n")
        #         return None
        # print("\nWrong card number or PIN!\n")
        # return None

    def get_the_balance(self, print_result=True):
        self.cursor.execute('SELECT balance FROM card WHERE number = ? AND pin = ?;', (self.account, self.account_pin))
        self.balance = self.cursor.fetchone()[0]
        if print_result:
            print(f"\nBalance: {self.balance}\n")
        else:
            return self.balance
        # print(f"\nBalance: {self.balance}")

    def log_out(self):
        self.authorized = False
        print("\nYou have successfully logged out!\n")

    def exit(self):
        # self.log_out()
        self.connection.close()
        print("\nBye!")


if __name__ == '__main__':
    new_client = BankAccount()
