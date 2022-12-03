from typing import *

import httpx
from pathlib import Path

from ghunt import globals as gb
from ghunt.helpers.utils import *
from ghunt.helpers.auth import *
from ghunt.objects.base import GHuntCreds


async def check_and_login(as_client: httpx.AsyncClient, clean: bool=False) -> None:
    """Check the users credentials validity, and generate new ones."""

    ghunt_creds = GHuntCreds()

    if clean:
        creds_path = Path(ghunt_creds.creds_path)
        if creds_path.is_file():
            creds_path.unlink()
            print(f"[+] Credentials file at {creds_path} deleted !")
        else:
            print(f"Credentials file at {creds_path} doesn't exists, no need to delete.")
        exit()

    if not as_client:
        as_client = get_httpx_client()

    ghunt_creds.load_creds()

    wanted_cookies = {"SID": "", "SSID": "", "APISID": "", "SAPISID": "", "HSID": "", "LSID": "", "__Secure-3PSID": ""}
    default_cookies = {"CONSENT": gb.config.default_consent_cookie, "PREF": gb.config.default_pref_cookie}

    osids = ["cloudconsole", "cl"] # OSIDs to generate

    new_cookies_entered = False
    if not ghunt_creds.are_creds_loaded():
        cookies, oauth_token = await getting_cookies_dialog(wanted_cookies)
        cookies = {**cookies, **default_cookies}
        new_cookies_entered = True
    else:
        # in case user wants to enter new cookies (example: for new account)
        are_cookies_valid = check_cookies(ghunt_creds.cookies)
        if are_cookies_valid:
            print("\n[+] The cookies seems valid !")
            are_osids_valid = check_osids(ghunt_creds.cookies, ghunt_creds.osids)
            if are_osids_valid:
                print("[+] The OSIDs seems valid !")
            else:
                print("[-] Seems like the OSIDs are invalid.")
        else:
            print("[-] Seems like the cookies are invalid.")
        is_master_token_valid = await check_master_token(as_client, ghunt_creds.android.master_token)
        if is_master_token_valid:
            print("[+] The master token seems valid !")
        else:
            print("[-] Seems like the master token is invalid.")
        new_gen_inp = input("\nDo you want to input new cookies ? (Y/n) ").lower()
        if new_gen_inp == "y":
            cookies, oauth_token = await getting_cookies_dialog(wanted_cookies)
            new_cookies_entered = True
        elif not are_cookies_valid:
            await exit("Please put valid cookies. Exiting...")

    # Validate cookies
    if new_cookies_entered or not ghunt_creds.are_creds_loaded():
        are_cookies_valid = check_cookies(cookies)
        if are_cookies_valid:
            print("\n[+] The cookies seems valid !")
        else:
            await exit("\n[-] Seems like the cookies are invalid, try regenerating them.")
    
    if not new_cookies_entered:
        await exit()

    print(f"\n[+] Got OAuth2 token => {oauth_token}")
    master_token, services, owner_email, owner_name = await android_master_auth(as_client, oauth_token)

    print("\n[Connected account]")
    print(f"Name : {owner_name}")
    print(f"Email : {owner_email}")
    gb.rc.print("\n🔑 [underline]A master token has been generated for your account and saved in the credentials file[/underline], please keep it safe as if it were your password, because it gives access to a lot of Google services, and with that, your personal information.", style="bold")
    print(f"Master token services access : {', '.join(services)}")

    # Feed the GHuntCreds object
    ghunt_creds.cookies = cookies
    ghunt_creds.android.master_token = master_token

    print("Generating OSIDs ...")
    ghunt_creds.osids = await gen_osids(cookies, osids)

    ghunt_creds.save_creds()

    await as_client.aclose()
