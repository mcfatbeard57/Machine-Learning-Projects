# -*- coding: utf-8 -*-
"""
Air Qualoty index file.
    Web Scraping
"""

# IMPORTS
import os
import time
import requests
import sys

# Defining a function to retrieve HTML
def retrieve_html():
    for year in range(2013,2019):
        for month in range(1,13):
            if(month<10):
                url = 'https://en.tutiempo.net/climate/0{}-{}/ws-432950.html'.format(month,year)
            else:
                url = 'https://en.tutiempo.net/climate/{}-{}/ws-432950.html'.format(month,year)
     
            texts = requests.get(url)
            text_utf = texts.text.encode('utf=8')        #Must do utf encoding 
            
            # check if Directory exists, if not create it
            if not os.path.exists("Data/html_Data/{}".format(year)):
                os.makedirs("Data/html_Data/{}".format(year))
            # Open helps opening a folder
            with open ("Data/Html_Data/{}/{}.html".format(year,month),"wb") as output:
                output.write(text_utf)
        
        sys.stdout.flush()

# Write main function        
if __name__ == "__main__":
    start_time = time.time()
    retrieve_html()
    stop_time = time.time()
    print("Time Taken : {}".format(stop_time-start_time))