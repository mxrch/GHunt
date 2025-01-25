from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.people import Person

import httpx

from typing import *
import inspect
import json


class PeoplePaHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {
            "Host": "people-pa.clients6.google.com",
        }

        headers = {**headers, **base_headers}

        self.hostname = "googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def people_lookup(self, as_client: httpx.AsyncClient, email: str, params_template="just_gaia_id") -> Tuple[bool, Person]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None
            require_key = "photos", # key name, or None
            # key_origin="photos"
        )

        # Android OAuth fields
        self.api_name = "people"
        self.package_name = "com.google.android.gms"
        self.scopes = [
            "https://www.googleapis.com/auth/profile.agerange.read",
            "https://www.googleapis.com/auth/profile.language.read",
            "https://www.googleapis.com/auth/contacts",
            "https://www.googleapis.com/auth/peopleapi.legacy.readwrite"

        ]

        self._load_endpoint(endpoint)

        base_url = "/v2/people/lookup"

        params_templates = {
            "just_gaia_id": {
                "id": email,
                "type": "EMAIL",
                "matchType": "EXACT",
                "requestMask.includeField.paths": "person.metadata"
            },
            "just_name": {
                "id": email,
                "type": "EMAIL",
                "matchType": "EXACT",
                "requestMask.includeField.paths": "person.name",
                "core_id_params.enable_private_names": True
            },
            "max_details": {
                "id": email,
                "type": "EMAIL",
                "match_type": "EXACT",
                "extension_set.extension_names": [
                    "DYNAMITE_ADDITIONAL_DATA",
                    "DYNAMITE_ORGANIZATION_INFO"
                ],
                "request_mask.include_field.paths": [
                    "person.metadata.best_display_name",
                    "person.photo",
                    "person.cover_photo",
                    "person.interaction_settings",
                    "person.legacy_fields",
                    "person.metadata",
                    "person.in_app_reachability",
                    "person.name",
                    "person.read_only_profile_info",
                    "person.sort_keys",
                    "person.email"
                ],
                "request_mask.include_container": [
                    "AFFINITY",
                    "PROFILE",
                    "DOMAIN_PROFILE",
                    "ACCOUNT",
                    "EXTERNAL_ACCOUNT",
                    "CIRCLE",
                    "DOMAIN_CONTACT",
                    "DEVICE_CONTACT",
                    "GOOGLE_GROUP",
                    "CONTACT"
                ],
                "core_id_params.enable_private_names": True
            }
        }

        if not params_templates.get(params_template):
            raise GHuntParamsTemplateError(f"The asked template {params_template} for the endpoint {endpoint.name} wasn't recognized by GHunt.")
        params = params_templates[params_template]

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        person = Person()
        if not data:
            return False, person
        
        person_data = list(data["people"].values())[0]
        await person._scrape(as_client, person_data)

        return True, person

    async def people(self, as_client: httpx.AsyncClient, gaia_id: str, params_template="just_name") -> Tuple[bool, Person]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None
            require_key = "photos", # key name, or None
            # key_origin="photos"
        )
        self._load_endpoint(endpoint)

        # Android OAuth fields
        self.api_name = "people"
        self.package_name = "com.google.android.gms"
        self.scopes = [
            "https://www.googleapis.com/auth/profile.agerange.read",
            "https://www.googleapis.com/auth/profile.language.read",
            "https://www.googleapis.com/auth/contacts",
            "https://www.googleapis.com/auth/peopleapi.legacy.readwrite"

        ]

        base_url = "/v2/people"

        params_templates = {
            "just_name": {
                "person_id": gaia_id,
                "requestMask.includeField.paths": "person.name",
                "core_id_params.enable_private_names": True
            },
            "max_details": {
                "person_id": gaia_id,
                "extension_set.extension_names": [
                    "DYNAMITE_ADDITIONAL_DATA",
                    "DYNAMITE_ORGANIZATION_INFO"
                ],
                "request_mask.include_field.paths": [
                    "person.metadata.best_display_name",
                    "person.photo",
                    "person.cover_photo",
                    "person.interaction_settings",
                    "person.legacy_fields",
                    "person.metadata",
                    "person.in_app_reachability",
                    "person.name",
                    "person.read_only_profile_info",
                    "person.sort_keys",
                    "person.email"
                ],
                "request_mask.include_container": [
                    "AFFINITY",
                    "PROFILE",
                    "DOMAIN_PROFILE",
                    "ACCOUNT",
                    "EXTERNAL_ACCOUNT",
                    "CIRCLE",
                    "DOMAIN_CONTACT",
                    "DEVICE_CONTACT",
                    "GOOGLE_GROUP",
                    "CONTACT"
                ],
                "core_id_params.enable_private_names": True
            }
        }

        if not params_templates.get(params_template):
            raise GHuntParamsTemplateError(f"The asked template {params_template} for the endpoint {endpoint.name} wasn't recognized by GHunt.")
        params = params_templates[params_template]

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        person = Person()
        if data["personResponse"][0]["status"] == "NOT_FOUND":
            return False, person
        
        person_data = data["personResponse"][0]["person"]
        await person._scrape(as_client, person_data)

        return True, person