from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.geolocate import GeolocationResponse

import httpx

from typing import *
import inspect
import json


class GeolocationHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "www.googleapis.com"
        self.scheme = "https"

        self.authentication_mode = None # sapisidhash, cookies_only, oauth or None
        self.require_key = "geolocation" # key name, or None

        self._load_api(creds, headers)

    async def geolocate(self, as_client: httpx.AsyncClient, bssid: str, body: dict) -> Tuple[bool, GeolocationResponse]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "POST",
            data_type = "json", # json, data or None
            authentication_mode = None, # sapisidhash, cookies_only, oauth or None
            require_key = "geolocation", # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/geolocation/v1/geolocate"

        if bssid:
            payload = {
                "considerIp": False,
                "wifiAccessPoints": [
                    {
                        "macAddress": "00:25:9c:cf:1c:ad"
                    },
                    {
                        "macAddress": bssid
                    },
                ]
            }
        else:
            payload = body

        req = await self._query(endpoint.name, as_client, base_url, data=payload)

        # Parsing
        data = json.loads(req.text)

        resp = GeolocationResponse()
        if "error" in data:
            return False, resp
        
        resp._scrape(data)

        return True, resp