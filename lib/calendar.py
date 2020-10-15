import json
import httpx
#from bs4 import BeautifulSoup
from scrapy.selector import Selector

from lib.utils import TMPrinter 
from lib.utils import get_chrome_options_args
from lib.utils import get_driverpath

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException

# this method returns a dictionary with information of events, if there are no events then it returns None
def fetch_calendar(email, cookies, headers, headless_wanted):
    
    event_info_dictionary = {}

    try:
        # -- Getting connection to calendar's page ------------
        calendar_source = connect_to_calendar(headers, headless_wanted, cookies, email)

        if calendar_source == None:
            return None
        # adding event titles into dictionary
        # --------------------------------------- FOR BS4 ----------------------------------------------------------
        # for date_section in bs_source_code.find_all("div", attrs={"class" : "day"}): # iterating through all days
        #
        #    for event in date_section.find_all("div", attrs={"class":"event"}):
        #        ev_title         = event.find("div", attrs={"class": "event-summary"}).div.find("span", attrs={"class":"event-title"}).text
        #        ev_date_and_time = event.find("div", attrs={"class": "event-summary"}).span["title"]
        #
        #        event_info_dictionary[ev_title] = ev_date_and_time
        # ----------------------------------------------------------------------------------------------------------

        # ----------------------------------------- SCRAPY ---------------------------------------------------------
        for i in Selector(text=calendar_source).css(".day"):
            for event in i.css(".event"):
                ev_date_and_time = event.css("[class=\"event-time\"]::attr(title)").get()
                ev_title         = event.css(".event-title::text").get()
                #print(ev_title + " " + ev_date_and_time)
                event_info_dictionary[ev_title] = ev_date_and_time
        # ----------------------------------------------------------------------------------------------------------
        
    except TimeoutException:
        # if we are not able to fetch date-label, it means there are some problems in calendar
        return None
    
    return event_info_dictionary

def connect_to_calendar(headers, headless, cookies, email):
    
    # I am sorry for starting browser, but I was not able to manage this without chromedriver
    # but it's better than nothing, hun? Isn't it?
    
    delay = 3
    url_endpoint = "https://calendar.google.com/calendar/u/0/embed?src=" + email + "&mode=AGENDA"
    print("\nGoogle Calendar : " + url_endpoint)

    tmprinter = TMPrinter()
    # ------- Setting chrome settings ----------
    chrome_options = get_chrome_options_args(headless)
    options = {
        'connection_timeout': None  # Never timeout, otherwise it floods errors
    }
    # ------------------------------------------

    tmprinter.out("Starting browser...")

    driverpath = get_driverpath()
    driver = webdriver.Chrome(executable_path=driverpath, seleniumwire_options=options, options=chrome_options)
    driver.header_overrides = headers
    wait = WebDriverWait(driver, 30)

    tmprinter.out("Setting cookies...")

    # set cookies
    driver.get("https://get.google.com/robots.txt")
    for k, v in cookies.items():
        driver.add_cookie({'name': k, 'value': v})
  

    tmprinter.out("Fetching Calendar...")

    driver.get(url_endpoint)
    
    tmprinter.out("")

    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'date-label')))
    source_code = driver.page_source
    driver.close()
    
    return source_code
