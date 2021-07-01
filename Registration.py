from AccountManagement import AccountManagement
from TempMailApi import TempEmailController
import json
import os
import sys
import time
import re
import concurrent.futures
def register_new_accounts(amount_needed):

    account_management = AccountManagement()
    email_controller = TempEmailController()
    domain_list = email_controller.domain_list()
    username_list = email_controller.username_generator(amount_needed)
    email_list = email_controller.create_email(username_list, domain_list)
    email_dict = email_controller.email_hasher(email_list)
    email_controller.save_to_json(email_dict)
    user_details_json = json.load(open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r'))
    for username, details in user_details_json['accounts'].items():
        if not details['email_validated']:
            print(username)
            email_address = details['email']
            hashed_email = details['hashed_email']

            # Register account
            registration_attempts = 0
            while registration_attempts <= 5:
                try:
                    account_management.create_session()
                    account_management.register_account(email_address=email_address,
                                                        username=username)
                    details['account_registered'] = True
                    break
                except Exception:
                    registration_attempts += 1
                    print(f'An error occured during the registration process, maybe an issue with popups? '
                          f'Number of attempts: {registration_attempts}')

            # Breaks down the email string into a list so we can then use regex easier on it.
            # TODO set up if statement if the account has not been registered yet
            # TODO set up resend validation email.
            validation_attempts = 0
            while validation_attempts <= 3:
                try:
                    time.sleep(3)
                    validate_email = email_controller.get_email(hashed_email_address=hashed_email)\
                        .lstrip('[')\
                        .rstrip(']')\
                        .replace('\"', '')\
                        .split(',')
                    validation_url = re.search("<a href='(.*?)'>", validate_email[10]).group(1)
                    account_management.validate_account(validation_url)
                    details['email_validated'] = True
                    break
                except Exception:
                    validation_attempts += 1
                    print(f'issue with inbox, there may be no email. Number of attempts: {validation_attempts}')
        else:
            continue
    email_controller.save_to_json(user_details_json)
    account_management.quit_browser()

register_new_accounts(10)