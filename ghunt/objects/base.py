from typing import *
from pathlib import Path
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime

from ghunt import globals as gb
from ghunt.lib.utils import gprint


class GHuntCreds():
    """
    This object stores all the needed credentials that GHunt uses,
    such as cookies, OSIDs, keys and tokens.
    """
    
    def __init__(
        self,
        cookies: Dict[str, str] = {},
        osids: Dict[str, str] = {},
        tokens: Dict[str, str] = {},
        creds_path: str = ""
    ) -> None:
        self.cookies = cookies
        self.osids = osids
        self.tokens = tokens
        self.creds_path = creds_path if creds_path else gb.config.creds_path

    def are_creds_loaded(self) -> bool:
        return all([self.cookies, self.osids, self.tokens])

    def load_creds(self) -> None:
        """ Returns cookies, OSIDs and tokens if they exist """
        if Path(self.creds_path).is_file():
            try:
                with open(self.creds_path, 'r') as f:
                    out = json.loads(f.read())
                    self.cookies = out["cookies"]
                    self.osids = out["osids"]
                    self.tokens = out["tokens"]
                    gprint("[+] Detected stored cookies")
            except Exception:
                gprint("[-] Stored cookies are corrupted\n")
        else:
            gprint("[-] No stored cookies found\n")

class Position():
    def __init__(self):
        self.latitude: float = 0.0
        self.longitude: float = 0.0

class MapsGuidedAnswer():
    def __init__(self):
        self.id: str = ""
        self.question: str = ""
        self.answer: str = ""

class MapsLocation():
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.address: str = ""
        self.position: Position = Position()
        self.tags: list[str] = []
        self.types: list[str] = []
        self.cost: int = 0 # 1-4

class MapsReview():
    def __init__(self):
        self.id: str = ""
        self.comment: str = ""
        self.rating: int = 0
        self.location: MapsLocation = MapsLocation()
        self.guided_answers: list[MapsGuidedAnswer] = []
        self.approximative_date: relativedelta = None

class MapsPhoto():
    def __init__(self):
        self.id: str = ""
        self.url: str = ""
        self.location: MapsLocation = MapsLocation()
        self.approximative_date: relativedelta = None
        self.exact_date: datetime = None
