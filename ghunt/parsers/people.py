from typing import *
from datetime import datetime

from ghunt.errors import *
from ghunt.helpers.utils import is_default_profile_pic, unicode_patch
from ghunt.objects.apis import Parser

import httpx
import imagehash


class PersonGplusExtendedData(Parser):
    def __init__(self):
        self.contentRestriction: str = ""
        self.isEntrepriseUser: bool = False

    def _scrape(self, gplus_data):
        self.contentRestriction = gplus_data.get("contentRestriction")

        if (isEnterpriseUser := gplus_data.get("isEnterpriseUser")):
            self.isEntrepriseUser = isEnterpriseUser


class PersonDynamiteExtendedData(Parser):
    def __init__(self):
        self.presence: str = ""
        self.entityType: str = ""
        self.dndState: str = ""
        self.customerId: str = ""

    def _scrape(self, dynamite_data):
        self.presence = dynamite_data.get("presence")
        self.entityType = dynamite_data.get("entityType")
        self.dndState = dynamite_data.get("dndState")

        if (customerId := dynamite_data.get("organizationInfo", {})
            .get("customerInfo", {})
            .get("customerId", {})
            .get("customerId")):
            self.customerId = customerId


class PersonExtendedData(Parser):
    def __init__(self):
        self.dynamiteData: PersonDynamiteExtendedData = PersonDynamiteExtendedData()
        self.gplusData: PersonGplusExtendedData = PersonGplusExtendedData()

    def _scrape(self, extended_data: Dict[str, any]):
        if (dynamite_data := extended_data.get("dynamiteExtendedData")):
            self.dynamiteData._scrape(dynamite_data)

        if (gplus_data := extended_data.get("gplusExtendedData")):
            self.gplusData._scrape(gplus_data)


class PersonPhoto(Parser):
    def __init__(self):
        self.url: str = ""
        self.isDefault: bool = False
        self.flathash: str = None

    async def _scrape(self, as_client: httpx.AsyncClient, photo_data: Dict[str, any], photo_type: str):
        if photo_type == "profile_photo":
            self.url = photo_data.get("url")
            self.isDefault, self.flathash = await is_default_profile_pic(as_client, self.url)

        elif photo_type == "cover_photo":
            image_url = photo_data.get("imageUrl", "")
            if image_url:
                self.url = '='.join(image_url.split("=")[:-1])
            self.isDefault = photo_data.get("isDefault", False)
        else:
            raise GHuntAPIResponseParsingError(f'The provided photo type "{photo_type}" weren\'t recognized.')


class PersonEmail(Parser):
    def __init__(self):
        self.value: str = ""

    def _scrape(self, email_data: Dict[str, any]):
        self.value = email_data.get("value")


class PersonName(Parser):
    def __init__(self):
        self.fullname: str = ""
        self.firstName: str = ""
        self.lastName: str = ""

    def _scrape(self, name_data: Dict[str, any]):
        pass


class PersonProfileInfo(Parser):
    def __init__(self):
        self.userTypes: List[str] = []

    def _scrape(self, profile_data: Dict[str, any]):
        if "ownerUserType" in profile_data:
            self.userTypes += profile_data.get("ownerUserType", [])


class PersonSourceIds(Parser):
    def __init__(self):
        self.lastUpdated: datetime = None

    def _scrape(self, source_ids_data: Dict[str, any]):
        if (timestamp := source_ids_data.get("lastUpdatedMicros")):
            self.lastUpdated = datetime.utcfromtimestamp(float(timestamp[:10]))


class PersonInAppReachability(Parser):
    def __init__(self):
        self.apps: List[str] = []

    def _scrape(self, apps_data, container_name: str):
        for app in apps_data:
            if app.get("metadata", {}).get("container") == container_name:
                self.apps.append(app.get("appType", "").title())


class PersonContainers(dict):
    pass


class Person(Parser):
    def __init__(self):
        self.personId: str = ""
        self.sourceIds: Dict[str, PersonSourceIds] = PersonContainers()
        self.emails: Dict[str, PersonEmail] = PersonContainers()
        self.names: Dict[str, PersonName] = PersonContainers()
        self.profileInfos: Dict[str, PersonProfileInfo] = PersonContainers()
        self.profilePhotos: Dict[str, PersonPhoto] = PersonContainers()
        self.coverPhotos: Dict[str, PersonPhoto] = PersonContainers()
        self.inAppReachability: Dict[str, PersonInAppReachability] = PersonContainers()
        self.extendedData: PersonExtendedData = PersonExtendedData()

    async def _scrape(self, as_client: httpx.AsyncClient, person_data: Dict[str, any]):
        self.personId = person_data.get("personId")

        if person_data.get("email"):
            for email_data in person_data["email"]:
                container = email_data.get("metadata", {}).get("container")
                if not container:
                    continue
                person_email = PersonEmail()
                person_email._scrape(email_data)
                self.emails[container] = person_email

        if person_data.get("name"):
            for name_data in person_data["name"]:
                container = name_data.get("metadata", {}).get("container")
                if not container:
                    continue
                person_name = PersonName()
                person_name._scrape(name_data)
                self.names[container] = person_name

        if person_data.get("readOnlyProfileInfo"):
            for profile_data in person_data["readOnlyProfileInfo"]:
                container = profile_data.get("metadata", {}).get("container")
                if not container:
                    continue

                person_profile = PersonProfileInfo()
                person_profile._scrape(profile_data)
                self.profileInfos[container] = person_profile

                if person_data.get("photo"):
                    for photo_data in person_data["photo"]:
                        person_photo = PersonPhoto()
                        await person_photo._scrape(as_client, photo_data, "profile_photo")
                        self.profilePhotos[container] = person_photo

        if (source_ids := person_data.get("metadata", {}).get("identityInfo", {}).get("sourceIds")):
            for source_ids_data in source_ids:
                container = source_ids_data.get("container")
                if not container:
                    continue
                person_source_ids = PersonSourceIds()
                person_source_ids._scrape(source_ids_data)
                self.sourceIds[container] = person_source_ids

        if person_data.get("coverPhoto"):
            for cover_photo_data in person_data["coverPhoto"]:
                container = cover_photo_data.get("metadata", {}).get("container")
                if not container:
                    continue
                person_cover_photo = PersonPhoto()
                await person_cover_photo._scrape(as_client, cover_photo_data, "cover_photo")
                self.coverPhotos[container] = person_cover_photo

        if (apps_data := person_data.get("inAppReachability")):
            containers_names = set()
            for app_data in apps_data:
                container = app_data.get("metadata", {}).get("container")
                if container:
                    containers_names.add(container)

            for container_name in containers_names:
                person_app_reachability = PersonInAppReachability()
                person_app_reachability._scrape(apps_data, container_name)
                self.inAppReachability[container_name] = person_app_reachability

        if (extended_data := person_data.get("extendedData")):
            self.extendedData._scrape(extended_data)
