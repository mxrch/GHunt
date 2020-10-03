import httpx
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from config import cfg
from lib.utils import *
import json
from os.path import isfile

cookies = ""
auth = ""
keys = ""
already_exists = False
if isfile(cfg['data_path']):
    try:
        with open(cfg['data_path'], 'r') as f:
            out = json.loads(f.read())
            auth = out["auth"]
            hangouts_token = out["keys"]
            cookies = out["cookies"]
            print("[+] Detected stored cookies, checking it")
            already_exists = True
    except Exception:
        print("[-] Stored cookies are corrupted.")
        choice = input("Do you want to generate new cookies ? (Y/n) ").lower()
        if choice != "y":
            exit()

if not already_exists:
    cookies = {"__Secure-3PSID": "", "APISID": "", "SAPISID": "", "HSID": "", "CONSENT": "YES+FR.fr+V10+BX"}
    for name in cookies.keys():
        if not cookies[name]:
            cookies[name] = input(f"{name} => ").strip()

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'}
req = httpx.get("https://docs.google.com/document/u/0/?usp=direct_url", cookies=cookies, headers=headers, allow_redirects=False)
exitflag = False
if req.status_code != 200:
    exitflag = True
if not exitflag:
    req2 = httpx.get("https://hangouts.google.com", cookies=cookies, headers=headers, allow_redirects=False)
    if "myaccount.google.com" not in req2.text:
        exitflag = True
if exitflag:
    exit("\n[-] Seems like the cookies are invalid, try regenerating them.")
print("\n[+] The cookies seems valid ! Generating the Google Docs and Hangouts token...\n")

if already_exists:
    choice = input("Do you want to generate new Google Docs and Hangouts tokens ? (Y/n) ").lower()
    if choice != "y":
        exit()

# Google Docs
source = req.text
trigger = '\"token\":\"'
if trigger not in source:
	exit("[-] I can't find the Google Docs token in the source code...\n")
else:
	gdoc_token = source.split(trigger)[1][:100].split('"')[0]
	print("Google Docs Token => {}".format(gdoc_token))

# Hangouts
tmprinter = TMPrinter()
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--headless")
options = {
    'connection_timeout': None  # Never timeout, otherwise it floods errors
}

tmprinter.out("Starting browser...")

driverpath = get_driverpath()
driver = webdriver.Chrome(executable_path=driverpath, seleniumwire_options=options, options=chrome_options)

tmprinter.out("Setting cookies...")
driver.get("https://hangouts.google.com/robots.txt")
for k,v in cookies.items():
    driver.add_cookie({'name': k, 'value': v})

tmprinter.out("Fetching Hangouts homepage...")
driver.get("https://hangouts.google.com")
tmprinter.out("Waiting for the /v2/people/me/blockedPeople request, it can takes a few minutes...")
req = driver.wait_for_request('/v2/people/me/blockedPeople', timeout=120)
tmprinter.out("Request found !")
#driver.get("about:blank")
driver.close()

auth = req.headers["Authorization"]
tmprinter.out("")
print("Authorization Token => {}".format(auth))
hangouts_token = req.url.split("key=")[1]
print("Hangouts Token => {}".format(hangouts_token))

output = {"auth": auth, "keys": {"gdoc": gdoc_token, "hangouts": hangouts_token}, "cookies": cookies}
with open(cfg['data_path'], 'w') as f:
	f.write(json.dumps(output))