from typing import *
from datetime import datetime

from ghunt.objects.apis import Parser


### Profile

class PlayerProfile(Parser):
    def __init__(self):
        self.display_name: str = ""
        self.id: str = ""
        self.avatar_url: str = ""
        self.banner_url_portrait: str = ""
        self.banner_url_landscape: str = ""
        self.gamertag: str = ""
        self.last_played_app: PlayerPlayedApp = PlayerPlayedApp()
        self.profile_settings: PlayerProfileSettings = PlayerProfileSettings()
        self.experience_info: PlayerExperienceInfo = PlayerExperienceInfo()
        self.title: str = ""

    def _scrape(self, player_data: Dict[str, any]):
        self.display_name = player_data.get("playerId")
        self.display_name = player_data.get("displayName")
        self.avatar_url = player_data.get("avatarImageUrl")
        self.banner_url_portrait = player_data.get("bannerUrlPortrait")
        self.banner_url_landscape = player_data.get("bannerUrlLandscape")
        self.gamertag = player_data.get("gamerTag")
        if (last_played_app_data := player_data.get("lastPlayedApp")):
            self.last_played_app._scrape(last_played_app_data)
        if (profile_settings_data := player_data.get("profileSettings")):
            self.profile_settings._scrape(profile_settings_data)
        if (experience_data := player_data.get("experienceInfo")):
            self.experience_info._scrape(experience_data)
        self.title = player_data.get("title")

class PlayerPlayedApp(Parser):
    def __init__(self):
        self.app_id: str = ""
        self.icon_url: str = ""
        self.featured_image_url: str = ""
        self.app_name: str = ""
        self.timestamp_millis: str = ""

    def _scrape(self, played_app_data: Dict[str, any]):
        self.app_id = played_app_data.get("applicationId")
        self.icon_url = played_app_data.get("applicationIconUrl")
        self.featured_image_url = played_app_data.get("featuredImageUrl")
        self.app_name = played_app_data.get("applicationName")
        if (timestamp := played_app_data.get("timeMillis")):
            self.timestamp_millis = datetime.utcfromtimestamp(float(timestamp[:10]))

class PlayerExperienceInfo(Parser):
    def __init__(self):
        self.current_xp: str = ""
        self.last_level_up_timestamp_millis: str = ""
        self.current_level: PlayerLevel = PlayerLevel()
        self.next_level: PlayerLevel = PlayerLevel()
        self.total_unlocked_achievements: int = 0

    def _scrape(self, experience_data: Dict[str, any]):
        self.current_xp = experience_data.get("currentExperiencePoints")
        if (timestamp := experience_data.get("lastLevelUpTimestampMillis")):
            self.last_level_up_timestamp_millis = datetime.utcfromtimestamp(float(timestamp[:10]))
        if (current_level_data := experience_data.get("currentLevel")):
            self.current_level._scrape(current_level_data)
        if (next_level_data := experience_data.get("nextLevel")):
            self.next_level._scrape(next_level_data)
        self.total_unlocked_achievements = experience_data.get("totalUnlockedAchievements")

class PlayerLevel(Parser):
    def __init__(self):
        self.level: int = 0
        self.min_xp: str = ""
        self.max_xp: str = ""

    def _scrape(self, level_data: Dict[str, any]):
        self.level = level_data.get("level")
        self.min_xp = level_data.get("minExperiencePoints")
        self.max_xp = level_data.get("maxExperiencePoints")

class PlayerProfileSettings(Parser):
    def __init__(self):
        self.profile_visible: bool = False

    def _scrape(self, profile_settings_data: Dict[str, any]):
        self.profile_visible = profile_settings_data.get("profileVisible")

### Played Applications

class PlayedGames(Parser):
    def __init__(self):
        self.games: List[PlayGame] = []

    def _scrape(self, games_data: Dict[str, any]):
        for game_data in games_data:
            play_game = PlayGame()
            play_game._scrape(game_data)
            self.games.append(play_game)

class PlayGame(Parser):
    def __init__(self):
        self.game_data: PlayGameData = PlayGameData()
        self.market_data: PlayGameMarketData = PlayGameMarketData()
        self.formatted_last_played_time: str = ""
        self.last_played_time_millis: str = ""
        self.unlocked_achievement_count: int = 0

    def _scrape(self, game_data: Dict[str, any]):
        if (games_data := game_data.get("gamesData")):
            self.game_data._scrape(games_data)
        if (market_data := game_data.get("marketData")):
            self.market_data._scrape(market_data)
        self.formatted_last_played_time = game_data.get("formattedLastPlayedTime")
        if (timestamp := game_data.get("lastPlayedTimeMillis")):
            self.last_played_time_millis = datetime.utcfromtimestamp(float(timestamp[:10]))
        self.unlocked_achievement_count = game_data.get("unlockedAchievementCount")

