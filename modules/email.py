#!/usr/bin/env python3

import json
import sys
import os
from datetime import datetime
from io import BytesIO
from os.path import isfile
from pathlib import Path
from pprint import pprint

import httpx
from PIL import Image
from geopy.geocoders import Nominatim

import config
from lib.banner import banner
import lib.gmaps as gmaps
import lib.youtube as ytb
from lib.photos import gpics
from lib.utils import *
import lib.calendar as gcalendar


def email_hunt(email):
    banner()

    if not email:
        exit("Please give a valid email.\nExample : larry@google.com")

    if not isfile(config.data_path):
        exit("Please generate cookies and tokens first, with the check_and_gen.py script.")

    hangouts_auth = ""
    hangouts_token = ""
    internal_auth = ""
    internal_token = ""

    cookies = {}

    with open(config.data_path, 'r') as f:
        out = json.loads(f.read())
        hangouts_auth = out["hangouts_auth"]
        hangouts_token = out["keys"]["hangouts"]
        internal_auth = out["internal_auth"]
        internal_token = out["keys"]["internal"]
        cookies = out["cookies"]

    client = httpx.Client(cookies=cookies, headers=config.headers)

    data = is_email_google_account(client, hangouts_auth, cookies, email,
                                   hangouts_token)

    is_within_docker = within_docker()
    if is_within_docker:
        print("[+] Docker detected, profile pictures will not be saved.")

    geolocator = Nominatim(user_agent="nominatim")
    print(f"[+] {len(data['matches'])} account found !")

    for user in data["matches"]:
        print("\n------------------------------\n")

        gaiaID = user["personId"][0]
        email = user["lookupId"]
        infos = data["people"][gaiaID]

        # get name & profile picture
        account = get_account_data(client, gaiaID, internal_auth, internal_token, config)
        name = account["name"]
        
        if name:
            print(f"Name : {name}")
        else:
            if "name" not in infos:
                print("[-] Couldn't find name")
            else:
                for i in range(len(infos["name"])):
                    if 'displayName' in infos['name'][i].keys():
                        name = infos["name"][i]["displayName"]
                        print(f"Name : {name}")

        organizations = account["organizations"]
        if organizations:
            print(f"Organizations : {organizations}")

        locations = account["locations"]
        if locations:
            print(f"Locations : {locations}")

        # profile picture
        profile_pic_url = account.get("profile_pics") and account["profile_pics"][0].url
        if profile_pic_url:
            req = client.get(profile_pic_url)

            # TODO: make sure it's necessary now
            profile_pic_img = Image.open(BytesIO(req.content))
            profile_pic_flathash = image_hash(profile_pic_img)
            is_default_profile_pic = detect_default_profile_pic(profile_pic_flathash)

            if not is_default_profile_pic:
                print("\n[+] Custom profile picture !")
                print(f"=> {profile_pic_url}")
                if config.write_profile_pic and not is_within_docker:
                    open(Path(config.profile_pics_dir) / f'{email}.jpg', 'wb').write(req.content)
                    print("Profile picture saved !")
            else:
                print("\n[-] Default profile picture")

        # cover profile picture
        cover_pic = account.get("cover_pics") and account["cover_pics"][0]
        if cover_pic and not cover_pic.is_default:
            cover_pic_url = cover_pic.url
            req = client.get(cover_pic_url)

            print("\n[+] Custom profile cover picture !")
            print(f"=> {cover_pic_url}")
            if config.write_profile_pic and not is_within_docker:
                open(Path(config.profile_pics_dir) / f'cover_{email}.jpg', 'wb').write(req.content)
                print("Cover profile picture saved !")

        # last edit
        try:
            timestamp = int(infos["metadata"]["lastUpdateTimeMicros"][:-3])
            last_edit = datetime.utcfromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S (UTC)")
            print(f"\nLast profile edit : {last_edit}")
        except KeyError:
            last_edit = None
            print(f"\nLast profile edit : Not found")

        canonical_email = ""
        emails = update_emails(account["emails_set"], infos)
        if emails and len(list(emails)) == 1:
            if list(emails.values())[0].is_normalized(email):
                new_email = list(emails.keys())[0]
                if email != new_email:
                    canonical_email = f' (canonical email is {new_email})'
                emails = []

        print(f"\nEmail : {email}{canonical_email}\nGaia ID : {gaiaID}\n")

        if emails:
            print(f"Contact emails : {', '.join(map(str, emails.values()))}")

        phones = account["phones"]
        if phones:
            print(f"Contact phones : {phones}")

        # is bot?
        if "extendedData" in infos:
            isBot = infos["extendedData"]["hangoutsExtendedData"]["isBot"]
            if isBot:
                print("Hangouts Bot : Yes !")
            else:
                print("Hangouts Bot : No")
        else:
            print("Hangouts Bot : Unknown")

        # decide to check YouTube
        ytb_hunt = False
        try:
            services = [x["appType"].lower() if x["appType"].lower() != "babel" else "hangouts" for x in
                        infos["inAppReachability"]]
            if name and (config.ytb_hunt_always or "youtube" in services):
                ytb_hunt = True
            print("\n[+] Activated Google services :")
            print('\n'.join(["- " + x.capitalize() for x in services]))

        except KeyError:
            ytb_hunt = True
            print("\n[-] Unable to fetch connected Google services.")

        # check YouTube
        if name and ytb_hunt:
            confidence = None
            data = ytb.get_channels(client, name, config.data_path,
                                   config.gdocs_public_doc)
            if not data:
                print("\n[-] YouTube channel not found.")
            else:
                confidence, channels = ytb.get_confidence(data, name, profile_pic_flathash)
                
                if confidence:
                    print(f"\n[+] YouTube channel (confidence => {confidence}%) :")
                    for channel in channels:
                        print(f"- [{channel['name']}] {channel['profile_url']}")
                    possible_usernames = ytb.extract_usernames(channels)
                    if possible_usernames:
                        print("\n[+] Possible usernames found :")
                        for username in possible_usernames:
                            print(f"- {username}")
                else:
                    print("\n[-] YouTube channel not found.")

        # TODO: return gpics function output here
        #gpics(gaiaID, client, cookies, config.headers, config.regexs["albums"], config.regexs["photos"],
        #      config.headless)

        # reviews
        reviews = gmaps.scrape(gaiaID, client, cookies, config, config.headers, config.regexs["review_loc_by_id"], config.headless)

        if reviews:
            confidence, locations = gmaps.get_confidence(geolocator, reviews, config.gmaps_radius)
            print(f"\n[+] Probable location (confidence => {confidence}) :")

            loc_names = []
            for loc in locations:
                loc_names.append(
                    f"- {loc['avg']['town']}, {loc['avg']['country']}"
                )

            loc_names = set(loc_names)  # delete duplicates
            for loc in loc_names:
                print(loc)
        
        
       # Google Calendar
        calendar_response = gcalendar.fetch(email, client, config)
        if calendar_response:
            print("[+] Public Google Calendar found !")
            events = calendar_response["events"]
            if events:
                gcalendar.out(events)
            else:
                print("=> No recent events found.")
        else:
            print("[-] No public Google Calendar.")
        