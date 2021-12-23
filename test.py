from ghunt.objects.base import GHuntCreds
from ghunt.apis.peoplepa import PeoplePaHttp

from ghunt import config
from ghunt import globals as gb

import trio
import httpx

import ghunt.parsers.people


gb.init_globals()
gb.config = config # We export the given config to a project-wide global variable
config.silent_mode = False # If true, no print is being executed

async def main():
    ghunt_creds = GHuntCreds()
    ghunt_creds.load_creds()

    as_client = httpx.AsyncClient()

    people_pa = PeoplePaHttp(ghunt_creds)
    is_found, target = await people_pa.people_lookup(as_client, "larry@google.com", params_template="max_details")
    if not is_found:
        await as_client.aclose()
        exit("[-] The target wasn't found.")

    containers = target.sourceIds
    for container in containers:
        print(f"\n[{container.title()}]")
        print(f"Entreprise User : {target.extendedData.gplusData.isEntrepriseUser}")

    await as_client.aclose()

trio.run(main)