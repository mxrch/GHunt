from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.playgames import PlayedGames, PlayerAchievements, PlayerProfile

import httpx

from typing import *
import inspect
import json


class PlayGames(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        # Android OAuth fields
        self.api_name = "playgames"
        self.package_name = "com.google.android.play.games"
        self.scopes = [
            "https://www.googleapis.com/auth/games.firstparty",
            "https://www.googleapis.com/auth/googleplay"
        ]
        
        self.hostname = "www.googleapis.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def get_profile(self, as_client: httpx.AsyncClient, player_id: str) -> Tuple[bool, PlayerProfile]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/games/v1whitelisted/players/{player_id}"

        req = await self._query(endpoint.name, as_client, base_url)

        # Parsing
        data = json.loads(req.text)
        player_profile = PlayerProfile()
        if not "displayPlayer" in data:
            return False, player_profile

        player_profile._scrape(data["displayPlayer"])
        player_profile.id = player_id

        return True, player_profile

    async def get_played_games(self, as_client: httpx.AsyncClient, player_id: str, page_token: str="") -> Tuple[bool, str, PlayedGames]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/games/v1whitelisted/players/{player_id}/applications/played"

        params = {}
        if page_token:
            params = {"pageToken": page_token}

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        played_games = PlayedGames()
        if not "items" in data:
            return False, "", played_games

        next_page_token = data.get("nextPageToken", "")

        played_games._scrape(data["items"])

        return True, next_page_token, played_games

    async def get_achievements(self, as_client: httpx.AsyncClient, player_id: str, page_token: str="") -> Tuple[bool, str, PlayerAchievements]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "POST",
            data_type = "json", # json, data or None
            authentication_mode = "oauth", # sapisidhash, cookies_only, oauth or None
            require_key = None, # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/games/v1whitelisted/players/{player_id}/achievements"

        params = {
            "state": "UNLOCKED",
            "returnDefinitions": True,
            "sortOrder": "RECENT_FIRST"
        }

        if page_token:
            params["pageToken"] = page_token

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)
        achievements = PlayerAchievements()
        if not "items" in data:
            return False, "", achievements
        
        next_page_token = ""
        if "nextPageToken" in data:
            next_page_token = data["nextPageToken"]

        achievements._scrape(data)

        return True, next_page_token, achievements