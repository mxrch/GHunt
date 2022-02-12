from ghunt.errors import GHuntCorruptedHeadersError
from ghunt.lib.knowledge import get_origin_of_key, get_api_key
from ghunt.objects.base import GHuntCreds
from ghunt.lib.utils import gen_sapisidhash, is_headers_syntax_good
from ghunt.errors import *
from ghunt.lib.utils import get_class_name

import httpx


class EndpointConfig():
    def __init__(self, headers: dict[str, str], sapisidhash: str, cookies: str):
        self.headers = headers
        self.sapisidhash = sapisidhash
        self.cookies = cookies

class HttpAPI():
    def _load_api(self, creds: GHuntCreds, headers: dict[str, str]):
        if not creds.are_creds_loaded():
            raise GHuntInsufficientCreds(f"This API requires a loaded GhuntCreds object, but it is not.")

        if not is_headers_syntax_good(headers):
            raise GHuntCorruptedHeadersError(f"The provided headers when loading the endpoint seems corrupted, please check it : {headers}")

        self.key_origin = None
        if (key_name := self.require_key):
            if not get_api_key(key_name):
                raise GHuntInsufficientCreds(f"This API requires the {key_name} API key in the GhuntCreds object, but it isn't loaded.")
            key_origin = get_origin_of_key(key_name)
            self.headers = {**headers, "Origin": key_origin, "Referer": key_origin, "X-Goog-Api-Key": get_api_key(key_name)}
            self.key_origin = key_origin

        self.creds = creds
        self.loaded_endpoints : dict[str, EndpointConfig] = {}

    def _load_endpoint(self, endpoint_name: str, require_sapisidhash: bool, require_cookies: bool):
        if endpoint_name in self.loaded_endpoints:
            return

        if require_sapisidhash:
            if not (sapisidhash := self.creds.cookies.get("SAPISID")):
                raise GHuntInsufficientCreds(f"This endpoint requires the SAPISID cookie in the GhuntCreds object, but it isn't loaded.")
            headers = {**self.headers, "Authorization": f"SAPISIDHASH {gen_sapisidhash(sapisidhash, self.key_origin)}"}
        
        if require_cookies:
            if not self.creds.cookies:
                raise GHuntInsufficientCreds(f"This endpoint requires the cookies in the GhuntCreds object, but they aren't loaded.")

        self.creds = self.creds
        self.loaded_endpoints[endpoint_name] = EndpointConfig(headers, sapisidhash, self.creds.cookies)

    async def _query(self, as_client: httpx.AsyncClient, verb: str, endpoint_name: str, base_url: str, params_template: dict[str, any]) -> httpx.Response:
        endpoint = self.loaded_endpoints[endpoint_name]

        if verb == "GET":
            req = await as_client.get(f"{self.scheme}://{self.hostname}{base_url}",
                params=params_template, headers=endpoint.headers, cookies=endpoint.cookies)
        elif verb == "POST":
            req = await as_client.post(f"{self.scheme}://{self.hostname}{base_url}",
                data=params_template, headers=endpoint.headers, cookies=endpoint.cookies)
        else:
            raise GHuntUnknownVerbError(f"The provided verb {verb} wasn't recognized by GHunt.")

        return req

class Parser():
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