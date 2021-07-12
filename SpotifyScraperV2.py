from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

from urllib.parse import unquote
import pandas as pd
import sys
import os

class ScraperController:

    def create_session(self):
        print("Creating Session")
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # suppresses errors that spawn when running code from excel sheet
        self.browser = webdriver.Chrome(executable_path=os.path.join(sys.path[0], 'chromedriver.exe'),
                                   options=chrome_options,
                                   desired_capabilities=capabilities)

    def get_discography(self, artist_id):
        print("Loading Artist's Page...")
        self.browser.get(f'https://open.spotify.com/artist/{artist_id}')
        # Handle Cookie popup
        WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        print('Accepting cookies...')
        self.browser.find_element_by_id('onetrust-accept-btn-handler').click()
        time.sleep(0.5)
        # Open Discography page
        see_discography = self.browser.find_element_by_xpath('//span[contains(text(), "See discography")]')
        print('Opening discography...')
        see_discography.click()
        WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/main/div[2]/div[2]/div/div/div[2]/section/div[1]/button[2]')))
        time.sleep(5)
        self.browser.find_element_by_xpath(
            '//*[@id="main"]/div/div[2]/div[3]/main/div[2]/div[2]/div/div/div[2]/section/div[1]/button[2]').click()

    def get_album_names(self):
        print('Getting Album names...')
        all_albums = self.browser.find_elements_by_xpath('//a[contains(@href, "/album/")]')
        columns = ['Album ID', 'Album Name']
        album_rows = []
        for album in all_albums:
            album_link = album.get_attribute('href')
            album_rows.append([re.search('album/(.*?)$', album_link).group(1), album.text])
        album_data = pd.DataFrame(album_rows, columns=columns)
        return album_data

    def scroll_through_album_collection(self):
        print('scrolling to bottom...')
        for album_pos_num in range(len(self.browser.find_elements_by_class_name('contentSpacing'))):
            self.browser.execute_script(
                f"document.getElementsByClassName('contentSpacing')[{album_pos_num}].scrollIntoView()")
            time.sleep(0.5)
        print('bottom reached.')

    def open_discography_type(self):
        print('Open/Close music collection...')
        collection_dropdown = self.browser.find_element_by_xpath(
            '//*[@id="main"]/div/div[2]/div[3]/main/div[2]/div[2]/div/div/div[2]/section/div[1]/button[1]')
        collection_dropdown.click()

    def click_discography(self, num):
        discography_button = self.browser.find_element_by_xpath(f'//*[@id="context-menu"]/ul/li[{num}]')
        print(f'Clicking button for: {discography_button.text}...')
        discography_button.click()

    def get_num_discography_types(self):  # This is used to grab the number of discography types so that the dropdown can be iterated through.
        self.open_discography_type()
        discography_count = self.browser.find_elements_by_xpath('//*[@id="context-menu"]/ul/li')
        self.open_discography_type()
        return len(discography_count)

    def har_file_data_collection(self):  # Grabs data from chrome devtools network tab.
        # extract requests from logs
        print('Gettings Chrome har files')
        logs_raw = self.browser.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        def log_filter(log_):
            return (
                # is an actual response
                    log_["method"] == "Network.responseReceived"
                    # and json
                    and "json" in log_["params"]["response"]["mimeType"]
            )

        music_rows = []
        columns = ['Artist Name', 'Album Name', 'Songs', 'Play Count']
        for log in filter(log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if '/query?operationName=queryAlbum' in resp_url:
                resp_url = unquote(resp_url)
                album_id = re.search('album:(.*?)"', resp_url).group(1)
                dataset = self.browser.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                json_file = json.loads(dataset['body'])
                if 'album' in json_file['data'].keys():
                    tracks = json_file['data']['album']['tracks']['items']
                    for track in tracks:
                        track = track['track']
                        artist_name = track['artists']['items'][0]['profile']['name']
                        track_name = track['name']
                        play_count = track['playcount']
                        music_rows.append([artist_name, album_id, track_name, play_count])
        final_music_dataframe = pd.DataFrame(music_rows, columns=columns)
        return final_music_dataframe

    def quit_session(self):
        self.browser.quit()
        print('Closing and quiting browser.')