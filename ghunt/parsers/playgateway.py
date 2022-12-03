from typing import *

from ghunt.protos.playgatewaypa.search_player_results_pb2 import PlayerSearchResultsProto
from ghunt.protos.playgatewaypa.get_player_response_pb2 import GetPlayerResponseProto
from ghunt.objects.apis import Parser


class PlayerSearchResult(Parser):
    def __init__(self):
        self.name: str = ""
        self.id: str = ""
        self.avatar_url: str = ""

    def _scrape(self, player_result_data):
        self.name = player_result_data.account.name
        self.id = player_result_data.account.id
        self.avatar_url = player_result_data.avatar.url

class PlayerSearchResults(Parser):
    def __init__(self):
        self.results: List[PlayerSearchResult] = []

    def _scrape(self, proto_results: PlayerSearchResultsProto):
        for player_result_data in proto_results.field1.results.field1.field1.player:
            player_search_result = PlayerSearchResult()
            player_search_result._scrape(player_result_data)
            self.results.append(player_search_result)

class PlayerProfile(Parser):
    """
        This parsing is not complete at all, we only use it
        in GHunt to dump total played games & achievements.
    """
    def __init__(self):
        self.achievements_count: int = 0
        self.played_games_count: int = 0

    def _scrape(self, proto_results: GetPlayerResponseProto):
        for section in proto_results.field1.results.section:
            if section.field3.section_name == "Games":
                self.played_games_count = int(section.counter.number)
            elif section.field3.section_name == "Achievements":
                self.achievements_count = int(section.counter.number)