import imagehash
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

from lib.os_detect import Os

from pathlib import Path
import shutil


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
    not_country = False
    not_town = False
    town = "?"
    country = "?"
    if "city" in location:
        town = location["city"]
    elif "village" in location:
        town = location["village"]
    elif "town" in location:
        town = location["town"]
    elif "municipality" in location:
        town = location["municipality"]
    else:
        not_town = True
    if not "country" in location:
        not_country = True
        location["country"] = country
    if not_country and not_town:
        return False
    location["town"] = town
    return location


def get_driverpath():
    tmprinter = TMPrinter()
    drivers = [str(x.absolute()) for x in Path('.').rglob('chromedriver*')]
    if not drivers:
        driver = shutil.which("chromedriver")
        if driver is not None:
            drivers = [driver]
    if drivers:
        return drivers[0]
    else:
        tmprinter.out("I can't find the chromedriver, so I'm downloading and installing it for you...")
        path = chromedriver_autoinstaller.install(cwd=True)
        tmprinter.out("")
        drivers = [str(x.absolute()) for x in Path('.').rglob('chromedriver*') if x.name.lower() == "chromedriver" or x.name.lower() == "chromedriver.exe"]
        if drivers:
            return path
        else:
            exit(f"I can't find the chromedriver.\nI installed it in \"{path}\" but it must be in the GHunt directory or PATH, you should move it here.")


def get_chrome_options_args(cfg):
    chrome_options = Options()
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--no-sandbox")
    if cfg["headless"]:
        chrome_options.add_argument("--headless")
    if Os().wsl or Os().windows:
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    return chrome_options
