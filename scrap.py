
from time import sleep # To prevent overwhelming the server between connections
from collections import Counter # Keep track of our term counts
import pandas as pd # For converting results to a dataframe and bar chart plots
import json # For parsing json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from figure import Figure
from listing import Listing
import pandas as pd 

# instantiate a chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # run invisible, faster
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--log-level=3') # do not show the info level log
chrome_driver = os.getcwd() +"\\chromedriver.exe"
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)

def getFig(gcode):
    # get detail of a single figure
    fig = Figure(driver)
    res = fig.parse(gcode)
    # print(res)
    return res

def testListing():
    # get all the figure codes
    listing = Listing(driver)
    # test the 1st page
    items = listing.parse(1)
    print(items)
    print(listing.totalPages)
    lst = []
    for item in items:
        fig = getFig(item)
        lst.append(fig)
    saveList(lst,'data.csv')
    
def saveList(lst,name):
    df = pd.DataFrame(lst)
    hasHeader = True
    if df.shape[1] == 1:
        hasHeader = False
    df.to_csv (name, index = False, header=hasHeader)

# testListing()
# getFig('HOB-FIG-0812A')

def scrapAllListings():
    listing = Listing(driver)
    page = 1
    results = set()
    print('started parsing')
    while listing.totalPages == None or page <= listing.totalPages:
        print('parsing page '+str(page))
        items = listing.parse(page)
        print(items)
        # save the 20 new items
        results.update(items)
        saveList(results,'listings.csv')
        # go to next page
        page += 1
    print('done parsing all listings')
    # last page will time out due to waiting for 20 items but has less than that. 
    # Ignore those data points.
    


# scrapAllListings()

def scrapAllItems():
    lst = pd.read_csv('listings.csv',header=None)  
    data = pd.read_csv('data.csv')
    need = lst[~lst[0].isin(data['gcode'])]
    print(str(need.shape[0]) + " items")
    results = []
    
    for i, row in need.iterrows():
        print('Parsing item #'+str(i))
        fig = getFig(row[0])
        if fig != None:
            results.append(fig)
        # save to disk every 20 items
        if i % 20 == 0:
            saveList(results,'data.csv')


scrapAllItems()

# close
driver.quit() 
