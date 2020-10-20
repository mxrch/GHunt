import json
import sys
from datetime import datetime
from io import BytesIO
from os.path import isfile

import httpx
from PIL import Image
from geopy.geocoders import Nominatim

from lib.banner import banner
import lib.gmaps as gmaps
import lib.youtube as ytb
import config
from lib.photos import gpics
from lib.utils import *

if __name__ == "__main__":

    banner()

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
                print("Couldn't find name")
            else:
                for i in range(len(infos["name"])):
                    print(f"Name : {infos['name'][i]['displayName']}")
                if len(infos["name"]) > 0:
                    name = infos["name"][0]["displayName"]

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
            if "youtube" in services and name:
                ytb_hunt = True
            print("\nActivated Google services :")
            print('\n'.join(["- " + x.capitalize() for x in services]))

        except KeyError:
            ytb_hunt = True
            print("\nUnable to fetch connected Google services.")

        # check YouTube
        if ytb_hunt or config.ytb_hunt_always:
            confidence = None
            req = client.get(profile_pic)
            img = Image.open(BytesIO(req.content))
            hash = image_hash(img)
            data = ytb.get_channels(client, name, config.data_path,
                                   config.gdocs_public_doc)
            if not data:
                print("\nYouTube channel not found.")
            else:
                confidence, channels = ytb.get_confidence(data, name, hash)

            if confidence:
                print(f"\nYouTube channel (confidence => {confidence}%) :")
                for channel in channels:
                    print(f"- [{channel['name']}] {channel['profile_url']}")
                possible_usernames = ytb.extract_usernames(channels)
                if possible_usernames:
                    print("\nPossible usernames found :")
                    for username in possible_usernames:
                        print(f"- {username}")
            else:
                print("\nYouTube channel not found.")

        # TODO: return gpics function output here
        #gpics(gaiaID, client, cookies, config.headers, config.regexs["albums"], config.regexs["photos"],
        #      config.headless)

        # reviews
        reviews = gmaps.scrape(gaiaID, client, cookies, config.headers, config.regexs["review_loc_by_id"], config.headless)

        if reviews:
            confidence, locations = gmaps.get_confidence(reviews, config.gmaps_radius)
            print(f"\nProbable location (confidence => {confidence}) :")

            loc_names = []
            for loc in locations:
                loc_names.append(
                    f"- {loc['avg']['town']}, {loc['avg']['country']}"
                )

            loc_names = set(loc_names)  # delete duplicates
            for loc in loc_names:
                print(loc)
