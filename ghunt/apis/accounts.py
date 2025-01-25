from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig

import httpx

from typing import *
import inspect


class Accounts(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        # Android OAuth fields
        self.api_name = "chrome"
        self.package_name = "com.android.chrome"
        self.scopes = [
            "https://www.google.com/accounts/OAuthLogin"
        ]
        
        self.hostname = "accounts.google.com"
        self.scheme = "https"

        self.authentication_mode = "oauth" # sapisidhash, cookies_only, oauth or None
        self.require_key = None # key name, or None

        self._load_api(creds, headers)

    async def OAuthLogin(self, as_client: httpx.AsyncClient) -> str:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
            key_origin = None
        )
        self._load_endpoint(endpoint)

        base_url = f"/OAuthLogin"
        params = {
            "source": "ChromiumBrowser",
            "issueuberauth": 1
        }

        req = await self._query(endpoint.name, as_client, base_url, params)

        # Parsing
        uber_auth = req.text

        return True, uber_auth