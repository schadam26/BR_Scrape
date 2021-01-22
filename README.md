# BR_Scrape
Python script which scrapes play-by-play data from Basketball-Reference.com

** wrote this a few years ago when I was learning Python, its not the prettiest script but it works
** written for a Mac

How to use this script:
1. Fill gamelinks.txt with game links from Basketball Reference (look at gamelinks.txt to see what it should look like)
2. Run the script via the command line "python3 scrape_pbp.py"

Things to know:
1. As the script runs through the game links it will print them out. Currently after every fifteen games it scrapes, the script pauses for 20 seconds. This was to keep my computer from over-heating. You can change this if you want to speed it up.
2. You can exit at any time with control-C. The links that you've already run through will be printed out into a file called "donelinks.txt". When you start up again the script will pick up with the games you still have left to scrape.
3. Everytime you pause the script/when the script runs through all of the links it outputs the scraped data into a CSV file called "output_pbp.csv". 

Feel free to improve this script! Also you can find PBP data that I've already scraped on Kaggle --> https://www.kaggle.com/schmadam97/nba-playbyplay-data-20182019 
