from ghunt.objects.apis import GAPI
from ghunt.objects.base import GHuntCreds
from ghunt import globals as gb
from ghunt.protos.playgatewaypa.search_player_pb2 import PlayerSearchProto
from ghunt.protos.playgatewaypa.search_player_results_pb2 import PlayerSearchResultsProto
from ghunt.protos.playgatewaypa.get_player_pb2 import GetPlayerProto
from ghunt.protos.playgatewaypa.get_player_response_pb2 import GetPlayerResponseProto
from ghunt.parsers.playgateway import PlayerSearchResults
from ghunt.parsers.playgateway import PlayerProfile

import httpx

from typing import *
from struct import pack
import inspect


class PlayGatewayPaGrpc(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()

        # Android OAuth fields
        self.api_name = "playgames"
        self.package_name = "com.google.android.play.games"
        self.scopes = [
            "https://www.googleapis.com/auth/games.firstparty",
            "https://www.googleapis.com/auth/googleplay"
        ]

        if not headers:
            headers = gb.config.android_headers
            headers["User-Agent"] = headers["User-Agent"].format(self.package_name)

        headers = {**headers, **{
            "Content-Type": "application/grpc",
            "Te": "trailers"
        }}

        # Normal fields

        self.hostname = "playgateway-pa.googleapis.com"
        self.scheme = "https"

        self.authentication_mode = "oauth" # sapisidhash, cookies_only, oauth or None
        self.require_key = None # key name, or None

        self._load_api(creds, headers)

    async def search_player(self, as_client: httpx.AsyncClient, query: str) -> PlayerSearchResults:
        endpoint_name = inspect.currentframe().f_code.co_name

        verb = "POST"
        base_url = "/play.gateway.adapter.interplay.v1.PlayGatewayInterplayService/GetPage"
        data_type = "data"

        ext_metadata = {
            "bin": {
                "158709649": "CggaBgj22K2aARo4EgoI+aKnlZf996E/GhcQHhoPUkQyQS4yMTEwMDEuMDAyIgIxMToICgZJZ0pHVWdCB1BpeGVsIDU",
                "173715354": "CgEx"
            }
        }

        player_search = PlayerSearchProto()
        player_search.search_form.query.text = query
        payload = player_search.SerializeToString()

        prefix = bytes(1) + pack(">i", len(payload))
        data = prefix + payload

        self._load_endpoint(endpoint_name, {}, ext_metadata)
        req = await self._query(as_client, verb, endpoint_name, base_url, None, data, data_type)

        # Parsing
        player_search_results = PlayerSearchResultsProto()
        player_search_results.ParseFromString(req.content[5:])

        parser = PlayerSearchResults()
        parser._scrape(player_search_results)

        return parser

    async def get_player_stats(self, as_client: httpx.AsyncClient, player_id: str) -> PlayerProfile:
        """
            This endpoint client isn't finished, it is only used to get total played applications & achievements count.
            To get all the details about a player, please use get_player method of PlayGames (HTTP API).
        """

        endpoint_name = inspect.currentframe().f_code.co_name

        verb = "POST"
        base_url = "/play.gateway.adapter.interplay.v1.PlayGatewayInterplayService/GetPage"
        data_type = "data"

        ext_metadata = {
            "bin": {
                "158709649": "CggaBgj22K2aARo4EgoI+aKnlZf996E/GhcQHhoPUkQyQS4yMTEwMDEuMDAyIgIxMToICgZJZ0pHVWdCB1BpeGVsIDU",
                "173715354": "CgEx"
            }
        }

        player_profile = GetPlayerProto()
        player_profile.form.query.id = player_id
        payload = player_profile.SerializeToString()

        prefix = bytes(1) + pack(">i", len(payload))
        data = prefix + payload

        self._load_endpoint(endpoint_name, {}, ext_metadata)
        req = await self._query(as_client, verb, endpoint_name, base_url, None, data, data_type)

        # Parsing
        player_profile = GetPlayerResponseProto()
        player_profile.ParseFromString(req.content[5:])

        parser = PlayerProfile()
        parser._scrape(player_profile)

        return parser