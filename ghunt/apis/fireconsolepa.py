from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.clientauthconfig import CacBrand

import httpx

from typing import *
import inspect
import json


class FireconsolePaHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "fireconsole-pa.clients6.google.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def is_project_valid(self, as_client: httpx.AsyncClient, project_identifier: str) -> Tuple[bool, CacBrand]:
        """
            Returns if the given project identifier is valid.
            The project identifier can be a project ID or a project number.
        """
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "POST",
            data_type = "json", # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None
            require_key = "firebase_console", # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = "/v1/analytics:checkAccess"

        params = {
            "alt": "json"
        }

        post_data = {
            "entityKey": {},
            "firebaseProjectId": project_identifier
        }

        req = await self._query(endpoint.name, as_client, base_url, params=params, data=post_data)

        return req.status_code != 404