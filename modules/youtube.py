#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from datetime import date
from io import BytesIO
from os.path import isfile
from pathlib import Path
from pprint import pprint

import httpx
import wayback
from PIL import Image
from bs4 import BeautifulSoup as bs
from geopy.geocoders import Nominatim

import config
from lib.banner import banner
import lib.gmaps as gmaps
import lib.youtube as ytb
from lib.utils import *


def find_gaiaID(body):
    """
    We don't use a regex to avoid extracting an other gaiaID
    for example if the target had put a secondary Google Plus blog in his channel social links.
    """

    # 1st method ~ 2014
    try:
        publisher = body.find("link", {"rel": "publisher"})
        gaiaID = publisher.attrs["href"].split("/")[-1]
    except:
        pass
    else:
        if gaiaID:
            return gaiaID

    # 2nd method ~ 2015
    try:
        author_links = [x.find_next("link") for x in body.find_all("span", {"itemprop": "author"})]
        valid_author_link = [x for x in author_links if "plus.google.com/" in x.attrs["href"]][0]
        gaiaID = valid_author_link.attrs["href"].split("/")[-1]
    except:
        pass
    else:
        if gaiaID:
            return gaiaID

    # 3rd method ~ 2019
    try:
        data = json.loads(str(body).split('window["ytInitialData"] = ')[1].split('window["ytInitialPlayerResponse"]')[0].strip().strip(";"))
        gaiaID = data["metadata"]["channelMetadataRenderer"]["plusPageLink"].split("/")[-1]
    except:
        pass
    else:
        if gaiaID:
            return gaiaID

def analyze_snapshots(client, wb_client, channel_url, dates):
    body = None
    record = None
    for record in wb_client.search(channel_url, to_date=dates["to"], from_date=dates["from"]):
        try:
            req = client.get(record.raw_url)
            if req.status_code == 429:
                continue # Rate-limit is fucked up and is snapshot-based, we can just take the next snapshot
        except Exception as err:
            pass
        else:
            if re.compile(config.regexs["gplus"]).findall(req.text):
                body = bs(req.text, 'html.parser')
                #print(record)
                print(f'[+] Snapshot : {record.timestamp.strftime("%d/%m/%Y")}')
                break
    else:
        return None

    gaiaID = find_gaiaID(body)
    return gaiaID

def check_channel(client, wb_client, channel_url):
    # Fast check (no doubt that GaiaID is present in this period)

    dates = {"to": date(2019, 12, 31), "from": date(2014, 1, 1)}
    gaiaID = analyze_snapshots(client, wb_client, channel_url, dates)

    # Complete check

    if not gaiaID:
        dates = {"to": date(2020, 7, 31), "from": date(2013, 6, 3)}
        gaiaID = analyze_snapshots(client, wb_client, channel_url, dates)

    return gaiaID

def launch_checks(client, wb_client, channel_data):
    for channel_url in channel_data["channel_urls"]:
        gaiaID = check_channel(client, wb_client, channel_url)
        if gaiaID:
            return gaiaID

    return False

def youtube_hunt(channel_url):
    banner()

    if not channel_url:
        exit("Please give a valid channel URL.\nExample : https://www.youtube.com/user/PewDiePie")

    if not isfile(config.data_path):
        exit("Please generate cookies and tokens first, with the check_and_gen.py script.")

    internal_auth = ""
    internal_token = ""

    cookies = {}

    with open(config.data_path, 'r') as f:
        out = json.loads(f.read())
        internal_auth = out["internal_auth"]
        internal_token = out["keys"]["internal"]
        cookies = out["cookies"]

    if not "PREF" in cookies:
        pref_cookies = {"PREF": "tz=Europe.Paris&f6=40000000&hl=en"} # To set the lang in english
        cookies = {**cookies, **pref_cookies}

    client = httpx.Client(cookies=cookies, headers=config.headers)

    is_within_docker = within_docker()
    if is_within_docker:
        print("[+] Docker detected, profile pictures will not be saved.")

    geolocator = Nominatim(user_agent="nominatim")

    print("\n📌 [Youtube channel]")

    channel_data = ytb.get_channel_data(client, channel_url)
    if channel_data:
        is_channel_existing = True
        print(f'[+] Channel name : {channel_data["name"]}\n')
    else:
        is_channel_existing = False
        print("[-] Channel not found.\nSearching for a trace in the archives...\n")

        channel_data = {
        "name": None,
        "description": None,
        "channel_urls": [channel_url],
        "email_contact": False,
        "views": None,
        "joined_date": None,
        "primary_links": [],
        "country": None
        }

    wb_client = wayback.WaybackClient()
    gaiaID = launch_checks(client, wb_client, channel_data)
    if gaiaID:
        print(f"[+] GaiaID => {gaiaID}\n")
    else:
        print("[-] No interesting snapshot found.\n")

    if is_channel_existing:
        if channel_data["email_contact"]:
            print(f'[+] Email on profile : available !')
        else:
            print(f'[-] Email on profile : not available.')
        if channel_data["country"]:
            print(f'[+] Country : {channel_data["country"]}')
        print()
        if channel_data["description"]:
            print(f'🧬 Description : {channel_data["description"]}')
        if channel_data["views"]:
            print(f'🧬 Total views : {channel_data["views"]}')
        if channel_data["joined_date"]:
            print(f'🧬 Joined date : {channel_data["joined_date"]}')

        if channel_data["primary_links"]:
            print(f'\n[+] Primary links ({len(channel_data["primary_links"])} found)')
            for primary_link in channel_data["primary_links"]:
                print(f'- {primary_link["title"]} => {primary_link["url"]}')


    if not gaiaID:
        exit()

    print("\n📌 [Google account]")
    # get name & profile picture
    account = get_account_data(client, gaiaID, internal_auth, internal_token, config)
    name = account["name"]

    if name:
        print(f"Name : {name}")

    # profile picture
    profile_pic_url = account.get("profile_pics") and account["profile_pics"][0].url
    req = client.get(profile_pic_url)

    profile_pic_img = Image.open(BytesIO(req.content))
    profile_pic_hash = image_hash(profile_pic_img)
    is_default_profile_pic = detect_default_profile_pic(profile_pic_hash)

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
                open(Path(config.profile_pics_dir) / f'{gaiaID}.jpg', 'wb').write(req.content)
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
            open(Path(config.profile_pics_dir) / f'cover_{gaiaID}.jpg', 'wb').write(req.content)
            print("Cover profile picture saved !")

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
