from ghunt.errors import GHuntCorruptedHeadersError
from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import HttpAPI

import httpx

import inspect


class PeoplePaHttp(HttpAPI):
    def __init__(self, creds: GHuntCreds, headers: dict[str, str] = {}):
        if not headers:
            headers = gb.config.headers

        self.hostname = "people-pa.clients6.google.com"
        self.scheme = "https"

        self.require_key = "hangouts" # key name, or None

        self._load_api(creds, headers)

    async def people_lookup(self, as_client: httpx.AsyncClient, email: str, params_template="just_gaia_id"):
        endpoint_name = inspect.currentframe().f_code.co_name

        verb = "GET"
        base_url = "/v2/people/lookup"
        require_sapisidhash = True # bool, and if true, cookies must be true
        require_cookies = True # bool
        params_templates = {
            "just_gaia_id": {
                "id": email,
                "type": "EMAIL",
                "matchType": "EXACT",
                "requestMask.includeField.paths": "person.name" # We need at least one requestmask
            },
            "max_details": {
                "id": email,
                "type": "EMAIL",
                "matchType": "EXACT",
                "extensionSet.extensionNames": [
                    "HANGOUTS_ADDITIONAL_DATA",
                    "HANGOUTS_OFF_NETWORK_GAIA_LOOKUP",
                    "HANGOUTS_PHONE_DATA",
                    "TLS_FILL_FIELD",
                    "DYNAMITE_ADDITIONAL_DATA",
                    "DYNAMITE_ORGANIZATION_INFO",
                    "GPLUS_ADDITIONAL_DATA"
                    ]
            }
        }

        if not params_templates.get(params_template):
            raise GHuntParamsTemplateError(f"The asked template {params_template} for the endpoint {endpoint_name} wasn't recognized by GHunt.")

        self._load_endpoint(endpoint_name, require_sapisidhash, require_cookies)
        await self._query(as_client, verb, endpoint_name, base_url, params_templates[params_template])