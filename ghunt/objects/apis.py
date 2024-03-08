from ghunt.errors import GHuntCorruptedHeadersError
from ghunt.helpers.knowledge import get_origin_of_key, get_api_key
from ghunt.objects.base import GHuntCreds, SmartObj
from ghunt.helpers.utils import *
from ghunt.errors import *
from ghunt.helpers.auth import *

import httpx

from datetime import datetime, timezone
from typing import *
import asyncio


# APIs objects

class EndpointConfig(SmartObj):
    def __init__(self, headers: Dict[str, str], cookies: str):
        self.headers = headers
        self.cookies = cookies

class GAPI(SmartObj):
    def __init__(self):
        self.loaded_endpoints: Dict[str, EndpointConfig] = {}
        self.creds: GHuntCreds = None
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.gen_token_lock: asyncio.Semaphore = None

        self.authentication_mode: str = ""
        self.require_key: str = ""
        self.key_origin: str = ""

    def _load_api(self, creds: GHuntCreds, headers: Dict[str, str]):
        if not creds.are_creds_loaded():
            raise GHuntInsufficientCreds(f"This API requires a loaded GHuntCreds object, but it is not.")

        if not is_headers_syntax_good(headers):
            raise GHuntCorruptedHeadersError(f"The provided headers when loading the endpoint seems corrupted, please check it : {headers}")

        if self.authentication_mode == "oauth":
            self.gen_token_lock = asyncio.Semaphore(1)

        cookies = {}
        if self.authentication_mode in ["sapisidhash", "cookies_only"]:
            if not (cookies := creds.cookies):
                raise GHuntInsufficientCreds(f"This endpoint requires the cookies in the GHuntCreds object, but they aren't loaded.")

        if (key_name := self.require_key):
            if not (api_key := get_api_key(key_name)):
                raise GHuntInsufficientCreds(f"This API requires the {key_name} API key in the GHuntCreds object, but it isn't loaded.")
            if not self.key_origin:
                self.key_origin = get_origin_of_key(key_name)
            headers = {**headers, "X-Goog-Api-Key": api_key, **headers, "Origin": self.key_origin, "Referer": self.key_origin}

        if self.authentication_mode == "sapisidhash":
            if not (sapisidhash := creds.cookies.get("SAPISID")):
                raise GHuntInsufficientCreds(f"This endpoint requires the SAPISID cookie in the GHuntCreds object, but it isn't loaded.")

            headers = {**headers, "Authorization": f"SAPISIDHASH {gen_sapisidhash(sapisidhash, self.key_origin)}"}

        self.creds = creds
        self.headers = headers
        self.cookies = cookies

    def _load_endpoint(self, endpoint_name: str,
                        headers: Dict[str, str]={}, ext_metadata: Dict[str, str]={}):
        if endpoint_name in self.loaded_endpoints:
            return

        headers = {**headers, **self.headers}

        # https://github.com/googleapis/googleapis/blob/f8a290120b3a67e652742a221f73778626dc3081/google/api/context.proto#L43
        for ext_type,ext_value in ext_metadata.items():
            ext_bin_headers = {f"X-Goog-Ext-{k}-{ext_type.title()}":v for k,v in ext_value.items()}
            headers = {**headers, **ext_bin_headers}

        if not is_headers_syntax_good(headers):
            raise GHuntCorruptedHeadersError(f"The provided headers when loading the endpoint seems corrupted, please check it : {headers}")

        self.loaded_endpoints[endpoint_name] = EndpointConfig(headers, self.cookies)


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

    async def _query(self, as_client: httpx.AsyncClient, verb: str, endpoint_name: str, base_url: str, params: Dict[str, Any], data: Any, data_type: str) -> httpx.Response:
        endpoint = self.loaded_endpoints[endpoint_name]
        headers = endpoint.headers
        if self.authentication_mode == "oauth":
            token = await self._check_and_gen_authorization_token(as_client, self.creds)
            headers = {**headers, "Authorization": f"OAuth {token}"}

        if verb == "GET":
            req = await as_client.get(f"{self.scheme}://{self.hostname}{base_url}",
                params=params, headers=headers, cookies=endpoint.cookies)
        elif verb == "POST":
            if data_type == "data":
                req = await as_client.post(f"{self.scheme}://{self.hostname}{base_url}",
                    params=params, data=data, headers=headers, cookies=endpoint.cookies)
            elif data_type == "json":
                req = await as_client.post(f"{self.scheme}://{self.hostname}{base_url}",
                    params=params, json=data, headers=headers, cookies=endpoint.cookies)
            else:
                raise GHuntUnknownRequestDataTypeError(f"The provided data type {data_type} wasn't recognized by GHunt.")
        else:
            raise GHuntUnknownVerbError(f"The provided verb {verb} wasn't recognized by GHunt.")

        return req

# Others

class Parser(SmartObj):
    def _merge(self, obj) -> any:
        """Merging two objects of the same class."""

        def recursive_merge(obj1, obj2, module_name: str) -> any:
            directions = [(obj1, obj2), (obj2, obj1)]
            for direction in directions:
                from_obj, target_obj = direction
                for attr_name, attr_value in from_obj.__dict__.items():
                    class_name = get_class_name(attr_value)
                    if class_name.startswith(module_name) and attr_name in target_obj.__dict__:
                        merged_obj = recursive_merge(attr_value, target_obj.__dict__[attr_name], module_name)
                        target_obj.__dict__[attr_name] = merged_obj

                    elif not attr_name in target_obj.__dict__ or \
                        (attr_value and not target_obj.__dict__.get(attr_name)):
                        target_obj.__dict__[attr_name] = attr_value
            return obj1

        class_name = get_class_name(self)
        module_name = self.__module__
        if not get_class_name(obj).startswith(class_name):
            raise GHuntObjectsMergingError("The two objects being merged aren't from the same class.")

        self = recursive_merge(self, obj, module_name)
