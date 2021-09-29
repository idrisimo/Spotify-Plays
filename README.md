
# Spotify Streams Scraper - wip

## Description
This script Scapes the Spotify to gather data on the number of times an artists song was played on Spotify and places that data into a spreadsheet. 

## Example
Click on image below to see script in action:

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/c7x5y68JQpU/0.jpg)](http://www.youtube.com/watch?v=c7x5y68JQpU)

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

### mainV2.py 
- this contains the the main bulk of the scripting. the process for this is as follows:

1) The links are grabbed from the spreadsheet, and opens the spotify page for the artist.

2) Goes through an artist's discography to load all the json queries into the chrome logs

3) Once all queries are loaded, the data is collected, put into a dataframe, cleaned up, then copied into middle.csv.

### Addition usage notes
This script uses threadpooling. if you the script is taking up too much of your pc's resources, it would be advisable to reduce the number of max workers in mainV2.py

## Support
If there are any bugs you find. please submit an issue ticket via [Github](https://github.com/idrisimo/Spotify-Plays). If you want to edit a project, just send me a message there as well or contact me via my email: idrissilva@hotmail.com

## Roadmap
- Add proper logging.
- More testing needs to be done for efficiency

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[TOBEADDED](https://choosealicense.com/licenses/mit/)
