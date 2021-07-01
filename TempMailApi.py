import requests
import hashlib
import json
from random import randint
import os
import sys

# TODO set limiter on api calls.
class TempEmailController:
    # Tempmail api from: https://rapidapi.com/Privatix/api/temp-mail/details
    def __init__(self):
        self.headers = {
            'x-rapidapi-key': "8fb1c6f72fmsh5a64a28cb348619p1eec67jsnf1bb10b11b6a",
            'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
        }

    # Gets list of domains currently available
    def domain_list(self):
        print('Generating domains')
        url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
        response = requests.request("GET", url, headers=self.headers)
        return response.text.lstrip('[').rstrip(']').replace('\"', '').split(',')

    # Create random usernames via 3 different methods
    def username_generator(self, names_needed):
        print('Generating list of usernames')
        username_list = []
        for num in range(names_needed):
            rand_selector = randint(0, 3)
            if rand_selector == 0:
                words_file = open(os.path.join(sys.path[0], r'username_generator_materials\words.text'), 'r')
                word_list = words_file.read().split()
                words_file.close()
                cleaned_word_list = [word for word in word_list if not "'" in word]
                random_username = f"{cleaned_word_list[randint(0, len(cleaned_word_list))]}{randint(0, 99)}"
            elif rand_selector >= 1:
                firstname_file = open(os.path.join(sys.path[0], r'username_generator_materials\firstname.txt'), 'r')
                firstname_list = firstname_file.read().split()
                firstname_file.close()
                selected_firstname = firstname_list[randint(0, len(firstname_list))].lower()
                if rand_selector == 1:
                    random_username = f"{selected_firstname}{randint(0, 99)}"
                elif rand_selector >= 2:
                    lastname_file = open(os.path.join(sys.path[0], r'username_generator_materials\lastname.txt'), 'r')
                    lastname_list = lastname_file.read().split()
                    lastname_file.close()
                    selected_lastname = lastname_list[randint(0, len(lastname_list))].lower()
                    if rand_selector == 2:
                        random_username = f"{selected_firstname}{selected_lastname}{randint(0, 9)}"
                    else:
                        random_username = f"{selected_firstname[0]}{selected_lastname}{randint(0, 999)}"
            username_list.append(random_username)
        return username_list

    # Create pool of emails
    def create_email(self, username_list, domain_list):
        print('splicing usernames with random domains...')
        email_list = []
        for username in username_list:
            random_num = randint(0, len(domain_list)) - 1
            full_email = f"{username}{domain_list[random_num]}"
            email_list.append(full_email)
        return email_list

    # Hash email address (md5)
    def email_hasher(self, email_list):
        print('encrypting email address...')
        email_dict = {'accounts': {}}
        for email in email_list:
            hashed_email = hashlib.md5(email.encode())

            email_dict['accounts'][email.split('@')[0]] = {
                                      'email': email,
                                      'hashed_email': hashed_email.hexdigest(),
                                      'out_of_searches': 3,
                                      'account_registered': False,
                                      'email_validated': False,
                                      'date_last_used': ''}
        return email_dict

    # Saves the email dict as a json file
    def save_to_json(self, email_dict):
        print('Saving to JSON...')
        try:
            with open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'r+') as json_file:
                json_data = json.load(json_file)
                json_data['accounts'].update(email_dict['accounts'])
                json_file.seek(0)
                json.dump(json_data, json_file, indent=2)
                json_file.truncate()
                json_file.close()
                print('JSON updated and saved')
        except:
            json_file = open(os.path.join(sys.path[0], r'username_generator_materials\useremails.json'), 'a+')
            json.dump(email_dict, json_file, indent=2)
            json_file.close()
            print('JSON created and saved')

    # Get emails for email address
    def get_email(self, hashed_email_address):
        print('Getting mail')
        url = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{hashed_email_address}/"
        response = requests.request("GET", url, headers=self.headers)
        return response.text
