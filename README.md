
# Spotify Streams Scraper - wip

## Description
This script Scapes chartmasters.org to gather data on the number of times an artists song was played on Spotify and places that data into a spreadsheet. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.

```bash
pip install requirements.txt
```
This script is also running off of Python 3.8.


## Usage
The Script has 3 main pieces:

### spotify-plays.xlsx 
- This is where you place your links for the artist (place in Sheet1 column A). It also has the button to run the script. heading to the data tab and clicking "Refresh" after you have run the script will update the spreadsheet with the new data. 

### middle.csv 
- this is a go between. The python script will scrape data and place it into this CSV file, which is then read by the excel spreadsheet.

### main.py 
- this contains the the main bulk of the scripting. the process for this is as follows:

1) The links are grabbed from the spreadsheet. It counts the number of usable accounts as well as the number of searches they have left vs the number of links in the spreadsheet. If there are enough searches left it will move onto the next stage.

2) Iterating through the links it logs into an account and searches for the artist.

3) Once the artist is found, the table generated is then taken from the site, put into a dataframe, cleaned up, then copied into middle.csv.

### Other scripts to be aware of:
Registration.py - This script creates new accounts using temp-email api. The only input for this script is the number of accounts that need to be created. 
(02/07/2021 - Currently this script can only be run by calling the script directly in command prompt and entering the number of accounts wanted when asked.
To Run script, Enter in the below:)
```Bash
C:\script\directory\here python Registration.py
```


### API setup:
The script also uses [Temp-mail api](https://rapidapi.com/Privatix/api/temp-mail) to create accounts as such you will need to sign up and create an account once set up, grab the api key (02/07/2021 - currently environmental variables have not been set up. As such you will need to go into TempMailApi.py and add your API key to the header found on line 13.)


## Support
If there are any bugs you find. please submit an issue ticket via [Github](https://github.com/idrisimo/Spotify-Plays). If you want to edit a project, just send me a message there as well or contact me via my email: idrissilva@hotmail.com

## Roadmap
- Sort out environmental variables so that the tempmail api is not hard coded 
- Add a button to the spreadsheet for account creation.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[TOBEADDED](https://choosealicense.com/licenses/mit/)
