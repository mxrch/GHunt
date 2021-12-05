from typing import *
from pathlib import Path
import json

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
        keys: Dict[str, str] = {},
        tokens: Dict[str, str] = {},
        creds_path: str = gb.config.creds_path
    ) -> None:
        self.cookies = cookies
        self.osids = osids
        self.keys = keys
        self.tokens = tokens
        self.creds_path = creds_path

    def are_creds_loaded(self) -> bool:
        return all([self.cookies, self.osids, self.keys, self.tokens])

    def load_creds(self) -> None:
        """ Returns cookies, OSIDs, keys and tokens if they exist """
        if Path(self.creds_path).is_file():
            try:
                with open(self.creds_path, 'r') as f:
                    out = json.loads(f.read())
                    self.cookies = out["cookies"]
                    self.osids = out["osids"]
                    self.keys = out["keys"]
                    self.tokens = out["tokens"]
                    gprint("[+] Detected stored cookies")
            except Exception:
                gprint("[-] Stored cookies are corrupted\n")
        else:
            gprint("[-] No stored cookies found\n")