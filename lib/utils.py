import imagehash
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from lib.os_detect import Os

from pathlib import Path
import shutil
from os.path import isfile
import json
import re
from pprint import pprint
from time import time
import hashlib


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

class Picture:
    def __init__(self, url, is_default=False):
        self.url = url
        self.is_default = is_default

class Contact:
    def __init__(self, val, is_primary=True):
        self.value = val
        self.is_secondary = not is_primary

    def is_normalized(self, val):
        return val.replace('.', '').lower() == self.value.replace('.', '').lower()

    def __str__(self):
        printable_value = self.value
        if self.is_secondary:
            printable_value += ' (secondary)'
        return printable_value

def update_emails(emails, data):
    """
        Typically canonical user email
        May not be present in the list method response
    """
    if not "email" in data:
        return emails

    for e in data["email"]:
        is_primary = e.get("signupEmailMetadata", {}).get("primary")
        email = Contact(e["value"], is_primary)

        if email.value in emails:
            if is_primary:
                emails[email.value].is_secondary = False
        else:
            emails[email.value] = email

    return emails

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
    #pprint(data)
    if "error" in data and "Request had invalid authentication credentials" in data["error"]["message"]:
        exit("[-] Cookies/Tokens seems expired, please verify them.")
    elif "error" in data:
        print("[-] Error :")
        pprint(data)
        exit()
    elif not "matches" in data:
        exit("[-] This email address does not belong to a Google Account.")

    return data

def get_account_data(httpx_client, gaiaID, internal_auth, internal_token, config):
    # Bypass method
    req_headers = {
        "Origin": "https://drive.google.com",
        "authorization": internal_auth,
        "Host": "people-pa.clients6.google.com"
    }
    headers = {**config.headers, **req_headers}

    url = f"https://people-pa.clients6.google.com/v2/people?person_id={gaiaID}&request_mask.include_container=PROFILE&request_mask.include_container=DOMAIN_PROFILE&request_mask.include_field.paths=person.metadata.best_display_name&request_mask.include_field.paths=person.photo&request_mask.include_field.paths=person.cover_photo&request_mask.include_field.paths=person.email&request_mask.include_field.paths=person.organization&request_mask.include_field.paths=person.location&request_mask.include_field.paths=person.email&requestMask.includeField.paths=person.phone&core_id_params.enable_private_names=true&requestMask.includeField.paths=person.read_only_profile_info&key={internal_token}"
    req = httpx_client.get(url, headers=headers)
    data = json.loads(req.text)
    # pprint(data)
    if "error" in data and "Request had invalid authentication credentials" in data["error"]["message"]:
        exit("[-] Cookies/Tokens seems expired, please verify them.")
    elif "error" in data:
        print("[-] Error :")
        pprint(data)
        exit()
    if data["personResponse"][0]["status"].lower() == "not_found":
        return False

    name = get_account_name(httpx_client, gaiaID, data, internal_auth, internal_token, config)

    profile_data = data["personResponse"][0]["person"]

    profile_pics = []
    for p in profile_data["photo"]:
        profile_pics.append(Picture(p["url"], p.get("isDefault", False)))

    # mostly is default
    cover_pics = []
    for p in profile_data["coverPhoto"]:
        cover_pics.append(Picture(p["imageUrl"], p["isDefault"]))

    emails = update_emails({}, profile_data)

    # absent if user didn't enter or hide them
    phones = []
    if "phone" in profile_data:
        for p in profile_data["phone"]:
            phones.append(f'{p["value"]} ({p["type"]})')

    # absent if user didn't enter or hide them
    locations = []
    if "location" in profile_data:
        for l in profile_data["location"]:
            locations.append(l["value"] if not l.get("current") else f'{l["value"]} (current)')

    # absent if user didn't enter or hide them
    organizations = []
    if "organization" in profile_data:
        organizations = (f'{o["name"]} ({o["type"]})' for o in profile_data["organization"])

    return {"name": name, "profile_pics": profile_pics, "cover_pics": cover_pics,
            "organizations": ', '.join(organizations), "locations": ', '.join(locations),
            "emails_set": emails, "phones": ', '.join(phones)}

def get_account_name(httpx_client, gaiaID, data, internal_auth, internal_token, config):
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
    flathash = imagehash.average_hash(img)
    return flathash

def detect_default_profile_pic(flathash):
    if flathash - imagehash.hex_to_flathash("000018183c3c0000", 8) < 10 :
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
    driver_path = shutil.which("chromedriver") or shutil.which("chromium.chromedriver")
    if driver_path:
        return driver_path
    if within_docker():
        chromedrivermanager_silent = ChromeDriverManager(print_first_line=False, log_level=0, path="/usr/src/app")
    else:
        chromedrivermanager_silent = ChromeDriverManager(print_first_line=False, log_level=0)
    driver = chromedrivermanager_silent.driver
    driverpath = chromedrivermanager_silent.driver_cache.find_driver(driver)
    if driverpath:
        return driverpath
    else:
        print("[Webdrivers Manager] I'm updating the chromedriver...")
        if within_docker():
            driver_path = ChromeDriverManager(path="/usr/src/app").install()
        else:
            driver_path = ChromeDriverManager().install()
        print("[Webdrivers Manager] The chromedriver has been updated !\n")
    return driver_path


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

def inject_osid(cookies, service, config):
    with open(config.data_path, 'r') as f:
        out = json.loads(f.read())

    cookies["OSID"] = out["osids"][service]
    return cookies

def gen_sapisidhash(sapisid: str, origin: str, timestamp: str = str(int(time()))) -> str:
    return f"{timestamp}_{hashlib.sha1(' '.join([timestamp, sapisid, origin]).encode()).hexdigest()}"