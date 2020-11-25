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

if __name__ == "__main__":

    banner()
    
    # We change the current working directory to allow using GHunt from anywhere
    os.chdir(Path(__file__).parents[0])

    if len(sys.argv) <= 1:
        exit("Please put an email address.")

    if not isfile(config.data_path):
        exit("Please generate cookies and tokens first.")

    email = sys.argv[1]
    auth = ""
    hangouts_token = ""
    cookies = ""

    with open(config.data_path, 'r') as f:
        out = json.loads(f.read())
        auth = out["auth"]
        hangouts_token = out["keys"]["hangouts"]
        cookies = out["cookies"]

    client = httpx.Client(cookies=cookies, headers=config.headers)

    data = is_email_google_account(client, auth, cookies, email,
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

        # get name
        name = get_account_name(client, gaiaID)
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

        # profile picture
        profile_pic_link = infos["photo"][0]["url"]
        req = client.get(profile_pic_link)

        profile_pic_img = Image.open(BytesIO(req.content))
        profile_pic_hash = image_hash(profile_pic_img)
        is_default_profile_pic = detect_default_profile_pic(profile_pic_hash)

        if not is_default_profile_pic and not is_within_docker:
            print("\n[+] Custom profile picture !")
            print(f"=> {profile_pic_link}")
            if config.write_profile_pic and not is_within_docker:
                open(Path(config.profile_pics_dir) / f'{email}.jpg', 'wb').write(req.content)
                print("Profile picture saved !")
        else:
            print("\n[-] Default profile picture")

        # last edit
        timestamp = int(infos["metadata"]["lastUpdateTimeMicros"][:-3])
        last_edit = datetime.utcfromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S (UTC)")
        print(f"\nLast profile edit : {last_edit}\n"
              f"\nEmail : {email}\nGoogle ID : {gaiaID}\n")

        # is bot?
        profile_pic = infos["photo"][0]["url"]
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
                confidence, channels = ytb.get_confidence(data, name, profile_pic_hash)
                
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
            confidence, locations = gmaps.get_confidence(reviews, config.gmaps_radius)
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
        