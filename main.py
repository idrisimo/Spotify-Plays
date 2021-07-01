from TempMailApi import TempEmailController
from Scraper import ScraperController
from AccountManagement import AccountManagement
from ExcelController import WorkbookController
from spotify_info_wrapper import SpotifySongGen
from datetime import date
import pandas as pd
import numpy as np
import json
from pprint import pprint
from json import JSONDecodeError
import re
import time
import concurrent.futures
import sys
import os
import math

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
            while registration_attempts < 3:
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
            while validation_attempts < 5:
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



def excel_initialiser():

    # Setup for excel spreadsheet
    worksheet = WorkbookController()
    sheet_data = worksheet.initialise()
    #sheet_headers = next(sheet_data)[0:]

    # pandas settings
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(desired_width)
    pd.set_option('display.max_columns', 10)

    # Move data from spreadsheet onto a dataframe
    excel_df = pd.DataFrame({'Artist Link': sheet_data})
    # Add 2 extra columns

    # TODO refactor account checking and updating to be more streamlined
    # open and select usable accounts
    user_details_json = json.load(open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r'))
    user_dict = {user: details for (user, details) in user_details_json['accounts'].items()
                 if details['email_validated'] and details['out_of_searches'] > 0}
    # Gets the total amount of searches vs the total number of links. Will be used for account creation.
    number_of_links = len(excel_df['Artist Link'])
    number_of_searches = sum([details['out_of_searches'] for details in user_dict.values()])
    number_of_accounts_needed = math.ceil((number_of_links - number_of_searches) / 3)
    print(f'number of links: {number_of_links}\n'
          f'number of searches: {number_of_searches}\n'
          f'number of accounts needed: {number_of_accounts_needed}')
    if number_of_accounts_needed > 0:
        print(f'Not enough searches left. Either create {number_of_accounts_needed} more or wait to for older accounts to refresh.')
        exit()


    for df_index, row in excel_df.iterrows():
        artist_id = worksheet.get_artist_id(row['Artist Link'])
        row['Artist Link'] = artist_id
        excel_df.at[df_index] = row

    return excel_df



def main(excel_df_data):
    account_management = AccountManagement()
    excel_df_row = excel_df_data[1]
    #username = excel_df_row['Assigned Account']
    artist_id = excel_df_row['Artist Link']

    def load_users():
        user_details_json = json.load(open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r'))
        user_dict = {user: details for (user, details) in user_details_json['accounts'].items()
                     if details['email_validated'] and details['out_of_searches'] > 0 or details['date_last_used'] < str(date.today())}
        return user_dict
    username_list = [username for username in load_users().keys()]

    browser_instance = ScraperController('password1123')
    browser_instance.create_session()
    stop = False
    count = 0
    while not stop:
        username = username_list[count]
        print(username)
        try:
            if load_users()[username]['date_last_used'] >= str(date.today()):
                browser_instance.load_cookies(username)
            else:
                browser_instance.delete_cookies()
                browser_instance.login(username)
                browser_instance.get_new_cookies(username)
        except:
            browser_instance.delete_cookies()
            browser_instance.login(username)
            browser_instance.get_new_cookies(username)
        browser_instance.search_artist(artist_id)
        check_searches_left = browser_instance.check_number_of_searches_left()
        if check_searches_left > 0:
            if browser_instance.check_if_artist_exist():
                if browser_instance.check_for_table() == False:
                    browser_instance.search_artist(artist_id)
                html_page = browser_instance.html_page_grabber()
                page_data = browser_instance.soup_siv(html_page)
                account_management.update_account_usage(username, check_searches_left)
                stop = True
            else:
                page_data = pd.DataFrame({'Artist': [artist_id],
                                          'Album': ['Not found'],
                                          'Song': ['Not found'],
                                          'Streams': ['Not found']})
            page_data = page_data.reindex(columns=['Artist',
                                                   'Album',
                                                   'Song',
                                                   'Streams'])
            browser_instance.quit_browser()
            current_data = pd.read_csv(os.path.join(sys.path[0], r'middle.csv'))
            if current_data.empty:
                page_data.to_csv(os.path.join(sys.path[0], r'middle.csv'), index=False)
            else:
                new_data = pd.concat([current_data, page_data]).drop_duplicates(['Artist', 'Album', 'Song', 'Streams'], keep='last')
                new_data.to_csv(os.path.join(sys.path[0], r'middle.csv'), index=False)

        else:
            account_management.update_account_usage(username, check_searches_left)
            count += 1
            print('no searches')
            if count >= len(username_list):
                username_list = load_users().keys()
                print('username_list updated')


if __name__ == '__main__':
    start_time = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        df_results = {executor.submit(main, df_row) for df_row in excel_initialiser().iterrows()}

    end_time = time.perf_counter()
    print(f'script took {end_time - start_time} second(s) to finish')
    input('Press ANY key to close console...')



