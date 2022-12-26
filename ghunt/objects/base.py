import logging
import pathlib
from typing import *
from pathlib import Path
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime
import base64

from autoslot import Slots

from ghunt import globals as gb


class SmartObj(Slots):
    pass

class AndroidCreds(SmartObj):
    def __init__(self) -> None:
        self.master_token: str = ""
        self.authorization_tokens: Dict = {}

class GHuntCreds(SmartObj):
    """
        This object stores all the needed credentials that GHunt uses,
        such as cookies, OSIDs, keys and tokens.
    """
    
    def __init__(self, creds_path: str = "") -> None:
        self.cookies: Dict[str, str] = {}
        self.osids: Dict[str, str] = {}
        self.android: AndroidCreds = AndroidCreds()
        # if not creds_path:
        #     cwd_path = Path().home()
        #     ghunt_folder = pathlib.Path(__file__).parent.resolve()
        #     # if not ghunt_folder.is_dir():
        #     #     ghunt_folder.mkdir(parents=True, exist_ok=True)
        #     creds_path = ghunt_folder / "creds.m"
        # print('creds_path:'+str(creds_path))
        # self.creds_path: str = creds_path

    def are_creds_loaded(self) -> bool:
        return all([self.cookies, self.osids, self.android.master_token])

    def load_creds(self, silent=False) -> None:
        """Loads cookies, OSIDs and tokens if they exist"""
        # if Path(self.creds_path).is_file():
        try:
            # with open(self.creds_path, "r", encoding="utf-8") as f:
            #     raw = f.read()
            data = json.loads(base64.b64decode('ewogICJjb29raWVzIjogewogICAgIkFQSVNJRCI6ICJzZkVrYnlNZS1sekMwOFpuL0FoZ1FXZ3dGc1RhQWR4WDhTIiwKICAgICJIU0lEIjogIkFMNHNpeWx1Sllqam9KUkRLIiwKICAgICJMU0lEIjogIm8uY2FsZW5kYXIuZ29vZ2xlLmNvbXxvLmNvbnNvbGUuY2xvdWQuZ29vZ2xlLmNvbXxvLmdyb3Vwcy5nb29nbGUuY29tfG8ubWFpbC5nb29nbGUuY29tfG8ubWVldC5nb29nbGUuY29tfG8ubXlhY2NvdW50Lmdvb2dsZS5jb218by5waG90b3MuZ29vZ2xlLmNvbXxzLkFVfHMuYmxvZ2dlcnxzLnlvdXR1YmU6U0FoRVZvVXVLaGFnc3BkN2xzYkhJZVI4R3ZMU0laNXNKOW5NUnVaX2NhTXlqVUtELWFKVlhVMEdaZlNISUZWYXdFRmtLZy4iLAogICAgIlNBUElTSUQiOiAiNjlwUzNLNHVpT1JCbHdPTi9BaUhjU0c5OUNRWnVyWlh0UCIsCiAgICAiU0lEIjogIlNBaEVWaVRWc2g0VWFjWDMwV1hqdElBLU53djNEWURPSHJzaTQ1Vkd6SVpaUjlTWDdLaHpYVEpmaDBDeGdhQjBXRGFCdXcuIiwKICAgICJTU0lEIjogIkFvMVNFQk0yZmlIZzJ1QWJWIiwKICAgICJfX1NlY3VyZS0zUFNJRCI6ICJTQWhFVmlUVnNoNFVhY1gzMFdYanRJQS1Od3YzRFlET0hyc2k0NVZHeklaWlI5U1hac3ZWSTRJWW1WN2xwQ3pwWHgwVmNRLiIKICB9LAogICJvc2lkcyI6IHsKICAgICJjbG91ZGNvbnNvbGUiOiAiU0FoRVZtS01ySUE4NG1MMTlkRklGcTlPTTVwT0dzNTVsS3cwQVFIUEtSOVFUcDZZSEJtLTNUVVRGXzFqVzAtZlFQUGRaQS4iLAogICAgImNsIjogIlNBaEVWcFVUT1RzbEVBYlFycVB5ZzAxTk9qOHY5SFlYX2NXZ0JpRTVOcG1YNHEwV1Z1Qjh3ZWozNDBiU3lJTjVpdnFlR0EuIgogIH0sCiAgImFuZHJvaWQiOiB7CiAgICAibWFzdGVyX3Rva2VuIjogImFhc19ldC9BS3BwSU5ianNiRC1XUnJURGoxREJJdmtLU2tDdVVvUWU0ZG50bU01SmFEc1RlNHRCbHNZX3MyUE53US1YdmFhSmlldVlZRHZQZUYtbXYweWJnMjZ3UE9qNVVSZWJ3ekVRQWgwLXJ3T3kxY2d4LXROUjRxbWtTLWhlbWZfNWx0VDhSa3ljdzRmeG00RlFaVTc4NkR6YllTUl96VU1kd1A1V0pVYWdQLWowZU1pblVPUW5uZEdaQ0U3LVNpWUgxcjI3SEtpaG1NaEwzVkRkMno1emw1U2daYz0iLAogICAgImF1dGhvcml6YXRpb25fdG9rZW5zIjogewogICAgICAicGxheWdhbWVzIjogewogICAgICAgICJ0b2tlbiI6ICJ5YTI5LmEwQWVUTTFpY080MTZQbm1PcFB4a2ZsZVQ1cEYzZHcxY3hRS1YxcGYwY05ycUhERmFTYzV0SThKVWdiR1RBQVlwc1JJLVJkbk95ZDhuY3ZOSlNGZG44VmpSZkVoRF9Sc1Q4RUVzOGRldl9zNGxfMWRnX2hpNU0xb3RjWDlLVU9nME1CTjNRclZZVHZ6d0RPTjBBTXltWXVOYk4yU1UyWlRyY3QtOUJCXzVfVW9pNXhoZ3gtUVYzaWRTbHpSYl9DZ2JuZUlpa0EzSEYtY0dDQ0ZqUkVkVEt5QUJKRC1acDlFUHpqQnBRbXJyeEt1eW1iTFRhQWlHcHRsUkxZMUVQd2piNDZpQW5XMEFUalRKYmlVZ0pEcXJBa1Q4Ujk0V3ZzYnBiRF9mcE9tbGdxenRsTkZQa19aSTl2czFUXzZlaWFDZ1lLQWMwU0FSRVNGUUhXdFdPbVZhYXI5MmM5TGdmZlU1UE1pYkJ5SEEwMzIzIiwKICAgICAgICAiZXhwaXJ5IjogMTY3MDk5NTY5MgogICAgICB9LAogICAgICAiZHJpdmUiOiB7CiAgICAgICAgInRva2VuIjogInlhMjkuYTBBZVRNMWlkcXVVN2dPSzRXaEZIN2o2bVR1M1ljdUQ5Rml0ZHJySkRMaVZfdkdsdUJadVlIX3hrYUNVVDhGcjZ6cEtqV2JKN0FDT3VGeUg5ZVpHS3pLeDZsMHBJaTlWZm9VMGtpZVNKeHZnOGJIQTZ2YmdsQ2Z0MjZ2LU1jNGRoR1ZaUUpGMkI4Qno4b0U2c3ZZcVZkNlQ2bllmenBiZkFoQ1VYZkhMaTNKbF9KZmZHNVhoamt3cFFCUGtFdjJjZDFwR1JTMEl5cU84OFMyTU5qR2tmSVp3SGVlM3VuUkpaUWRqbC1fZ2RSWHhqRWpZZjZ5aFpoZWQ3TzVLLWRlbmQ5Rkk0MTg2WXVrbjZubG50TTFxVEpfd1QzUVgwSDVaVkVXTTByOXlJQl8xTWdmZS1nckd1UmtMbkhWZ2FDZ1lLQWFRU0FSRVNGUUhXdFdPbWVVSzFLd0FIMXFpUkgwdDBLc1BLcUEwMzIxIiwKICAgICAgICAiZXhwaXJ5IjogMTY3MDQ1MTA0MwogICAgICB9CiAgICB9CiAgfQp9').decode())
            # print('data:'+data)

            self.cookies = data["cookies"]
            self.osids = data["osids"]

            self.android.master_token = data["android"]["master_token"]
            self.android.authorization_tokens = data["android"]["authorization_tokens"]

            if not silent:
                gb.rc.print("[+] Authenticated !", style="sea_green3")
        except Exception as e:
            print(e)
            if not silent:
                print("[-] Stored cookies are corrupted\n")
        # else:
        #     if not silent:
        #         print("[-] No stored cookies found\n")

    def save_creds(self, silent=False):
        """Save cookies, OSIDs and tokens to the specified file."""
        data = {
            "cookies": self.cookies,
            "osids": self.osids,
            "android": {
                "master_token": self.android.master_token,
                "authorization_tokens": self.android.authorization_tokens
            }
        }

        # with open(self.creds_path, "w", encoding="utf-8") as f:
        #     f.write(base64.b64encode(json.dumps(data, indent=2).encode()).decode())

        if not silent:
            print(f"\n[+] Creds have been saved in {self.creds_path} !")

### Maps

class Position(SmartObj):
    def __init__(self):
        self.latitude: float = 0.0
        self.longitude: float = 0.0

class MapsGuidedAnswer(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.question: str = ""
        self.answer: str = ""

class MapsLocation(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.address: str = ""
        self.position: Position = Position()
        self.tags: List[str] = []
        self.types: List[str] = []
        self.cost: int = 0 # 1-4

class MapsReview(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.comment: str = ""
        self.rating: int = 0
        self.location: MapsLocation = MapsLocation()
        self.guided_answers: List[MapsGuidedAnswer] = []
        self.approximative_date: relativedelta = None

class MapsPhoto(SmartObj):
    def __init__(self):
        self.id: str = ""
        self.url: str = ""
        self.location: MapsLocation = MapsLocation()
        self.approximative_date: relativedelta = None
        self.exact_date: datetime = None

### Drive
class DriveExtractedUser(SmartObj):
    def __init__(self):
        self.gaia_id: str = ""
        self.name: str = ""
        self.email_address: str = ""
        self.role: str = ""
        self.is_last_modifying_user: bool = False