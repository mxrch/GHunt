from ghunt import globals as gb
from ghunt.helpers.utils import get_httpx_client
from ghunt.objects.base import GHuntCreds
from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.apis.vision import VisionHttp
from ghunt.helpers import gmaps, playgames, auth, calendar as gcalendar, ia
from ghunt.helpers.knowledge import get_user_type_definition

import httpx

from typing import *
from pathlib import Path


async def hunt(as_client: httpx.AsyncClient, email_address: str, json_file: Path=None):
    if not as_client:
        as_client = get_httpx_client()
 
    ghunt_creds = await auth.load_and_auth(as_client)

    #gb.rc.print("[+] Target found !", style="sea_green3")

    people_pa = PeoplePaHttp(ghunt_creds)
    # vision_api = VisionHttp(ghunt_creds)
    is_found, target = await people_pa.people_lookup(as_client, email_address, params_template="max_details")
    if not is_found:
        exit("[-] The target wasn't found.")

    if json_file:
        json_results = {}

    containers = target.sourceIds

    if len(containers) > 1 or not "PROFILE" in containers:
        print("[!] You have this person in these containers :")
        for container in containers:
            print(f"- {container.title()}")

    if not "PROFILE" in containers:
        exit("[-] Given information does not match a public Google Account.")

    container = "PROFILE"
    
    gb.rc.print("🙋 Google Account data\n", style="plum2")

    # if container in target.names:
        # print(f"Name : {target.names[container].fullname}\n")

    if container in target.profilePhotos:
        if target.profilePhotos[container].isDefault:
            print("[-] Default profile picture")
        else:
            print("[+] Custom profile picture !")
            print(f"=> {target.profilePhotos[container].url}")
            
            # await ia.detect_face(vision_api, as_client, target.profilePhotos[container].url)
            print()

    if container in target.coverPhotos:
        if target.coverPhotos[container].isDefault:
            print("[-] Default cover picture\n")
        else:
            print("[+] Custom cover picture !")
            print(f"=> {target.coverPhotos[container].url}")

            # await ia.detect_face(vision_api, as_client, target.coverPhotos[container].url)
            print()

    if target.sourceIds[container].lastUpdated:
        print(f"Last profile edit : {target.sourceIds[container].lastUpdated.strftime('%Y/%m/%d %H:%M:%S (UTC)')}\n")
    else:
        gb.rc.print(f"Last profile edit : [italic]Not found.[/italic]\n")
    
    if container in target.emails:
        print(f"Email : {target.emails[container].value}")
    else:
        print(f"Email : {email_address}\n")

    print(f"Gaia ID : {target.personId}")

    if container in target.profileInfos:
        print("\nUser types :")
        for user_type in target.profileInfos[container].userTypes:
            definition = get_user_type_definition(user_type)
            gb.rc.print(f"- {user_type} [italic]({definition})[/italic]")

    gb.rc.print(f"\n📞 Google Chat Extended Data\n", style="light_salmon3")

    #print(f"Presence : {target.extendedData.dynamiteData.presence}")
    print(f"Entity Type : {target.extendedData.dynamiteData.entityType}")
    #print(f"DND State : {target.extendedData.dynamiteData.dndState}")
    gb.rc.print(f"Customer ID : {x if (x := target.extendedData.dynamiteData.customerId) else '[italic]Not found.[/italic]'}")

    gb.rc.print(f"\n🌐 Google Plus Extended Data\n", style="cyan")

    print(f"Entreprise User : {target.extendedData.gplusData.isEntrepriseUser}")
    #print(f"Content Restriction : {target.extendedData.gplusData.contentRestriction}")
    
    if container in target.inAppReachability:
        print("\n[+] Activated Google services :")
        for app in target.inAppReachability[container].apps:
            print(f"- {app}")

    gb.rc.print("\n🎮 Play Games data", style="deep_pink2")

    player_results = await playgames.search_player(ghunt_creds, as_client, email_address)
    if player_results:
        player_candidate = player_results[0]
        print("\n[+] Found player profile !")
        print(f"\nUsername : {player_candidate.name}")
        print(f"Player ID : {player_candidate.id}")
        print(f"Avatar : {player_candidate.avatar_url}")
        _, player = await playgames.get_player(ghunt_creds, as_client, player_candidate.id)
        playgames.output(player)
    else:
        print("\n[-] No player profile found.")

    gb.rc.print("\n🗺️ Maps data", style="green4")

    err, stats, reviews, photos = await gmaps.get_reviews(as_client, target.personId)
    gmaps.output(err, stats, reviews, photos, target.personId)

    gb.rc.print("\n🗓️ Calendar data\n", style="slate_blue3")

    cal_found, calendar, calendar_events = await gcalendar.fetch_all(ghunt_creds, as_client, email_address)

    if cal_found:
        print("[+] Public Google Calendar found !\n")
        if calendar_events.items:
            if "PROFILE" in target.names:
                gcalendar.out(calendar, calendar_events, email_address, target.names[container].fullname)
            else:
                gcalendar.out(calendar, calendar_events, email_address)
        else:
            print("=> No recent events found.")
    else:
        print("[-] No public Google Calendar.")

    if json_file:
        if container == "PROFILE":
            json_results[f"{container}_CONTAINER"] = {
                "profile": target,
                "play_games": player if player_results else None,
                "maps": {
                    "photos": photos,
                    "reviews": reviews,
                    "stats": stats
                },
                "calendar": {
                    "details": calendar,
                    "events": calendar_events
                } if cal_found else None
            }
        else:
            json_results[f"{container}_CONTAINER"] = {
                "profile": target
            }

    if json_file:
        import json
        from ghunt.objects.encoders import GHuntEncoder;
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_results, cls=GHuntEncoder, indent=4))
        gb.rc.print(f"\n[+] JSON output wrote to {json_file} !", style="italic")

    await as_client.aclose()
