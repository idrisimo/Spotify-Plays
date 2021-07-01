from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import sys
import json
from datetime import date


class AccountManagement:

    def create_session(self):
        print("Creating Session")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path=os.path.join(sys.path[0], 'chromedriver.exe'), options=chrome_options)

    def register_account(self, email_address, username):
        print('starting registration')
        url = "https://chartmasters.org/membership-account/membership-checkout/?level=1"
        self.browser.get(url)
        print('Loading registration page...')
        try:
            WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.ID, 'pmpro_btn-submit')))
            print('Page loaded, entering details...')
            # Will need to enter code here for clicking all the right buttons.
            username_input = self.browser.find_element_by_id('username').send_keys(username)
            print('Username added.')
            password_input = self.browser.find_element_by_id('password').send_keys('password1123')
            c_password_input = self.browser.find_element_by_id('password2').send_keys('password1123')
            print('Password added and confirmed.')
            email_address_input = self.browser.find_element_by_id('bemail').send_keys(email_address)
            c_email_address_input = self.browser.find_element_by_id('bconfirmemail').send_keys(email_address)
            print('Email added and confirmed.')
            terms_of_service_check = self.browser.find_element_by_id('tos').click()
            print('Terms Of Service clicked')
            submit_button =self.browser.find_element_by_id('pmpro_btn-submit')
            ActionChains(self.browser).move_to_element(submit_button).click(on_element=submit_button).perform()
            print('Clicked submit')
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.ID, 'pmpro_btn-submit')))
            submit_button = self.browser.find_element_by_id('pmpro_btn-submit')
            ActionChains(self.browser).move_to_element(submit_button).click(on_element=submit_button).perform()
            print('Clicked submit again.')
            print('details added, and submitted')
        except TimeoutException:
            print('an error has occured in the registration process. Browser Timed out.')

    def validate_account(self, varification_url):
        self.browser.get(varification_url)
        print('account varified')
        self.browser.quit()

    def login(self, username, password):
        print('Logging in...')
        login_url = 'https://chartmasters.org/login/'
        self.browser.get(login_url)
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.ID, 'wp-submit')))
        self.browser.find_element_by_id('user_login').send_keys(username)  # username input
        self.browser.find_element_by_id('user_pass').send_keys(password)  # password input
        self.browser.find_element_by_id('wp-submit').click()  # login button
        print('Logged in')

    def resend_validation_email(self):
        self.browser.get('https://chartmasters.org/membership-account/?resendconfirmation=1')

    # Saves the email dict as a json file
    def update_account_usage(self, account, out_of_searches):
        print('Saving date to JSON...')
        with open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r+') as json_file:
            json_data = json.load(json_file)
            json_data['accounts'][account]['date_last_used'] = str(date.today())
            json_data['accounts'][account]['out_of_searches'] = out_of_searches
            json_data['accounts'].update(json_data['accounts'])
            json_file.seek(0)
            json.dump(json_data, json_file, indent=2)
            json_file.truncate()
            json_file.close()
            print('JSON updated and saved')

    def remove_invalid_accounts(self):
        with open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r+') as json_file:
            json_data = json.load(json_file)

            json_data['accounts'] = {username: details for username, details in json_data['accounts'].items() if details['email_validated']}
            json_data['accounts'].update(json_data['accounts'])
            json_file.seek(0)
            json.dump(json_data, json_file, indent=2)
            json_file.truncate()
            json_file.close()
            print('JSON updated and saved. Removed dead accounts.')

    def get_new_usable_account(self):
        print('Grabbing another account')
        user_details_json = json.load(open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r'))
        for username, details in user_details_json['accounts'].items():
            if details['email_validated'] and details['out_of_searches'] > 0:
                return username

    def quit_browser(self):
        self.browser.quit()
