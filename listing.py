from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup # For HTML parsing



class Listing:

    totalPages = None

    def __init__(self,driver):
        self.driver = driver
    
    def parse(self,page):
        mainUrl='https://www.amiami.com/eng/search/list/?s_cate3=9713&pagecnt='+ str(page) +'&s_cate_tag=1'
        try:
            self.driver.get(mainUrl)
            # wait for items to be loaded, 20 items per page
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//ul[@class='new-items__inner'] / li[19]")))
            print ("Page is ready!")
            html = self.driver.page_source
            res = self.parseDetail(html)
            print ("done parsing: ")
            return res

        except TimeoutException:
            print ("Loading took too much time!")

        return 'testing'

    def parseDetail(self,html):
        output = []
        soup = BeautifulSoup(html, 'lxml')
        pagers = soup.find(class_='pager-list').findAll('li')
        self.totalPages = int(pagers[-1].find('a').getText())
        items = soup.find(class_='new-items__inner').findAll('a', href=True)
        # print(len(items))
        for item in items:
            gcode = item['href'].replace('/eng/detail/?gcode=','')
            # print(gcode)
            output.append(gcode)
        return output

