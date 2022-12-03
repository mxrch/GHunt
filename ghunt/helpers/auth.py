import json
import base64
from typing import *
from copy import deepcopy

import httpx
from bs4 import BeautifulSoup as bs

from ghunt import globals as gb
from ghunt.errors import *
from ghunt.helpers.utils import *
from ghunt.helpers import listener
from ghunt.helpers.knowledge import get_domain_of_service, get_package_sig
from ghunt.helpers.auth import *


async def android_master_auth(as_client: httpx.AsyncClient, oauth_token: str) -> Tuple[str, List[str], str, str]:
    """
        Takes an oauth_token to perform an android authentication
        to get the master token and other informations.

        Returns the master token, connected services, account email and account full name.
    """
    data = {
        "Token": oauth_token,
        "service": "ac2dm",
        "get_accountid": 1,
        "ACCESS_TOKEN": 1,
        "add_account": 1,
        "callerSig": "38918a453d07199354f8b19af05ec6562ced5788"
    }

    req = await as_client.post("https://android.googleapis.com/auth", data=data)
    resp = parse_oauth_flow_response(req.text)
    for keyword in ["Token", "Email", "services", "firstName", "lastName"]:
        if keyword not in resp:
            raise GHuntAndroidMasterAuthError(f'Expected "{keyword}" in the response of the Android Master Authentication.\nThe oauth_token may be expired.')
    return resp["Token"], resp["services"].split(","), resp["Email"], f'{resp["firstName"]} {resp["lastName"]}'

async def android_oauth_app(as_client: httpx.AsyncClient, master_token: str,
                package_name: str, scopes: List[str]) -> Tuple[str, List[str], int]:
    """
        Uses the master token to ask for an authorization token,
        with specific scopes and app package name.

        Returns the authorization token, granted scopes and expiry UTC timestamp.
    """
    client_sig = get_package_sig(package_name)

    data = {
        "app": package_name,
        "service": f"oauth2:{' '.join(scopes)}",
        "client_sig": client_sig,
        "Token": master_token
    }

    req = await as_client.post("https://android.googleapis.com/auth", data=data)
    resp = parse_oauth_flow_response(req.text)
    for keyword in ["Expiry", "grantedScopes", "Auth"]:
        if keyword not in resp:
            raise GHuntAndroidAppOAuth2Error(f'Expected "{keyword}" in the response of the Android App OAuth2 Authentication.\nThe master token may be revoked.')
    return resp["Auth"], resp["grantedScopes"].split(" "), int(resp["Expiry"])

async def gen_osids(cookies: Dict[str, str], osids: List[str]) -> Dict[str, str]:
    """
        Generate OSIDs of given services names,
        contained in the "osids" dict argument.
    """
    generated_osids = {}
    for service in osids:
        sample_cookies = deepcopy(cookies)
        domain = get_domain_of_service(service)
        req = httpx.get(f"https://accounts.google.com/ServiceLogin?service={service}&osid=1&continue=https://{domain}/&followup=https://{domain}/&authuser=0",
                        cookies=cookies, headers=gb.config.headers)

        for cookie in ["__Host-GAPS", "SIDCC", "__Secure-3PSIDCC"]:
           sample_cookies[cookie] = req.cookies[cookie]

        body = bs(req.text, 'html.parser')
        
        params = {x.attrs["name"]:x.attrs["value"] for x in body.find_all("input", {"type":"hidden"})}

        headers = {**gb.config.headers, **{"Content-Type": "application/x-www-form-urlencoded"}}
        req = httpx.post(f"https://{domain}/accounts/SetOSID", cookies=cookies, data=params, headers=headers)

        if not "OSID" in req.cookies:
            raise GHuntOSIDAuthError("[-] No OSID header detected, exiting...")

        generated_osids[service] = req.cookies["OSID"]

    return generated_osids

def check_cookies(cookies: Dict[str, str]) -> bool:
    """Checks the validity of given cookies."""
    req = httpx.get("https://docs.google.com", cookies=cookies, headers=gb.config.headers)
    if req.status_code != 307:
        return False

    set_cookies = extract_set_cookies(req)
    if any([cookie in set_cookies for cookie in cookies]):
        return False

    return True

def check_osids(cookies: Dict[str, str], osids: Dict[str, str]) -> bool:
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

async def check_master_token(as_client: httpx.AsyncClient, master_token: str) -> str:
    """Checks the validity of the android master token."""
    try:
        await android_oauth_app(as_client, master_token, "com.google.android.play.games", ["https://www.googleapis.com/auth/games.firstparty"])
    except GHuntAndroidAppOAuth2Error:
        return False
    return True

async def getting_cookies_dialog(cookies: Dict[str, str]) -> Tuple[Dict[str, str], str] :
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
    if choice in ["1", "2"]:
        if choice == "1":
            received_data = listener.run()
        elif choice == "2":
            received_data = input("Paste the encoded cookies here => ")
        data = json.loads(base64.b64decode(received_data))
        cookies = data["cookies"]
        oauth_token = data["oauth_token"]

    elif choice == "3":
        for name in cookies.keys():
            cookies[name] = input(f"{name} => ").strip().strip('"')
        oauth_token = input(f"oauth_token").strip().strip('"')

    else:
        exit("Please choose a valid choice. Exiting...")

    return cookies, oauth_token