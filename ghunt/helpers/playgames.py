from ghunt.objects.base import GHuntCreds
from ghunt.apis.playgames import PlayGames
from ghunt.apis.playgateway import PlayGatewayPaGrpc
from ghunt.parsers.playgames import Player, PlayerProfile
from ghunt.parsers.playgateway import PlayerSearchResult
from ghunt.objects.utils import TMPrinter

import httpx
from alive_progress import alive_bar

from typing import *


async def get_player(ghunt_creds: GHuntCreds, as_client: httpx.AsyncClient, player_id: str):
    playgames = PlayGames(ghunt_creds)

    tmprinter = TMPrinter()
    tmprinter.out("[~] Getting player profile...")
    is_found, player_profile = await playgames.get_profile(as_client, player_id)
    tmprinter.clear()
    if not is_found or not player_profile.profile_settings.profile_visible:
        return is_found, Player()
    
    playgateway_pa = PlayGatewayPaGrpc(ghunt_creds)
    player_stats = await playgateway_pa.get_player_stats(as_client, player_id)

    with alive_bar(player_stats.played_games_count, title="🚎 Fetching played games...", receipt=False) as bar:
        _, next_page_token, played_games = await playgames.get_played_games(as_client, player_id)
        bar(len(played_games.games))
        while next_page_token:
            _, next_page_token, new_played_games = await playgames.get_played_games(as_client, player_id, next_page_token)
            played_games.games += new_played_games.games
            bar(len(new_played_games.games))

    with alive_bar(player_stats.achievements_count, title="🚎 Fetching achievements...", receipt=False) as bar:
        _, next_page_token, achievements = await playgames.get_achievements(as_client, player_id)
        bar(len(achievements.achievements))
        while next_page_token:
            _, next_page_token, new_achievements = await playgames.get_achievements(as_client, player_id, next_page_token)
            achievements.achievements += new_achievements.achievements
            bar(len(new_achievements.achievements))

    player = Player(player_profile, played_games.games, achievements.achievements)
    return is_found, player

async def search_player(ghunt_creds: GHuntCreds, as_client: httpx.AsyncClient, query: str) -> List[PlayerSearchResult]:
    playgateway_pa = PlayGatewayPaGrpc(ghunt_creds)
    player_search_results = await playgateway_pa.search_player(as_client, query)
    return player_search_results.results

def output(player: Player):
    if not player.profile.profile_settings.profile_visible:
        print("\n[-] Profile is private.")
        return

    print("\n[+] Profile is public !")
    print(f"\n[+] Played to {len(player.played_games)} games")
    print(f"[+] Got {len(player.achievements)} achievements")

    if player.played_games:
        print(f"\n[+] Last played game : {player.profile.last_played_app.app_name} ({player.profile.last_played_app.timestamp_millis} UTC)")

        if player.achievements:
            app_ids_count = {}
            for achievement in player.achievements:
                if (app_id := achievement.app_id) not in app_ids_count:
                    app_ids_count[app_id] = 0
                app_ids_count[app_id] += 1
            app_ids_count = dict(sorted(app_ids_count.items(), key=lambda item: item[1], reverse=True))
            achiv_nb = list(app_ids_count.values())[0]
            target_game = None
            for game in player.played_games:
                if game.game_data.id == list(app_ids_count.keys())[0]:
                    target_game = game
                    break

            print(f"[+] Game with the most achievements : {target_game.game_data.name} ({achiv_nb})")