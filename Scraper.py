import time
import json
import sys
import os
import re
import html5lib
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from TempMailApi import TempEmailController
from datetime import date


# TODO Uses selenium to start a browser in headless mode, search the data and returns the html page for scraping
class ScraperController:

    def __init__(self,  password):
        self.password = password

    def create_session(self):
        print("Creating Session")
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path=os.path.join(sys.path[0], 'chromedriver.exe'), options=chrome_options)
        

    def get_session_id(self):
        session_id = self.browser.session_id
        return session_id

    # Gets cookies and stores them in their own file so that it the login function is not always needed.
    def get_new_cookies(self, username):
        print('Getting cookies...')
        json.dump(self.browser.get_cookies(), open(os.path.join(sys.path[0], f'cookie_jar\\{username}_cookie_data.json'), 'w'))
        print('New cookies in the jar')

    # Loads the selected users cookies into the new session so login does not need to be called
    def load_cookies(self, username):
        print('Taking cookies out of jar...')
        login_url = 'https://chartmasters.org/login/'
        self.browser.get(login_url)
        cookies = json.load(open(os.path.join(sys.path[0], f'cookie_jar\\{username}_cookie_data.json'), 'r'))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        print('Cookies loaded')
        self.browser.refresh()
        print('Refreshing page')

    def login(self, username):
        print('Logging in...')
        login_url = 'https://chartmasters.org/login/'
        self.browser.get(login_url)
        WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.ID, 'wp-submit')))
        self.browser.find_element_by_id('cookie_action_close_header').click()
        self.browser.find_element_by_id('user_login').send_keys(username)  # username input
        self.browser.find_element_by_id('user_pass').send_keys(self.password)  # password input
        actions = ActionChains(self.browser)
        login_button = self.browser.find_element_by_id('wp-submit')  # login button
        actions.move_to_element(login_button).perform()
        login_button.click()
        print('Logged in')

    def search_artist(self, artist_id):
        print('Searching selected artist...')
        streams_data_url = f'https://chartmasters.org/spotify-streaming-numbers-tool' \
                           f'/?artist_id={artist_id}&displayView=topSongs'
        self.browser.get(streams_data_url)
        print('Artist details loaded')

    def get_search_page(self):
        url = 'https://chartmasters.org/spotify-streaming-numbers-tool/'
        self.browser.get(url)

    def html_page_grabber(self):
        print('Grabbing page ready for parsing...')
        page_html = self.browser.page_source
        #self.browser.quit()
        print('Page grabbed')
        return page_html

    def check_if_artist_exist(self):
        try:
            check = self.browser.find_element_by_xpath('//br[contains(text(), "No results found. No credit has been discounted.")]')
            print('artist found')
        except:
            check = ''
            print('artist not found')
        if check == '':
            print('returning true')
            return True
        else:
            print('returning false')
            return False
    def check_for_table(self):
        try:
            self.browser.find_element_by_id("resultsTable")
            print('Table exists')
            return True
        except:
            print('Table does not exists')
            return False

    def check_number_of_searches_left(self):
        search_credits = self.browser.find_element_by_xpath('//*[@id="page-11228"]/div[1]/b')

        if search_credits.text != 'It appears that you have no search credit available.':
            number_of_searches = re.findall(r'\d+', search_credits.text)
            return int(number_of_searches[0])
        else:
            return 0

    # TODO Go through the soup, pickup the alphabits
    def soup_siv(self, html_page):
        print('Starting soup siv...')
        soup = BeautifulSoup(html_page, 'html.parser')
        artist_name = soup.find_all('h2', text={re.compile("Streams on Spotify:")})

        artist_name = re.search("Streams on Spotify: (.*?) - Top Songs View", artist_name[0].text).group(1)
        print(artist_name)
        results_table = soup.find_all('table', attrs={'id': 'resultsTable'})
        try:
            df = pd.read_html(str(results_table))
            df = df[0].drop(['EAS', '#'], 1)
            if len(df) > 1:
                df = df[:-1]
            df['Artist'] = artist_name
        except ValueError as e:
            df = e
            print(f'An error occured: {e}')
        return df

    def delete_cookies(self):
        print('deleting cookies')
        self.browser.delete_all_cookies()
    def quit_browser(self):
        self.browser.quit()