class PlayGameMarketData(Parser):
    def __init__(self):
        self.instances: List[PlayGameMarketInstance] = []

    def _scrape(self, market_data: Dict[str, any]):
        if (instances_data := market_data.get("instances")):
            for instance_data in instances_data:
                instance = PlayGameMarketInstance()
                instance._scrape(instance_data)
                self.instances.append(instance)

class PlayGameMarketInstance(Parser):
    def __init__(self):
        self.id: str = ""
        self.title: str = ""
        self.description: str = ""
        self.images: List[PlayGameImageAsset] = []
        self.developer_name: str = ""
        self.categories: List[str] = []
        self.formatted_price: str = ""
        self.price_micros: str = ""
        self.badges: List[PlayGameMarketBadge] = []
        self.is_owned: bool = False
        self.enabled_features: List[str] = []
        self.description_snippet: str = ""
        self.rating: PlayGameMarketRating = PlayGameMarketRating()
        self.last_updated_timestamp_millis: str = ""
        self.availability: str = ""

    def _scrape(self, instance_data: Dict[str, any]):
        self.id = instance_data.get("id")
        self.title = instance_data.get("title")
        self.description = instance_data.get("description")
        if (images_data := instance_data.get("images")):
            for image_data in images_data:
                image = PlayGameImageAsset()
                image._scrape(image_data)
                self.images.append(image)
        self.developer_name = instance_data.get("developerName")
        self.categories = instance_data.get("categories", [])
        self.formatted_price = instance_data.get("formattedPrice")
        self.price_micros = instance_data.get("priceMicros")
        if (badges_data := instance_data.get("badges")):
            for badge_data in badges_data:
                badge = PlayGameMarketBadge()
                badge._scrape(badge_data)
                self.badges.append(badge)
        self.is_owned = instance_data.get("isOwned")
        self.enabled_features = instance_data.get("enabledFeatures", [])
        self.description_snippet = instance_data.get("descriptionSnippet")
        if (rating_data := instance_data.get("rating")):
            self.rating._scrape(rating_data)
        if (timestamp := instance_data.get("lastUpdatedTimestampMillis")):
            self.last_updated_timestamp_millis = datetime.utcfromtimestamp(float(timestamp[:10]))
        self.availability = instance_data.get("availability")

class PlayGameMarketRating(Parser):
    def __init__(self):
        self.star_rating: float = 0.0
        self.ratings_count: str = ""

    def _scrape(self, rating_data: Dict[str, any]):
        self.star_rating = rating_data.get("starRating")
        self.ratings_count = rating_data.get("ratingsCount")

class PlayGameMarketBadge(Parser):
    def __init__(self):
        self.badge_type: str = ""
        self.title: str = ""
        self.description: str = ""
        self.images: List[PlayGameImageAsset] = []

    def _scrape(self, badge_data: Dict[str, any]):
        self.badge_type = badge_data.get("badgeType")
        self.title = badge_data.get("title")
        self.description = badge_data.get("description")
        if (images_data := badge_data.get("images")):
            for image_data in images_data:
                image = PlayGameImageAsset()
                image._scrape(image_data)
                self.images.append(image)

class PlayGameData(Parser):
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.author: str = ""
        self.description: str = ""
        self.category: PlayGameCategory = PlayGameCategory()
        self.assets: List[PlayGameImageAsset] = []
        self.instances: List[PlayGameInstance] = []
        self.last_updated_timestamp: str = ""
        self.achievement_count: int = 0,
        self.leaderboard_count: int = 0,
        self.enabled_features: List[str] = []
        self.theme_color: str = ""

    def _scrape(self, game_data: Dict[str, any]):
        self.id = game_data.get("id")
        self.name = game_data.get("name")
        self.author = game_data.get("author")
        self.description = game_data.get("description")
        if (category_data := game_data.get("category")):
            self.category._scrape(category_data)
        if (assets_data := game_data.get("assets")):
            for asset_data in assets_data:
                asset = PlayGameImageAsset()
                asset._scrape(asset_data)
                self.assets.append(asset)
        if (instances_data := game_data.get("instances")):
            for instance_data in instances_data:
                instance = PlayGameInstance()
                instance._scrape(instance_data)
                self.instances.append(instance)
        if (timestamp := game_data.get("lastUpdatedTimestamp")):
            self.last_updated_timestamp = datetime.utcfromtimestamp(float(timestamp[:10]))
        self.achievement_count = game_data.get("achievement_count")
        self.leaderboard_count = game_data.get("leaderboard_count")
        self.enabled_features = game_data.get("enabledFeatures", [])
        self.theme_color = game_data.get("themeColor")

