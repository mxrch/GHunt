import json
from os.path import isfile
from ssl import SSLError

import httpx
from seleniumwire import webdriver

import config
from lib.utils import *


def get_saved_cookies():
    ''' returns cookie cache if exists '''
    if isfile(config.data_path):
        try:
            with open(config.data_path, 'r') as f:
                out = json.loads(f.read())
                cookies = out["cookies"]
                print("[+] Detected stored cookies, checking it")
                return cookies
        except Exception:
            print("[-] Stored cookies are corrupted")
            return False
    print("[-] No stored cookies found")
    return False


def get_authorization_source(cookies):
    ''' returns html source of hangouts page if user authorized '''
    req = httpx.get("https://docs.google.com/document/u/0/?usp=direct_url",
                    cookies=cookies, headers=config.headers, allow_redirects=False)

    if req.status_code == 200:
        req2 = httpx.get("https://hangouts.google.com", cookies=cookies,
                         headers=config.headers, allow_redirects=False)
        if "myaccount.google.com" in req2.text:
            return req.text
    return None


def save_tokens(auth, gdoc_token, hangouts_token, cookies):
    ''' save tokens to file '''
    output = {
        "auth": auth,
        "keys": {"gdoc": gdoc_token, "hangouts": hangouts_token},
        "cookies": cookies
    }
    with open(config.data_path, 'w') as f:
        f.write(json.dumps(output))


def get_hangouts_tokens(cookies, driverpath):
    ''' gets auth and hangout token '''
    tmprinter = TMPrinter()
    chrome_options = get_chrome_options_args(config.headless)
    options = {
        'connection_timeout': None  # Never timeout, otherwise it floods errors
    }

    tmprinter.out("Starting browser...")
    driver = webdriver.Chrome(
        executable_path=driverpath, seleniumwire_options=options,
        options=chrome_options
    )
    driver.header_overrides = config.headers

    tmprinter.out("Setting cookies...")
    driver.get("https://hangouts.google.com/robots.txt")
    for k, v in cookies.items():
        driver.add_cookie({'name': k, 'value': v})

    tmprinter.out("Fetching Hangouts homepage...")
    driver.get("https://hangouts.google.com")

    tmprinter.out("Waiting for the /v2/people/me/blockedPeople request, it "
                  "can takes a few minutes...")
    req = driver.wait_for_request('/v2/people/me/blockedPeople', timeout=120)
    tmprinter.out("Request found !")
    driver.close()
    tmprinter.out("")

    auth_token = req.headers["Authorization"]
    hangouts_token = req.url.split("key=")[1]

    return (auth_token, hangouts_token)


if __name__ == '__main__':

    driverpath = get_driverpath()
    cookies = get_saved_cookies()

    ask = True
    if not cookies:
        ask = False
        print("\nEnter these browser cookies found at accounts.google.com :")
        cookies = {"__Secure-3PSID": "", "APISID": "", "SAPISID": "",
                   "HSID": "", "CONSENT": "YES+FR.fr+V10+BX"}
        for name in cookies.keys():
            if not cookies[name]:
                cookies[name] = input(f"{name} => ").strip()

    # validate cookies
    html = get_authorization_source(cookies)
    if html:
        print("\n[+] The cookies seems valid! Generating the Google Docs and "
            "Hangouts token...\n")
    else:
        exit("\n[-] Seems like the cookies are invalid, try regenerating them")

    if ask:
        choice = input("Do you want to generate new Google Docs "
                        "and Hangouts tokens ? (Y/n) ").lower()
        if choice != "y":
            exit()

    # get Google Docs token
    trigger = '\"token\":\"'
    if trigger not in html:
        exit("[-] I can't find the Google Docs token in the source code...\n")
    else:
        gdoc_token = html.split(trigger)[1][:100].split('"')[0]
        print("Google Docs Token => {}".format(gdoc_token))

    # get Google Hangouts token
    auth_token, hangouts_token = get_hangouts_tokens(cookies, driverpath)
    print("Authorization Token => {}".format(auth_token))
    print("Hangouts Token => {}".format(hangouts_token))

    save_tokens(auth_token, gdoc_token, hangouts_token, cookies)
