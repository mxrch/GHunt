from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.digitalassetslinks import DalStatements

import httpx

from typing import *
import inspect
import json


class DigitalAssetsLinksHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "digitalassetlinks.googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def list_statements(self, as_client: httpx.AsyncClient, website: str="",
                        android_package_name: str="", android_cert_fingerprint: str="") -> Tuple[bool, DalStatements]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = None, # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = "/v1/statements:list"

        # Inputs checks
        if website and (android_package_name or android_cert_fingerprint):
            raise GHuntParamsInputError(f"[DigitalAssetsLinks API list statements] website and {android_package_name if android_package_name else android_cert_fingerprint} can't be both put at the same time.")
        elif not website and not (android_package_name and android_cert_fingerprint):
            raise GHuntParamsInputError("[DigitalAssetsLinks API list statements] Please , android_package_name and android_cert_ingerprint.")
        elif not (website or android_package_name or android_cert_fingerprint):
            raise GHuntParamsInputError("[DigitalAssetsLinks API list statements] Please choose at least one parameter between website, android_package_name and android_cert_ingerprint.")

        params = {}
        if website:
            params["source.web.site"] = website
        if android_package_name:
            params["source.androidApp.packageName"] = android_package_name
        if android_cert_fingerprint:
            params["source.androidApp.certificate.sha256Fingerprint"] = android_cert_fingerprint

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)

        statements = DalStatements()
        if "error" in data:
            return False, statements
        
        statements._scrape(data)

        found = bool(statements.statements)
        return found, statements