from pathlib import Path
import hashlib
from typing import *
import json
from copy import deepcopy

import httpx

from ghunt import globals as gb


class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text: str):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        gprint(text, end='\r')

    def clear(self):
    	gprint(" " * self.max_len, end="\r")

def gprint(*args, **kwargs) -> None:
    if not gb.config.silent_mode:
        print(*args, **kwargs)

def within_docker() -> bool:
    return Path('/.dockerenv').is_file()

def gen_sapisidhash(timestamp: str, sapisid: str, origin: str) -> str:
    return hashlib.sha1(' '.join([timestamp, sapisid, origin]).encode()).hexdigest()

def extract_set_cookies(req: httpx.Response) -> Dict[str, str]:
    return {pair[0]:''.join(pair[1:]) for x in req.headers.get_list("set-cookie") if (pair := x.split(";")[0].split("="))}

def inject_osid(cookies: Dict[str, str], osids: Dict[str, str], service: str) -> Dict[str, str]:
    cookies_with_osid = deepcopy(cookies)
    cookies_with_osid["OSID"] = osids[service]
    return cookies_with_osid