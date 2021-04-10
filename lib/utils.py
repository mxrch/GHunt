import imagehash
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

from lib.os_detect import Os

from pathlib import Path
import shutil
import subprocess, os
from os.path import isfile
import json
import re
from pprint import pprint


class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        print(text, end='\r')
    def clear(self):
    	print(" " * self.max_len, end="\r")

def within_docker():
    return Path('/.dockerenv').is_file()

def is_email_google_account(httpx_client, auth, cookies, email, hangouts_token):
    host = "https://people-pa.clients6.google.com"
    url = "/v2/people/lookup?key={}".format(hangouts_token)
    body = """id={}&type=EMAIL&matchType=EXACT&extensionSet.extensionNames=HANGOUTS_ADDITIONAL_DATA&extensionSet.extensionNames=HANGOUTS_OFF_NETWORK_GAIA_LOOKUP&extensionSet.extensionNames=HANGOUTS_PHONE_DATA&coreIdParams.useRealtimeNotificationExpandedAcls=true&requestMask.includeField.paths=person.email&requestMask.includeField.paths=person.gender&requestMask.includeField.paths=person.in_app_reachability&requestMask.includeField.paths=person.metadata&requestMask.includeField.paths=person.name&requestMask.includeField.paths=person.phone&requestMask.includeField.paths=person.photo&requestMask.includeField.paths=person.read_only_profile_info&requestMask.includeContainer=AFFINITY&requestMask.includeContainer=PROFILE&requestMask.includeContainer=DOMAIN_PROFILE&requestMask.includeContainer=ACCOUNT&requestMask.includeContainer=EXTERNAL_ACCOUNT&requestMask.includeContainer=CIRCLE&requestMask.includeContainer=DOMAIN_CONTACT&requestMask.includeContainer=DEVICE_CONTACT&requestMask.includeContainer=GOOGLE_GROUP&requestMask.includeContainer=CONTACT"""

    headers = {
        "X-HTTP-Method-Override": "GET",
        "Authorization": auth,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://hangouts.google.com"
    }

    req = httpx_client.post(host + url, data=body.format(email), headers=headers, cookies=cookies)
    data = json.loads(req.text)
    #pprint(data); exit()
    if not "matches" in data:
        exit("[-] This email address does not belong to a Google Account.")

    return data

def get_account_name(httpx_client, gaiaID, internal_auth, internal_token, cookies, config):
    # Bypass method
    req_headers = {
        "Origin": "https://drive.google.com",
        "authorization": internal_auth,
        "Host": "people-pa.clients6.google.com"
    }
    headers = {**config.headers, **req_headers}

    url = f"https://people-pa.clients6.google.com/v2/people?person_id={gaiaID}&request_mask.include_container=PROFILE&request_mask.include_container=DOMAIN_PROFILE&request_mask.include_field.paths=person.metadata.best_display_name&core_id_params.enable_private_names=true&key={internal_token}"
    req = httpx_client.get(url, headers=headers)
    data = json.loads(req.text)

    try:
        name = data["personResponse"][0]["person"]["metadata"]["bestDisplayName"]["displayName"]
    except KeyError:
        pass # We fallback on the classic method
    else:
        return name

    # Classic method, but requires the target to have at least 1 GMaps contribution
    req = httpx_client.get(f"https://www.google.com/maps/contrib/{gaiaID}")
    gmaps_source = req.text
    match = re.search(r'<meta content="Contributions by (.*?)" itemprop="name">', gmaps_source)
    if not match:
        return None
    return match[1]

def image_hash(img):
    hash = str(imagehash.average_hash(img))
    return hash

def detect_default_profile_pic(hash):
    if hash == 'ffffc3c3e7c38181':
        return True
    return False

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
    drivers = [str(x.absolute()) for x in Path('.').rglob('chromedriver*') if not "chromedriver_autoinstaller" in str(x)]
    if drivers:
        return drivers[0]
    else:
        driver = shutil.which("chromedriver")
        if driver:
            return driver
        tmprinter.out("I can't find the chromedriver, so I'm downloading and installing it for you...")
        path = chromedriver_autoinstaller.install(cwd=True)
        tmprinter.out("")
        drivers = [str(x.absolute()) for x in Path('.').rglob('chromedriver*') if x.name.lower() == "chromedriver" or x.name.lower() == "chromedriver.exe"]
        if drivers:
            return path
        else:
            exit(f"I can't find the chromedriver.\nI installed it in \"{path}\" but it must be in the GHunt directory or PATH, you should move it here.")


def get_chrome_options_args(is_headless):
    chrome_options = Options()
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--no-sandbox")
    if is_headless:
        chrome_options.add_argument("--headless")
    if (Os().wsl or Os().windows) and is_headless:
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    return chrome_options
