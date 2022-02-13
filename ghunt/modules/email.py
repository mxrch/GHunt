from ghunt.objects.base import GHuntCreds
from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.lib import gmaps
from ghunt import globals as gb

import httpx


async def hunt(as_client: httpx.AsyncClient, email_address: str):

    if not as_client:
        as_client = httpx.AsyncClient()

    ghunt_creds = GHuntCreds()
    ghunt_creds.load_creds()

    gb.rc.print("\n🪁 Google Account data", style="dodger_blue2")

    people_pa = PeoplePaHttp(ghunt_creds)
    is_found, target = await people_pa.people_lookup(as_client, email_address, params_template="max_details")
    if not is_found:
        await as_client.aclose()
        exit("\n[-] The target wasn't found.")

    containers = target.sourceIds
    for container in containers:
        print(f"\n[{container} CONTAINER]")
        if container in target.names:
            print(f"Name : {target.names[container].fullname}\n")

        if container in target.profilePhotos:
            if target.profilePhotos[container].isDefault:
                print("[-] Default profile picture")
            else:
                print("[+] Custom profile picture !")
                print(f"=> {target.profilePhotos[container].url}")

        if container in target.coverPhotos:
            if target.coverPhotos[container].isDefault:
                print("[-] Default cover picture\n")
            else:
                print("[+] Custom cover picture !")
                print(f"=> {target.coverPhotos[container].url}\n")

        print(f"Last profile edit : {target.sourceIds[container].lastUpdated}\n")
        
        if container in target.emails:
            print(f"Email : {target.emails[container].value}")
        else:
            print(f"Email : {email_address}\n")

        print(f"Gaia ID : {target.personId}\n")

        if container in target.profileInfos:
            print("User types :")
            for user_type in target.profileInfos[container].userTypes:
                print(f"- {user_type}")
            print()

        gb.rc.print(f"📞 Hangouts Extended Data\n", style="green")

        print(f"Is bot : {target.extendedData.hangoutsData.isBot}")
        print(f"User type : {target.extendedData.hangoutsData.userType}")
        print(f"Past Hangouts State : {target.extendedData.hangoutsData.hadPastHangoutState}")

        gb.rc.print(f"\n🧨 Dynamite Extended Data\n", style="orange1")

        print(f"Presence : {target.extendedData.dynamiteData.presence}")
        print(f"Entity Type : {target.extendedData.dynamiteData.entityType}")
        print(f"DND State : {target.extendedData.dynamiteData.dndState}")
        print(f"Customer ID : {target.extendedData.dynamiteData.customerId}")

        gb.rc.print(f"\n🌐 Google Plus Extended Data\n", style="cyan")

        print(f"Entreprise User : {target.extendedData.gplusData.isEntrepriseUser}")
        print(f"Content Restriction : {target.extendedData.gplusData.contentRestriction}")
        
        if container in target.inAppReachability:
            print("\n[+] Activated Google services :")
            for app in target.inAppReachability[container].apps:
                print(f"- {app}")

        gb.rc.print("\n🗺️ Maps data", style="green4")

        err, stats, reviews, photos = await gmaps.get_reviews(as_client, target.personId)
        gmaps.output(err, stats, reviews, photos, target.personId)

    await as_client.aclose()