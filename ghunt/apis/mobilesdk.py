from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.mobilesdk import MobileSDKDynamicConfig

import httpx

from typing import *
import inspect
import json


class MobileSDKPaHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "mobilesdk-pa.clients6.google.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def test_iam_permissions(self, as_client: httpx.AsyncClient, project_identifier: str, permissions: List[str]) -> Tuple[bool, List[str]]:
        """
            Returns the permissions you have against a project.
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

        base_url = f"/v1/projects/{project_identifier}:testIamPermissions"

        post_data = {
            "permissions": permissions
        }

        req = await self._query(endpoint.name, as_client, base_url, data=post_data)

        # Parsing
        data = json.loads(req.text)

        if "error" in data:
            return False, []

        return True, data.get("permissions", [])

    async def get_webapp_dynamic_config(self, as_client: httpx.AsyncClient, app_id: str) -> Tuple[bool, MobileSDKDynamicConfig]:
        """
            Returns the dynamic config of a web app.
            
            :param app_id: The app id
        """
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None,
            key_origin="firebase_console", # key name, or None
            # require_key = "firebase_console", # key name, or None
        )
        self._load_endpoint(endpoint)

        # Android OAuth fields
        self.api_name = "mobilesdk"
        self.package_name = "com.android.chrome"
        self.scopes = [
                        "https://www.googleapis.com/auth/cloud-platform",
                        "https://www.googleapis.com/auth/cloud-platform.read-only",
                        "https://www.googleapis.com/auth/firebase",
                        "https://www.googleapis.com/auth/firebase.readonly"
                    ]

        base_url = f"/v1/config/webApps/{app_id}/dynamicConfig"

        req = await self._query(endpoint.name, as_client, base_url)

        # Parsing
        data = json.loads(req.text)

        dynamic_config = MobileSDKDynamicConfig()
        if "error" in data:
            return False, dynamic_config
        
        dynamic_config._scrape(data)

        return True, dynamic_config