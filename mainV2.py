import pandas as pd
import numpy as np
import time
import concurrent.futures
import sys
import os

from ExcelController import WorkbookController
from SpotifyScraperV2 import ScraperController

def excel_initialiser():

    # Setup for excel spreadsheet
    worksheet = WorkbookController()
    excel_df = worksheet.initialise()

    # pandas settings
    desired_width = 320
    pd.set_option('display.width', desired_width)
    np.set_printoptions(desired_width)
    pd.set_option('display.max_columns', 10)

    # Convert data link into artist ID
    for df_index, row in excel_df.iterrows():
        artist_id = worksheet.get_artist_id(row['Artist Link'])
        row['Artist Link'] = artist_id
        excel_df.at[df_index] = row
    return excel_df

def scrape_instance(excel_df_data):

    scraper_instance = ScraperController()
    excel_df_row = excel_df_data[1]
    artist_id = excel_df_row['Artist Link']
    scraper_instance.create_session()
    scraper_instance.get_discography(artist_id=artist_id)
    album_name_df_list = []
    first_run = True
    for num in range(scraper_instance.get_num_discography_types()):
        num += 1
        if first_run:
            first_run = False
            album_name_df_list.append(scraper_instance.get_album_names())
            scraper_instance.scroll_through_album_collection()
        else:
            scraper_instance.open_discography_type()
            scraper_instance.click_discography(num=num)
            time.sleep(0.5)
            album_name_df_list.append(scraper_instance.get_album_names())
            scraper_instance.scroll_through_album_collection()
    album_name_df = pd.concat(album_name_df_list)
    album_name_df.reset_index(drop=True, inplace=True)
    track_df = scraper_instance.har_file_data_collection()
    scraper_instance.quit_session()
    rename_dict = album_name_df.set_index('Album ID')['Album Name']
    renamed_df = track_df.replace(rename_dict)
    return renamed_df



if __name__ == '__main__':
    start_time = time.perf_counter()
    print('Starting script...')
    dataframe_list = []
    excel_data = excel_initialiser().iterrows()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(scrape_instance, excel_data, chunksize=10)
        for result in results:
            dataframe_list.append(result)
    dataframe = pd.concat(dataframe_list)
    dataframe.reset_index(drop=True, inplace=True)
    print('Saving data to CSV...')
    dataframe.to_csv(os.path.join(sys.path[0], r'middle.csv'), index=False)
    print()
    end_time = time.perf_counter()
    print(f'script took {end_time - start_time} second(s) to finish')
    input('Press ANY key to close console...')
