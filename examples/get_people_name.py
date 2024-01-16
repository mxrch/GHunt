import httpx

import asyncio
import sys

from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.objects.base import GHuntCreds


async def main():
    if not sys.argv[1:]:
        exit("Please give an email address.")
    email = sys.argv[1]

    ghunt_creds = GHuntCreds()
    ghunt_creds.load_creds() # Check creds (but it doesn't crash if they are invalid)

    as_client = httpx.AsyncClient() # Async client

    people_api = PeoplePaHttp(ghunt_creds)
    found, person = await people_api.people_lookup(as_client, email, params_template="just_name")
                                                                    # You can have multiple "params_template" for the GHunt APIs,
                                                                    # for example, on this endpoint, you have "just_gaia_id" by default,
                                                                    # "just_name" or "max_details" which is used in the email CLI module.

    print("Found :", found)
    if found:
        if "PROFILE" in person.names: # A specification of People API, there are different containers
                                          # A target may not exists globally, but only in your contacts,
                                          # so it will show you only the CONTACT container,
                                          # with the informations you submitted.
                                          # What we want here is the PROFILE container, with public infos.

            print("Name :", person.names["PROFILE"].fullname)
        else:
            print("Not existing globally.")

asyncio.run(main()) # running our async code in a non-async code