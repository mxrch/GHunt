#!/usr/bin/env python3

import json
from time import time
from pathlib import Path
import base64
from copy import deepcopy
import os
from typing import *

import httpx
from bs4 import BeautifulSoup as bs

from ghunt import globals as gb
from ghunt.lib.utils import *
from ghunt.lib import listener
from ghunt.lib.knowledge import get_domain_of_service
from ghunt.objects.base import GHuntCreds


def save_cookies_and_keys(ghunt_creds: GHuntCreds, creds_path: str):
    """Save cookies, OSIDs, tokens and keys to the specified file."""
    data = {
        "cookies": ghunt_creds.cookies,
        "osids": ghunt_creds.osids,
        "tokens": ghunt_creds.tokens,
        "keys": ghunt_creds.keys
    }
    with open(creds_path, "w") as f:
        f.write(json.dumps(data, indent=4))

    print(f"\n[+] Creds have been saved in {creds_path} !")

def gen_osids(cookies: Dict[str, str], osids: Dict[str, str]) -> Dict[str, str]:
    """
        Generate OSIDs of given services names,
        contained in the "osids" dict argument.
    """
    for service in osids:
        domain = get_domain_of_service(service)
        req = httpx.get(f"https://accounts.google.com/ServiceLogin?service={service}&osid=1&continue=https://{domain}/&followup=https://{domain}/&authuser=0",
                        cookies=cookies, headers=gb.config.headers)

        body = bs(req.text, 'html.parser')
        
        params = {x.attrs["name"]:x.attrs["value"] for x in body.find_all("input", {"type":"hidden"})}

        headers = {**gb.config.headers, **{"Content-Type": "application/x-www-form-urlencoded"}}
        req = httpx.post(f"https://{domain}/accounts/SetOSID", cookies=cookies, data=params, headers=headers)

        osid_header = [x for x in req.headers["set-cookie"].split(", ") if x.startswith("OSID")]
        if not osid_header:
            exit("[-] No OSID header detected, exiting...")

        osids[service] = osid_header[0].split("OSID=")[1].split(";")[0]

    return osids

def get_gdrive_api_key(cookies: Dict[str, str]) -> str:
    """Extracts the GDrive API Key."""
    req = httpx.get("https://drive.google.com/drive/my-drive", cookies=cookies)
    gdrive_api_key = req.text.split("appsitemsuggest-pa")[1].split(",")[3].strip('"')
    
    return gdrive_api_key

def get_pantheon_api_key(cookies: Dict[str, str]):
    """Extracts the Pantheon API Key."""
    req = httpx.get("https://console.cloud.google.com",
                    cookies=cookies, headers=gb.config.headers)

    if req.status_code == 200 and "pantheon_apiKey" in req.text:
        pantheon_api_key = req.text.split('pantheon_apiKey\\x22:')[1].split(",")[0].strip('\\x22')
        return pantheon_api_key

    exit("[-] I can't find the Pantheon API Key...")

def get_gdocs_token(cookies: Dict[str, str]) -> str:
    """Extracts the Google Docs token."""
    req = httpx.get("https://docs.google.com/document/u/0/", cookies=cookies, headers=gb.config.headers)
    trigger = '\"token\":\"'
    if trigger not in req.text:
        exit("[-] I can't find the Google Docs token in the source code...\n")
    else:
        gdoc_token = req.text.split(trigger)[1][:100].split('"')[0]
        return gdoc_token

def check_cookies(cookies) -> bool:
    """Checks the validity of given cookies."""
    req = httpx.get("https://docs.google.com", cookies=cookies, headers=gb.config.headers)
    if req.status_code != 307:
        return False

    set_cookies = extract_set_cookies(req)
    if any([cookie in set_cookies for cookie in cookies]):
        return False

    return True

def check_osids(cookies, osids) -> bool:
    """Checks the validity of given OSIDs."""
    for service in osids:
        domain = get_domain_of_service(service)
        cookies_with_osid = inject_osid(cookies, osids, service)
        wanted = ["authuser", "continue", "osidt", "ifkv"]
        req = httpx.get(f"https://accounts.google.com/ServiceLogin?service={service}&osid=1&continue=https://{domain}/&followup=https://{domain}/&authuser=0",
                        cookies=cookies_with_osid, headers=gb.config.headers)

        body = bs(req.text, 'html.parser')
        params = [x.attrs["name"] for x in body.find_all("input", {"type":"hidden"})]
        if not all([param in wanted for param in params]):
            return False

    return True

