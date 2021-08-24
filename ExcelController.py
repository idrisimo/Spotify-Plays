import re
import sys
import os
import pandas as pd

class WorkbookController:

    def initialise(self):
        artist_links = pd.read_excel(os.path.join(sys.path[0], 'spotify-data-spreadsheet.xlsm'))
        artist_links.dropna(subset=['Artist Link'], inplace=True)
        if artist_links.empty:
            print('No links in spreadsheet. Did you save before running script?')
            input('Press ANY key to quit...')
            exit()
        return artist_links

    def get_artist_id(self, link):
        try:
            artist_id = re.search("artist/(.*?)\?si=", str(link)).group(1)
        except:
            artist_id = re.search("artist/(\w+)", str(link)).group(1)
        return artist_id