from datetime import datetime

from ghunt.errors import *
from ghunt.lib.utils import is_default_profile_pic
from ghunt.objects.apis import Parser

import httpx


class PersonGplusExtendedData():
    def __init__(self):
        self.contentRestriction: str = ""
        self.isEntrepriseUser: bool = False

    def _scrape(self, gplus_data):
        self.contentRestriction = gplus_data.get("contentRestriction")
        
        if (isEnterpriseUser := gplus_data.get("isEnterpriseUser")):
            self.isEntrepriseUser = isEnterpriseUser

class PersonDynamiteExtendedData():
    def __init__(self):
        self.presence: str = ""
        self.entityType: str = ""
        self.dndState: str = ""
        self.customerId: str = ""

    def _scrape(self, dynamite_data):
        self.presence = dynamite_data.get("presence")
        self.entityType = dynamite_data.get("entityType")
        self.dndState = dynamite_data.get("dndState")
        if (customerId := dynamite_data.get("organizationInfo", {}).get("customerInfo", {}).
            get("customerId", {}).get("customerId")):
            self.customerId = customerId


class PersonHangoutsExtendedData():
    def __init__(self):
        self.isBot: bool = False
        self.userType: str = ""
        self.hadPastHangoutState: str = ""

    def _scrape(self, hangouts_data):
        if (isBot := hangouts_data.get("isBot")):
            self.isBot = isBot

        self.userType = hangouts_data.get("userType")
        self.hadPastHangoutState = hangouts_data.get("hasPastHangoutState")

class PersonExtendedData():
    def __init__(self):
         self.hangoutsData: PersonHangoutsExtendedData = PersonHangoutsExtendedData()
         self.dynamiteData: PersonDynamiteExtendedData = PersonDynamiteExtendedData()
         self.gplusData: PersonGplusExtendedData = PersonGplusExtendedData()

    def _scrape(self, extended_data: dict[str, any]):
        if (hangouts_data := extended_data.get("hangoutsExtendedData")):
            self.hangoutsData._scrape(hangouts_data)

        if (dynamite_data := extended_data.get("dynamiteExtendedData")):
            self.dynamiteData._scrape(dynamite_data)

        if (gplus_data := extended_data.get("gplusExtendedData")):
            self.gplusData._scrape(gplus_data)

class PersonPhoto():
    def __init__(self):
        self.url: str = ""
        self.isDefault: bool = False

    async def _scrape(self, as_client: httpx.AsyncClient, photo_data: dict[str, any], photo_type: str):
        if photo_type == "profile_photo":
            self.url = photo_data.get("url")
            self.isDefault = await is_default_profile_pic(as_client, self.url)
            
        elif photo_type == "cover_photo":
            self.url = '='.join(photo_data.get("imageUrl").split("=")[:-1])
            if (isDefault := photo_data.get("isDefault")):
                self.isDefault = isDefault
        else:
            raise GHuntAPIResponseParsingError(f'The provided photo type "{photo_type}" weren\'t recognized.')

class PersonEmail():
    def __init__(self):
        self.value: str = ""
    
    def _scrape(self, email_data: dict[str, any]):
        self.value = email_data.get("value")

class PersonName():
    def __init__(self):
        self.fullname: str = ""
        self.firstName: str = ""
        self.lastName: str = ""

    def _scrape(self, name_data: dict[str, any]):
        self.fullname = name_data.get("displayName")
        self.firstName = name_data.get("givenName")
        self.lastName = name_data.get("familyName")

class PersonProfileInfo():
    def __init__(self):
        self.userTypes: list[str] = []

    def _scrape(self, profile_data: dict[str, any]):
        if "ownerUserType" in profile_data:
            self.userTypes += profile_data.get("ownerUserType")

class PersonSourceIds():
    def __init__(self):
        self.lastUpdated: datetime = None

    def _scrape(self, source_ids_data: dict[str, any]):
        if (timestamp := source_ids_data.get("lastUpdatedMicros")):
            self.lastUpdated = datetime.utcfromtimestamp(float(timestamp[:-6])).strftime("%Y/%m/%d %H:%M:%S (UTC)")

class PersonInAppReachability():
    def __init__(self):
        self.apps: list[str] = []

    def _scrape(self, apps_data, container_name: str):
        for app in apps_data:
            if app["metadata"]["container"] == container_name:
                self.apps.append(app["appType"].title())

class PersonContainers(dict):
    pass

class Person(Parser):
    def __init__(self):
        self.personId: str = ""
        self.sourceIds: dict[str, PersonSourceIds] = PersonContainers() # All the fetched containers
        self.emails: dict[str, PersonEmail] = PersonContainers()
        self.names: dict[str, PersonName] = PersonContainers()
        self.profileInfos: dict[str, PersonProfileInfo] = PersonContainers()
        self.profilePhotos: dict[str, PersonPhoto] = PersonContainers()
        self.coverPhotos: dict[str, PersonPhoto] = PersonContainers()
        self.inAppReachability: dict[str, PersonInAppReachability] = PersonContainers()
        self.extendedData: PersonExtendedData = PersonExtendedData()

    async def _scrape(self, as_client: httpx.AsyncClient, person_data: dict[str, any]):
        self.personId = person_data.get("personId")
        if person_data.get("email"):
            for email_data in person_data["email"]:
                person_email = PersonEmail()
                person_email._scrape(email_data)
                self.emails[email_data["metadata"]["container"]] = person_email

        if person_data.get("name"):
            for name_data in person_data["name"]:
                person_name = PersonName()
                person_name._scrape(name_data)
                self.names[name_data["metadata"]["container"]] = person_name

        if person_data.get("readOnlyProfileInfo"):
            for profile_data in person_data["readOnlyProfileInfo"]:
                person_profile = PersonProfileInfo()
                person_profile._scrape(profile_data)
                self.profileInfos[profile_data["metadata"]["container"]] = person_profile

        if (source_ids := person_data.get("metadata", {}).get("identityInfo", {}).get("sourceIds")):
            for source_ids_data in source_ids:
                person_source_ids = PersonSourceIds()
                person_source_ids._scrape(source_ids_data)
                self.sourceIds[source_ids_data["container"]] = person_source_ids

        if person_data.get("photo"):
            for photo_data in person_data["photo"]:
                person_photo = PersonPhoto()
                await person_photo._scrape(as_client, photo_data, "profile_photo")
                self.profilePhotos[profile_data["metadata"]["container"]] = person_photo

        if person_data.get("coverPhoto"):
            for cover_photo_data in person_data["coverPhoto"]:
                person_cover_photo = PersonPhoto()
                await person_cover_photo._scrape(as_client, cover_photo_data, "cover_photo")
                self.coverPhotos[cover_photo_data["metadata"]["container"]] = person_cover_photo

        if (apps_data := person_data.get("inAppReachability")):
            containers_names = set()
            for app_data in person_data["inAppReachability"]:
                containers_names.add(app_data["metadata"]["container"])

            for container_name in containers_names:
                person_app_reachability = PersonInAppReachability()
                person_app_reachability._scrape(apps_data, container_name)
                self.inAppReachability[container_name] = person_app_reachability

        if (extended_data := person_data.get("extendedData")):
            self.extendedData._scrape(extended_data)