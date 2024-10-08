import os

from ghunt.helpers.utils import *
from ghunt.objects.base import DriveExtractedUser, GHuntCreds
from ghunt.apis.drive import DriveHttp
from ghunt.apis.clientauthconfig import ClientAuthConfigHttp
from ghunt import globals as gb
from ghunt.helpers import auth
from ghunt.helpers.drive import get_comments_from_file, get_users_from_file
from ghunt.knowledge import drive as drive_knownledge

import httpx
import inflection
import humanize

import inspect
from typing import *
from datetime import timedelta


def show_user(user: DriveExtractedUser):
    if user.name:
        print(f"Full name : {user.name}")
    else:
        gb.rc.print("Full name : -", style="bright_black")
    print(f"Email : {user.email_address}")
    if user.gaia_id:
        print(f"Gaia ID : {user.gaia_id}")
    else:
        gb.rc.print("Gaia ID : -", style="bright_black")
    if user.is_last_modifying_user:
        print("[+] Last user to have modified the document !")

async def hunt(as_client: httpx.AsyncClient, file_id: str, json_file: bool=Path):
    if not as_client:
        as_client = get_httpx_client()

    ghunt_creds = await auth.load_and_auth(as_client)

    drive = DriveHttp(ghunt_creds)
    file_found, file = await drive.get_file(as_client, file_id)
    if not file_found:
        print("[-] The file wasn't found.")
        exit(os.EX_IOERR)

    is_folder = file.mime_type == "application/vnd.google-apps.folder"
    file_type = drive_knownledge.mime_types.get(file.mime_type)

    #gb.rc.print(f"[+] {'Folder' if is_folder else 'File'} found !", style="sea_green3")

    gb.rc.print("🗃️ Drive properties\n", style="deep_pink4")
        
    print(f"Title : {file.title}")
    print(f"{'Folder' if is_folder else 'File'} ID : {file.id}")
    if file.md5_checksum:
        print(f"MD5 Checksum : {file.md5_checksum}")
    if file.file_size:
        print(f"{'Folder' if is_folder else 'File'} size : {humanize.naturalsize(file.file_size)}")

    if file_type:
        gb.rc.print(f"\nType : {file_type} [italic]\[{file.mime_type}][/italic]")
    else:
        print(f"\nMime Type : {file.mime_type}")
    if is_folder:
        print(f"Folder link :\n=> {file.alternate_link}")
    else:
        print(f"Download link :\n=> {file.alternate_link}")

    print(f"\n[+] Created date : {file.created_date.strftime('%Y/%m/%d %H:%M:%S (UTC)')}")
    print(f"[+] Modified date : {file.modified_date.strftime('%Y/%m/%d %H:%M:%S (UTC)')}")

    for perm in file.permissions:
        if perm.id == "anyoneWithLink":
            giving_roles = [perm.role.upper()] + [x.upper() for x in perm.additional_roles if x != perm.role]
            print(f"\n[+] Sharing with link enabled ! Giving the role{'s' if len(giving_roles) > 1 else ''} {humanize_list(giving_roles)}.")

    #print("\n[Source application]")
    gb.rc.print("\n📱 Source application\n", style="deep_pink2")
    brand_found = False
    brand = None
    if file.source_app_id:
        print(f"App ID : {file.source_app_id}")
        cac = ClientAuthConfigHttp(ghunt_creds)
        brand_found, brand = await cac.get_brand(as_client, file.source_app_id)
        if brand_found:
            print(f"Name : {brand.display_name}")
            if brand.home_page_url:
                print(f"Home page : {brand.home_page_url}")
            else:
                gb.rc.print(f"Home page : [italic][bright_black]Not found.[/italic][/bright_black]")
        else:
            gb.rc.print("Not found.", style="italic")
    else:
        gb.rc.print("No source application.", style="italic")

    if file.image_media_metadata.height and file.image_media_metadata.width:
        #print("\n[Image metadata]")
        gb.rc.print("\n📸 Image metadata\n", style="light_coral")
        print(f"Height : {file.image_media_metadata.height}")
        print(f"Width : {file.image_media_metadata.width}")
        if isinstance((data := file.image_media_metadata.rotation), int):
            print(f"Rotation : {data}")

    if file.video_media_metadata.height and file.video_media_metadata.width:
        #print("\n[Video metadata]")
        gb.rc.print("\n📸 Video metadata\n", style="light_coral")
        print(f"Height : {file.video_media_metadata.height}")
        print(f"Width : {file.video_media_metadata.width}")
        if (data := file.video_media_metadata.duration_millis):
            duration = timedelta(milliseconds=int(file.video_media_metadata.duration_millis))
            print(f"Duration : {humanize.precisedelta(duration)}")

    #print("\n[Parents]")
    gb.rc.print("\n📂 Parents\n", style="gold3")
    if file.parents:
        print(f"[+] Parents folders :")
        for parent in file.parents:
            print(f"- 📁 {parent.id}{' [Root folder]' if parent.is_root else ''}")
    else:
        gb.rc.print("No parent folder found.", style="italic")

    if is_folder:
        #print("\n[Items]")
        gb.rc.print("\n🗃️ Items\n", style="gold3")
        found, _, drive_childs = await drive.get_childs(as_client, file_id)
        if found and drive_childs.items:
            count = f"{x if (x := len(drive_childs.items)) < 1000 else '>= 1000'}"
            print(f"[+] {count} items found inside this folder !")
        else:
            gb.rc.print("No items found.", style="italic")

    #print("\n[Users]")
    gb.rc.print("\n👪 Users\n", style="dark_orange")
    users = get_users_from_file(file)
    if (owners := [x for x in users if x.role == "owner"]):
        print(f"-> 👤 Owner{'s' if len(owners) > 1 else ''}")
        for user in owners:
            show_user(user)

    if (writers := [x for x in users if x.role == "writer"]):
        print(f"\n-> 👤 Writer{'s' if len(writers) > 1 else ''}")
        for user in writers:
            show_user(user)

    if (commenters := [x for x in users if x.role == "commenter"]):
        print(f"\n-> 👤 Commenter{'s' if len(commenters) > 1 else ''}")
        for user in commenters:
            show_user(user)

    if (readers := [x for x in users if x.role == "reader"]):
        print(f"\n-> 👤 Reader{'s' if len(readers) > 1 else ''}")
        for user in readers:
            show_user(user)

    if (nones := [x for x in users if x.role == "none"]):
        print(f"\n-> 👤 User{'s' if len(nones) > 1 else ''} with no right")
        for user in nones:
            show_user(user)

    #print("[Comments]")
    gb.rc.print("\n🗣️ Comments\n", style="plum2")
    comments_found, _, drive_comments = await drive.get_comments(as_client, file_id)
    if comments_found and drive_comments.items:
        authors = get_comments_from_file(drive_comments)
        if len(drive_comments.items) > 20:
            print(f"[+] Authors ({len(authors)} found, showing the top 20) :")
        else:
            print("[+] Authors :")
        for _, author in authors[:20]:
            print(f"- 🙋 {author['name']} ({author['count']} comment{'s' if author['count'] > 1 else ''})")
    else:
        gb.rc.print("No comments.", style="italic")

    #print("\n[Capabilities]")
    gb.rc.print("\n🧙 Capabilities\n", style="dodger_blue1")
    capabilities = sorted([k for k,v in inspect.getmembers(file.capabilities) if v and not k.startswith("_")])
    if is_folder:
        if capabilities == drive_knownledge.default_folder_capabilities:
            print("[-] You don't have special permissions against this folder.")
        else:
            print(f"[+] You have special permissions against this folder ! ✨")
            for cap in capabilities:
                print(f"- {inflection.humanize(cap)}")
    else:
        if capabilities == drive_knownledge.default_file_capabilities:
            print("[-] You don't have special permissions against this file.")
        else:
            print(f"[+] You have special permissions against this file ! ✨")
            for cap in capabilities:
                print(f"- {inflection.humanize(cap)}")

    if json_file:
        json_results = {
            "file": file if file_found else None,
            "source_app": brand if brand_found else None,
            "users": users,
            "comments": drive_comments if comments_found else None
        }

        import json
        from ghunt.objects.encoders import GHuntEncoder;
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_results, cls=GHuntEncoder, indent=4))
        gb.rc.print(f"\n[+] JSON output wrote to {json_file} !", style="italic")

    await as_client.aclose()
