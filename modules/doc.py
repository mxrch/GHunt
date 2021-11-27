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

import config
from lib.utils import *
from lib.banner import banner


def doc_hunt(doc_link):
    banner()

    tmprinter = TMPrinter()

    if not doc_link:
        exit("Please give the link to a Google resource.\nExample : https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

    is_within_docker = within_docker()
    if is_within_docker:
        print("[+] Docker detected, profile pictures will not be saved.")

    doc_id = ''.join([x for x in doc_link.split("?")[0].split("/") if len(x) in (33, 44)])
    if doc_id:
        print(f"\nDocument ID : {doc_id}\n")
    else:
        exit("\nDocument ID not found.\nPlease make sure you have something that looks like this in your link :\1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

    if not isfile(config.data_path):
        exit("Please generate cookies and tokens first, with the check_and_gen.py script.")

    internal_token = ""
    cookies = {}

    with open(config.data_path, 'r') as f:
        out = json.loads(f.read())
        internal_token = out["keys"]["internal"]
        cookies = out["cookies"]

    headers = {**config.headers, **{"X-Origin": "https://drive.google.com"}}
    client = httpx.Client(cookies=cookies, headers=headers)

    url = f"https://clients6.google.com/drive/v2beta/files/{doc_id}?fields=alternateLink%2CcopyRequiresWriterPermission%2CcreatedDate%2Cdescription%2CdriveId%2CfileSize%2CiconLink%2Cid%2Clabels(starred%2C%20trashed)%2ClastViewedByMeDate%2CmodifiedDate%2Cshared%2CteamDriveId%2CuserPermission(id%2Cname%2CemailAddress%2Cdomain%2Crole%2CadditionalRoles%2CphotoLink%2Ctype%2CwithLink)%2Cpermissions(id%2Cname%2CemailAddress%2Cdomain%2Crole%2CadditionalRoles%2CphotoLink%2Ctype%2CwithLink)%2Cparents(id)%2Ccapabilities(canMoveItemWithinDrive%2CcanMoveItemOutOfDrive%2CcanMoveItemOutOfTeamDrive%2CcanAddChildren%2CcanEdit%2CcanDownload%2CcanComment%2CcanMoveChildrenWithinDrive%2CcanRename%2CcanRemoveChildren%2CcanMoveItemIntoTeamDrive)%2Ckind&supportsTeamDrives=true&enforceSingleParent=true&key={internal_token}"
    
    retries = 100
    for retry in range(retries):
        req = client.get(url)
        if "File not found" in req.text:
            exit("[-] This file does not exist or is not public")
        elif "rateLimitExceeded" in req.text:
            tmprinter.out(f"[-] Rate-limit detected, retrying... {retry+1}/{retries}")
            continue
        else:
            break
    else:
        tmprinter.clear()
        exit("[-] Rate-limit exceeded. Try again later.")

    if '"reason": "keyInvalid"' in req.text:
        exit("[-] Your key is invalid, try regenerating your cookies & keys.")

    tmprinter.clear()
    data = json.loads(req.text)

    # Extracting informations

    # Dates

    created_date = datetime.strptime(data["createdDate"], '%Y-%m-%dT%H:%M:%S.%fz')
    modified_date = datetime.strptime(data["modifiedDate"], '%Y-%m-%dT%H:%M:%S.%fz')

    print(f"[+] Creation date : {created_date.strftime('%Y/%m/%d %H:%M:%S')} (UTC)")
    print(f"[+] Last edit date : {modified_date.strftime('%Y/%m/%d %H:%M:%S')} (UTC)")

    # Permissions

    user_permissions = []
    if data["userPermission"]:
        if data["userPermission"]["id"] == "me":
            user_permissions.append(data["userPermission"]["role"])
            if "additionalRoles" in data["userPermission"]:
                user_permissions += data["userPermission"]["additionalRoles"]

    public_permissions = []
    owner = None
    for permission in data["permissions"]:
        if permission["id"] in ["anyoneWithLink", "anyone"]:
            public_permissions.append(permission["role"])
            if "additionalRoles" in data["permissions"]:
                public_permissions += permission["additionalRoles"]
        elif permission["role"] == "owner":
            owner = permission

    print("\nPublic permissions :")
    for permission in public_permissions:
        print(f"- {permission}")

    if public_permissions != user_permissions:
        print("[+] You have special permissions :")
        for permission in user_permissions:
            print(f"- {permission}")

    if owner:
        print("\n[+] Owner found !\n")
        print(f"Name : {owner['name']}")
        print(f"Email : {owner['emailAddress']}")
        print(f"Google ID : {owner['id']}")
        
        # profile picture
        profile_pic_link = owner['photoLink']
        req = client.get(profile_pic_link)

        profile_pic_img = Image.open(BytesIO(req.content))
        profile_pic_flathash = image_hash(profile_pic_img)
        is_default_profile_pic = detect_default_profile_pic(profile_pic_flathash)

        if not is_default_profile_pic and not is_within_docker:
            print("\n[+] Custom profile picture !")
            print(f"=> {profile_pic_link}")
            if config.write_profile_pic and not is_within_docker:
                open(Path(config.profile_pics_dir) / f'{owner["emailAddress"]}.jpg', 'wb').write(req.content)
                print("Profile picture saved !\n")
        else:
            print("\n[-] Default profile picture\n")