import imagehash
from platform import system
from os.path import isfile
from .os_detect import Os
from selenium.webdriver.chrome.options import Options

def image_hash(img):
    hash = str(imagehash.average_hash(img))
    return hash

class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        print(text, end='\r')

def sanitize_location(location):
    if "city" in location:
        town = location["city"]
    elif "village" in location:
        town = location["village"]
    elif "town" in location:
        town = location["town"]
    else:
        town = location["municipality"]
    location["town"] = town
    return location

def get_driverpath():
    if Os().wsl or Os().windows:
        driverpath = "./chromedriver.exe"
    else:
        driverpath = "./chromedriver"
    
    if isfile(driverpath):
        return driverpath
    else:
        exit("The chromedriver is missing.\nPlease put it in the GHunt directory.")

def get_wsl_chrome_options_args():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    if Os().wsl or Os().windows:
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")