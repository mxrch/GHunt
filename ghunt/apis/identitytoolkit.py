from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.identitytoolkit import ITKProjectConfig

import httpx

from typing import *
import inspect
import json


class IdentityToolkitHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "www.googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def get_project_config(self, as_client: httpx.AsyncClient, api_key: str) -> Tuple[bool, ITKProjectConfig]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = None, # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = "/identitytoolkit/v3/relyingparty/getProjectConfig"

        params = {
            "key": api_key
        }

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)

        project_config = ITKProjectConfig()
        if "error" in data:
            return False, project_config
        
        project_config._scrape(data)

        return True, project_config