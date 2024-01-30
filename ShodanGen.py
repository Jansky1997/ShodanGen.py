import random
import string
from time import sleep
import requests
import re
import json
from colorama import init, Fore, Style
import pyfiglet
from concurrent.futures import ThreadPoolExecutor
import argparse
import logging

# Initialisieren von Colorama
init()
# Initialisieren des Loggers
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger()

class Mailer:
    def __init__(self, user_agent="Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"):
        self.session = requests.session()
        self.session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "upgrade-insecure-requests": "1",
            "user-agent": user_agent
        }

    def create_email(self, min_len=10, max_len=10):
        self.session.get("https://temp-mail.io/en")
        data = {
            "min_name_length": str(min_len),
            "max_name_length": str(max_len)
        }
        email = json.loads(self.session.post(
            "https://api.internal.temp-mail.io/api/v2/email/new", data=data).text)["email"]
        return email

    def read_messages(self, email):
        return self.session.get(f"https://api.internal.temp-mail.io/api/v2/email/{email}/messages").content.decode("utf-8")

    def close_session(self):
        self.session.close()

class ShodanGenerator:
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            "origin": "https://account.shodan.io",
            "referer": "https://account.shodan.io/register",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        }
        self.mailer = Mailer()

    def create_account(self, username=None):
        if not username:
            username = self.create_random_username()
        email = self.mailer.create_email()
        page = self.session.get("https://account.shodan.io/register")
        token = re.search(r'csrf_token.*="(\w*)"',
                          page.content.decode("utf-8")).group(1)
        
        # Kennwort automatisch generieren
        password = self.generate_password()
        
        data = {
            "username": username,
            "password": password,
            "password_confirm": password,
            "email": email,
            "csrf_token": token
        }
        response = self.session.post("https://account.shodan.io/register", data=data)
        if response.ok:
            return email, username, password
        else:
            return None, None, None

    def activate_account(self, email, max_retries=15):
        for _ in range(max_retries):
            activation_link = re.search(r'(https://account.shodan.io/activate/\w*)', self.mailer.read_messages(email))
            if activation_link:
                activation_response = self.session.get(activation_link.group(1))
                if activation_response.ok:
                    return True
            sleep(1)
        return False

    def create_random_username(self, length=8):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def generate_password(self, length=12):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    def close_session(self):
        self.session.close()

def print_banner():
    banner_text = pyfiglet.figlet_format("ShodanGen.py", font="slant")
    print(Fore.CYAN + banner_text)
    print(Fore.YELLOW + "Created by Jansky1997")
    print()

def create_accounts(num_accounts, output_file=None, threads=5, max_retries=15):
    results = []
    generator = ShodanGenerator()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(generator.create_account) for _ in range(num_accounts)]
    
    for i, future in enumerate(futures):
        try:
            email, username, password = future.result()
            if email:
                results.append((username, password, email))
                logger.info(f"Account {i+1}: Successfully created.")
                sleep(1)
                if generator.activate_account(email, max_retries):
                    logger.info(f"Account {i+1}: Successfully activated.")
                else:
                    logger.error(f"Account {i+1}: Failed to activate.")
            else:
                logger.error(f"Account {i+1}: Failed to create.")
        except Exception as e:
            logger.error(f"Account {i+1}: {str(e)}")

    generator.close_session()

    if output_file:
        with open(output_file, "w") as file:
            for username, password, email in results:
                file.write(f"User: {username}\nPass: {password}\nEmail: {email}\n\n")
        logger.info(f"Account information saved to {output_file}")
    else:
        print(Style.RESET_ALL + "\nAccounts:")
        for username, password, email in results:
            print(f"User: {username}\nPass: {password}\nEmail: {email}\n")
        print(Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(description='Generate Shodan accounts.')
    parser.add_argument('num_accounts', type=int, help='Number of accounts to create')
    parser.add_argument('-o', '--output', type=str, help='Output file for account information')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of threads to use')
    parser.add_argument('-m', '--max-retries', type=int, default=15, help='Maximum number of activation retries')
    
    args = parser.parse_args()
    
    print_banner()
    create_accounts(args.num_accounts, args.output, args.threads, args.max_retries)

if __name__ == "__main__":
    main()
