from ghunt.errors import GHuntCorruptedHeadersError
from ghunt.helpers.knowledge import get_origin_of_key, get_api_key
from ghunt.objects.base import GHuntCreds, SmartObj
from ghunt.helpers.utils import *
from ghunt.errors import *
from ghunt.helpers.auth import *

import httpx
import asyncio

from datetime import datetime, timezone
from typing import *
from dataclasses import dataclass


# APIs objects

@dataclass
class EndpointConfig(SmartObj):
    def __init__(self, 
        name: str="",
        headers: Dict[str, str] = {},
        cookies: Dict[str, str] = {},
        ext_metadata: Dict[str, Dict[str, str]] = {},
        verb: str = "",
        data_type: str|None = None,
        authentication_mode: str|None = None,
        require_key: str | None = None,
        key_origin: str | None = None,
        _computed_headers: Dict[str, str] = {},
        _computed_cookies: Dict[str, str] = {}
    ):
        self.name = name
        self.headers = headers
        self.cookies = cookies
        self.ext_metadata = ext_metadata
        self.verb = verb
        self.data_type = data_type
        self.authentication_mode = authentication_mode
        self.require_key = require_key
        self.key_origin = key_origin
        self._computed_headers = _computed_headers
        self._computed_cookies = _computed_cookies

class GAPI(SmartObj):
    def __init__(self):
        self.api_name: str = ""
        self.package_name: str = ""
        self.scopes: List[str] = []

        self.hostname: str = ""
        self.scheme: str = ""
        self.loaded_endpoints: Dict[str, EndpointConfig] = {}
        self.creds: GHuntCreds = None
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.gen_token_lock: asyncio.Lock = None

    def _load_api(self, creds: GHuntCreds, headers: Dict[str, str]):
        if not creds.are_creds_loaded():
            raise GHuntInsufficientCreds(f"This API requires a loaded GHuntCreds object, but it is not.")

        if not is_headers_syntax_good(headers):
            raise GHuntCorruptedHeadersError(f"The provided headers when loading the endpoint seems corrupted, please check it : {headers}")

        self.creds = creds
        self.headers = headers

    def _load_endpoint(self, endpoint: EndpointConfig):
        if endpoint.name in self.loaded_endpoints:
            return

        headers = {**endpoint.headers, **self.headers}

        if endpoint.authentication_mode == "oauth":
            self.gen_token_lock = asyncio.Lock()

        cookies = {}
        if endpoint.authentication_mode in ["sapisidhash", "cookies_only"]:
            if not (cookies := self.creds.cookies):
                raise GHuntInsufficientCreds(f"This endpoint requires the cookies in the GHuntCreds object, but they aren't loaded.")

        if (key_name := endpoint.require_key):
            if not (api_key := get_api_key(key_name)):
                raise GHuntInsufficientCreds(f"This endpoint requires the {key_name} API key in the GHuntCreds object, but it isn't loaded.")
            if not endpoint.key_origin:
                endpoint.key_origin = get_origin_of_key(key_name)
            headers = {**headers, "X-Goog-Api-Key": api_key, **headers, "Origin": endpoint.key_origin, "Referer": endpoint.key_origin}

        if endpoint.authentication_mode == "sapisidhash":
            if not (sapisidhash := cookies.get("SAPISID")):
                raise GHuntInsufficientCreds(f"This endpoint requires the SAPISID cookie in the GHuntCreds object, but it isn't loaded.")

            headers = {**headers, "Authorization": f"SAPISIDHASH {gen_sapisidhash(sapisidhash, endpoint.key_origin)}"}

        # https://github.com/googleapis/googleapis/blob/f8a290120b3a67e652742a221f73778626dc3081/google/api/context.proto#L43
        for ext_type,ext_value in endpoint.ext_metadata.items():
            ext_bin_headers = {f"X-Goog-Ext-{k}-{ext_type.title()}":v for k,v in ext_value.items()}
            headers = {**headers, **ext_bin_headers}
        
        if not is_headers_syntax_good(headers):
            raise GHuntCorruptedHeadersError(f"The provided headers when loading the endpoint seems corrupted, please check it : {headers}")

        endpoint._computed_headers = headers
        endpoint._computed_cookies = cookies
        self.loaded_endpoints[endpoint.name] = endpoint

    async def _check_and_gen_authorization_token(self, as_client: httpx.AsyncClient, creds: GHuntCreds):
        async with self.gen_token_lock:
            present = False
            if self.api_name in creds.android.authorization_tokens:
                present = True
                token = creds.android.authorization_tokens[self.api_name]["token"]
                expiry_date = datetime.utcfromtimestamp(creds.android.authorization_tokens[self.api_name]["expiry"]).replace(tzinfo=timezone.utc)

            # If there are no registered authorization token for the current API, or if the token has expired
            if (not self.api_name in creds.android.authorization_tokens) or (present and datetime.now(timezone.utc) > expiry_date):
                token, _, expiry_timestamp = await android_oauth_app(as_client, creds.android.master_token, self.package_name, self.scopes)
                creds.android.authorization_tokens[self.api_name] = {
                    "token": token,
                    "expiry": expiry_timestamp
                }
                creds.save_creds(silent=True)
                gb.rc.print(f"\n[+] New token for {self.api_name} has been generated", style="italic")
            return token

    async def _query(self, endpoint_name: str, as_client: httpx.AsyncClient, base_url: str, params: Dict[str, Any]={}, data: Any=None) -> httpx.Response:
        endpoint = self.loaded_endpoints[endpoint_name]
        headers = endpoint._computed_headers
        if endpoint.authentication_mode == "oauth":
            token = await self._check_and_gen_authorization_token(as_client, self.creds)
            headers = {**headers, "Authorization": f"OAuth {token}"}

        if endpoint.verb == "GET":
            req = await as_client.get(f"{self.scheme}://{self.hostname}{base_url}",
                params=params, headers=headers, cookies=endpoint._computed_cookies)
        elif endpoint.verb == "POST":
            if endpoint.data_type == "data":
                req = await as_client.post(f"{self.scheme}://{self.hostname}{base_url}",
                    params=params, data=data, headers=headers, cookies=endpoint._computed_cookies)
            elif endpoint.data_type == "json":
                req = await as_client.post(f"{self.scheme}://{self.hostname}{base_url}",
                    params=params, json=data, headers=headers, cookies=endpoint._computed_cookies)
            else:
                raise GHuntUnknownRequestDataTypeError(f"The provided data type {endpoint.data_type} wasn't recognized by GHunt.")
        else:
            raise GHuntUnknownVerbError(f"The provided verb {endpoint.verb} wasn't recognized by GHunt.")

        return req
    
# Others

class Parser(SmartObj):
    """
        The class that is used to initialize every parser class.
        It will automatically manage the __slots__ attribute.
    """
    pass