class PlayGameInstance(Parser):
    def __init__(self):
        self.platform_type: str = ""
        self.name: str = ""
        self.turn_based_play: bool = False
        self.realtime_play: bool = False
        self.android_instance: List[PlayGameAndroidInstance] = []
        self.acquisition_uri: str = ""

    def _scrape(self, instance_data: Dict[str, any]):
        self.platform_type = instance_data.get("plateformType")
        self.name = instance_data.get("name")
        self.turn_based_play = instance_data.get("turnBasedPlay")
        self.realtime_play = instance_data.get("realtimePlay")
        if (android_instance_data := instance_data.get("androidInstance")):
            android_instance = PlayGameAndroidInstance()
            android_instance._scrape(android_instance_data)
            self.android_instance.append(android_instance_data)

class PlayGameAndroidInstance(Parser):
    def __init__(self):
        self.package_name: str = ""
        self.enable_piracy_check: bool = False
        self.preferred: bool = False

    def _scrape(self, android_instance_data: Dict[str, any]):
        self.package_name = android_instance_data.get("packageName")
        self.enable_piracy_check = android_instance_data.get("enablePiracyCheck")
        self.preferred = android_instance_data.get("preferred")

class PlayGameImageAsset(Parser):
    def __init__(self):
        self.name: str = ""
        self.width: str = ""
        self.height: str = ""
        self.url: str = ""

    def _scrape(self, image_data: Dict[str, any]):
        self.name = image_data.get("name")
        self.width = image_data.get("width")
        self.height = image_data.get("height")
        self.url = image_data.get("url")

class PlayGameCategory(Parser):
    def __init__(self):
        self.primary: str = ""

    def _scrape(self, category_data: Dict[str, any]):
        self.primary = category_data.get("primary")

### Achievements

class PlayerAchievements(Parser):
    def __init__(self):
        self.achievements: List[PlayerAchievement] = []

    def _scrape(self, achievements_data: Dict[str, any]):
        achievements_defs : List[PlayerAchievementDefinition] = []
        if (achievement_defs_data := achievements_data.get("definitions")):
            for achievement_def_data in achievement_defs_data:
                achievement_def = PlayerAchievementDefinition()
                achievement_def._scrape(achievement_def_data)
                achievements_defs.append(achievement_def)
        if (achievements_items_data := achievements_data.get("items")):
            for achievement_item_data in achievements_items_data:
                achievement = PlayerAchievement()
                achievement._scrape(achievement_item_data)
                for achievement_def in achievements_defs:
                    if achievement_def.id == achievement.id:
                        achievement.definition = achievement_def
                self.achievements.append(achievement)

class PlayerAchievement(Parser):
    def __init__(self):
        self.id: str = ""
        self.achievement_state: str = ""
        self.last_updated_timestamp: datetime = 0
        self.app_id: str = 0
        self.xp: str = ""
        self.definition: PlayerAchievementDefinition = PlayerAchievementDefinition()

    def _scrape(self, achievement_item_data: Dict[str, any]):
        self.id = achievement_item_data.get("id")
        self.achievement_state = achievement_item_data.get("achievementState")
        if (timestamp := achievement_item_data.get("lastUpdatedTimestamp")):
            self.last_updated_timestamp = datetime.utcfromtimestamp(float(timestamp[:10]))
        self.app_id = achievement_item_data.get("application_id")
        self.xp = achievement_item_data.get("experiencePoints")

class PlayerAchievementDefinition(Parser):
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.achievement_type: str = ""
        self.xp: str = ""
        self.revealed_icon_url: str = ""
        self.unlocked_icon_url: str = ""
        self.initial_state: str = ""
        self.is_revealed_icon_url_default: bool = False
        self.is_unlocked_icon_url_default: bool = False
        self.rarity_percent: float = 0.0

    def _scrape(self, achievement_def_data: Dict[str, any]):
        self.id = achievement_def_data.get("id")
        self.name = achievement_def_data.get("name")
        self.description = achievement_def_data.get("description")
        self.achievement_type = achievement_def_data.get("achievementType")
        self.xp = achievement_def_data.get("experiencePoints")
        self.revealed_icon_url = achievement_def_data.get("revealedIconUrl")
        self.unlocked_icon_url = achievement_def_data.get("unlockedIconUrl")
        self.initial_state = achievement_def_data.get("initialState")
        self.is_revealed_icon_url_default = achievement_def_data.get("isRevealedIconUrlDefault")
        self.is_unlocked_icon_url_default = achievement_def_data.get("isUnlockedIconUrlDefault")
        self.rarity_percent = achievement_def_data.get("rarityParcent")

### Global

class Player(Parser):
    def __init__(self, profile: PlayerProfile = PlayerProfile(),
                played_games: List[PlayGame] = [],
                achievements: List[PlayerAchievement] = []):
        self.profile: PlayerProfile = profile
        self.played_games: List[PlayGame] = played_games
        self.achievements: List[PlayerAchievement] = achievements