def getting_cookies_dialog(cookies: Dict[str, str]) -> Dict[str, str] :
    """
        Launch the dialog that asks the user
        how he want to generate its credentials.
    """
    choices = ("You can facilitate configuring GHunt by using the GHunt Companion extension on Firefox, Chrome, Edge and Opera here :\n"
                "=> https://github.com/mxrch/ghunt_companion\n\n"
                "[1] (Companion) Put GHunt on listening mode (currently not compatible with docker)\n"
                "[2] (Companion) Paste base64-encoded cookies\n"
                "[3] Enter manually all cookies\n\n"
                "Choice => ")

    choice = input(choices)
    if choice not in ["1","2","3"]:
        exit("Please choose a valid choice. Exiting...")

    if choice == "1":
        received_cookies = listener.run()
        cookies = json.loads(base64.b64decode(received_cookies))

    elif choice == "2":
        received_cookies = input("Paste the cookies here => ")
        cookies = json.loads(base64.b64decode(received_cookies))

    elif choice == "3":
        for name in cookies.keys():
            if not cookies[name]:
                cookies[name] = input(f"{name} => ").strip().strip('\"')

    return cookies

def check_and_login() -> None:
    """Check the users credentials validity, and generate new ones."""

    ghunt_creds = GHuntCreds()
    ghunt_creds.load_creds()

    cookies = {"SID": "", "SSID": "", "APISID": "", "SAPISID": "", "HSID": "", "LSID": "", "__Secure-3PSID": "", "CONSENT": gb.config.default_consent_cookie, "PREF": gb.config.default_pref_cookie}
    osids = {"cloudconsole": ""}

    new_cookies_entered = False
    if not ghunt_creds.are_creds_loaded():
        cookies = getting_cookies_dialog(cookies)
        new_cookies_entered = True
    else:
        # in case user wants to enter new cookies (example: for new account)
        valid_cookies = check_cookies(ghunt_creds.cookies)
        if valid_cookies:
            print("[+] The cookies seem valid !")
            valid_osids = check_osids(ghunt_creds.cookies, ghunt_creds.osids)
            if valid_osids:
                print("[+] The OSIDs seem valid !")
            else:
                print("[-] Seems like the OSIDs are invalid.")
        else:
            print("[-] Seems like the cookies are invalid.")
        new_gen_inp = input("\nDo you want to input new cookies ? (Y/n) ").lower()
        if new_gen_inp == "y":
            cookies = getting_cookies_dialog(cookies)
            new_cookies_entered = True
        elif not valid_cookies:
            exit("Please put valid cookies. Exiting...")


    # Validate cookies
    if new_cookies_entered or not ghunt_creds.are_creds_loaded():
        valid_cookies = check_cookies(cookies)
        if valid_cookies:
            print("\n[+] The cookies seems valid !")
        else:
            exit("\n[-] Seems like the cookies are invalid, try regenerating them.")
    
    if not new_cookies_entered:
        cookies = ghunt_creds.cookies
        choice = input("Do you want to generate new tokens ? (Y/n) ").lower()
        if choice != "y":
            exit()

    # Feed the GHuntCreds object
    ghunt_creds.cookies = cookies

    # Start the extraction process
    ghunt_creds.tokens["gdocs"] = get_gdocs_token(cookies)
    print(f'Google Docs Token => {ghunt_creds.tokens["gdocs"]}')

    print("Generating OSID for the Cloud Console...")
    ghunt_creds.osids = gen_osids(cookies, osids)

    cookies_with_cloudconsole_osid = inject_osid(cookies, ghunt_creds.osids, "cloudconsole")

    # Extracting Internal APIs keys
    ghunt_creds.keys["gdrive"] = get_gdrive_api_key(cookies_with_cloudconsole_osid)
    print(f'Google Drive API Key => {ghunt_creds.keys["gdrive"]}')

    ghunt_creds.keys["pantheon_key"] = get_pantheon_api_key(cookies_with_cloudconsole_osid)
    print(f'Pantheon API Key => {ghunt_creds.keys["pantheon_key"]}')

    save_cookies_and_keys(ghunt_creds, gb.config.creds_path)

if __name__ == '__main__':
    check_and_login()
