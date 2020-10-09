import re
from io import BytesIO

from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from lib.metadata import ExifEater
from lib.utils import *


def get_source(gaiaID, client, cookies, cfg):
    baseurl = f"https://get.google.com/albumarchive/{gaiaID}/albums/profile-photos?hl=en"
    req = client.get(baseurl)
    if req.status_code != 200:
        return False

    class element_has_substring_or_substring(object):
        """An expectation for checking that an element has a particular css class.

        locator - used to find the element
        returns the WebElement once it has the particular css class
        """

        def __init__(self, locator, substring1, substring2):
            self.locator = locator
            self.substring1 = substring1
            self.substring2 = substring2

        def __call__(self, driver):
            element = driver.find_element(*self.locator)  # Finding the referenced element
            if self.substring1 in element.text:
                return self.substring1
            elif self.substring2 in element.text:
                return self.substring2
            else:
                return False

    tmprinter = TMPrinter()
    chrome_options = get_chrome_options_args(cfg)
    options = {
        'connection_timeout': None  # Never timeout, otherwise it floods errors
    }

    tmprinter.out("Starting browser...")

    driverpath = get_driverpath()
    driver = webdriver.Chrome(executable_path=driverpath, seleniumwire_options=options, options=chrome_options)
    wait = WebDriverWait(driver, 30)

    tmprinter.out("Setting cookies...")
    driver.get("https://get.google.com/robots.txt")
    for k, v in cookies.items():
        driver.add_cookie({'name': k, 'value': v})

    tmprinter.out('Fetching Google Photos "Profile photos" album...')
    driver.get(baseurl)

    tmprinter.out('Fetching the Google Photos albums overview...')
    buttons = driver.find_elements(By.XPATH, "//button")
    for button in buttons:
        text = button.get_attribute('jsaction')
        if text and 'touchcancel' in text:
            button.click()
            break
    else:
        tmprinter.out("")
        print("Can't get the back button..")
        driver.close()
        return False

    wait.until(EC.text_to_be_present_in_element((By.XPATH, "//body"), "Album Archive"))
    tmprinter.out("Got the albums overview !")
    no_photos_trigger = "reached the end"
    photos_trigger = " item"
    body = driver.find_element_by_xpath("//body").text
    if no_photos_trigger in body:
        stats = "notfound"
    elif photos_trigger in body:
        stats = "found"
    else:
        return False
    tmprinter.out("")
    source = driver.page_source
    driver.close()

    return {"stats": stats, "source": source}


def gpics(gaiaID, client, cookies, cfg):
    baseurl = "https://get.google.com/albumarchive/"

    print(f"\nGoogle Photos : {baseurl + gaiaID + '/albums/profile-photos'}")
    out = get_source(gaiaID, client, cookies, cfg)
    if not out:
        print("=> Couldn't fetch the public photos.")
        return False
    if out["stats"] == "notfound":
        print("=> No album")
        return False

    # open('debug.html', 'w').write(repr(out["source"]))
    results = re.compile(cfg["regexs"]["albums"]).findall(out["source"])

    list_albums_length = len(results)

    if results:
        exifeater = ExifEater()
        pics = []
        for album in results:
            album_name = album[1]
            album_link = baseurl + gaiaID + "/album/" + album[0]
            album_length = int(album[2])

            if album_length >= 1:
                req = client.get(album_link)
                source = req.text.replace('\n', '')
                results_pics = re.compile(cfg["regexs"]["photos"]).findall(source)
                for pic in results_pics:
                    pic_name = pic[1]
                    pic_link = pic[0]
                    pics.append(pic_link)

        print(f"=> {list_albums_length} albums{', ' + str(len(pics)) + ' photos' if list_albums_length else ''}")
        for pic in pics:
            req = client.get(pic)
            img = Image.open(BytesIO(req.content))
            exifeater.feed(img)

        print("\nSearching metadata...")
        exifeater.output()
    else:
        print("=> No album")
