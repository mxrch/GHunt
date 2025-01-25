from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.drive import DriveCommentList, DriveFile, DriveChildList
from ghunt.knowledge import drive as drive_knowledge

import httpx

from typing import *
import inspect
import json


class DriveHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        # Android OAuth fields
        self.api_name = "drive"
        self.package_name = "com.google.android.apps.docs"
        self.scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file"
        ]

        self.hostname = "www.googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def get_file(self, as_client: httpx.AsyncClient, file_id: str) -> Tuple[bool, DriveFile]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/drive/v2internal/files/{file_id}"

        params = {
            "fields": ','.join(drive_knowledge.request_fields),
            "supportsAllDrives": True
        }

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        drive_file = DriveFile()
        if "error" in data:
            return False, drive_file

        drive_file._scrape(data)

        return True, drive_file

    async def get_comments(self, as_client: httpx.AsyncClient, file_id: str, page_token: str="") -> Tuple[bool, str, DriveCommentList]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/drive/v2internal/files/{file_id}/comments"

        params = {
            "supportsAllDrives": True,
            "maxResults": 100
        }

        if page_token:
            params["pageToken"] = page_token

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        drive_comments = DriveCommentList()
        if "error" in data:
            return False, "", drive_comments

        next_page_token = data.get("nextPageToken", "")

        drive_comments._scrape(data)

        return True, next_page_token, drive_comments

    async def get_childs(self, as_client: httpx.AsyncClient, file_id: str, page_token: str="") -> Tuple[bool, str, DriveChildList]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/drive/v2internal/files/{file_id}/children"

        params = {
            "supportsAllDrives": True,
            "maxResults": 1000
        }

        if page_token:
            params["pageToken"] = page_token

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        drive_childs = DriveChildList()
        if "error" in data:
            return False, "", drive_childs

        next_page_token = data.get("nextPageToken", "")

        drive_childs._scrape(data)

        return True, next_page_token, drive_childs