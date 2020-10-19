from bs4 import BeautifulSoup # For HTML parsing
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


waitTime = 5

class Figure:

    def __init__(self,driver):
        self.driver = driver

    def logError(self,msg,gcode):
        timestamp = datetime.now()
        with open("error.log", "a") as logf:
            logf.write(str(timestamp) + " - " +msg + " - " +gcode +"\n")
    
    def parse(self,gcode):
        page_url = 'https://www.amiami.com/eng/detail/?gcode='+gcode
        # wait until element is clickable
        try:
            self.driver.get(page_url)
            WebDriverWait(self.driver, waitTime).until(EC.presence_of_element_located((By.XPATH,"//section[@class='item-about'] / dl[7]")))
            # print ("Page is ready!")
            html = self.driver.page_source
            res = self.parseDetail(html,gcode)
            print ("done parsing: "+gcode)
            return(res)
        except TimeoutException:
            msg = "Timeout Error"
            print(msg+gcode)
            self.logError(msg,gcode)
        except Exception:
            msg  = "Parsing Error "
            print (msg+gcode)
            self.logError(msg,gcode)

    def parseDatePrice(self,dl,output,soup):
        releaseDate = dl.find('dd').getText()
        # remove some early/late in the date field
        if len(releaseDate)>8:
            releaseDate = releaseDate[-8:]
        if len(releaseDate)>0 and '-' in releaseDate:
            output['ReleaseDate'] = datetime.strptime(releaseDate,'%b-%Y')
        price = dl.findAll('dd')[1].getText()
        if price == 'Open Price':
            price = soup.find(class_='item-detail__price_selling-price').getText()
            # print(price)

        output['ListPrice']=int(price.strip(' JPY').replace(',',''))

    @staticmethod
    def parseLinkField(dl,output,key):
        text = dl.find('dd').find('span').getText()
        text = text.strip()
        output[key]=text

    @staticmethod
    def parseSculptor(dl,output):
        sculptor = dl.find('dd')
        # print(sculptor)
        if 'span' in sculptor:
            sculptor.find('span').decompose()
        output['Sculptor'] = sculptor.getText()

    @staticmethod
    def parseSpecs(dl,output):
        specs = [ x for x in dl.find('dd').contents if getattr(x, 'name', None) != 'br' ]
        # print(specs)
        for s in specs:
            for key in ['Scale','Size','Material']:
                if key in s:
                    output[key] = s.replace(key+': ','')
                    break

    def parseField(self,dl,output,html):
        dt = dl.find('dt')
        # print(dl)
        if dt == None:
            return
        text = dt.getText()
        if 'Release Date' in text:
            self.parseDatePrice(dl,output,html)
            return

        if 'Specifications' in text:
            Figure.parseSpecs(dl,output)
            return

        if 'Sculptor' in text:
            Figure.parseSculptor(dl,output)
            return

        for key in ['Brand','Series Title','Character Name']:
            if key in text:
                Figure.parseLinkField(dl,output,key)
                break

    def parseDetail(self,html,gcode):
        soup = BeautifulSoup(html, 'lxml')
        about = soup.find(class_='item-about')
        details = about.findAll('dl')
        output = {}
        output['gcode']=gcode
        for dl in details:
            self.parseField(dl,output,soup)
        return output
