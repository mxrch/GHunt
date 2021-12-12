from pathlib import Path
import hashlib
from typing import *
from time import time
from copy import deepcopy

import httpx

from ghunt import globals as gb


def gprint(*args, **kwargs) -> None:
    if not gb.config.silent_mode:
        print(*args, **kwargs)

def within_docker() -> bool:
    return Path('/.dockerenv').is_file()

def gen_sapisidhash(sapisid: str, origin: str, timestamp: str = str(int(time()))) -> str:
    return f"{timestamp}_{hashlib.sha1(' '.join([timestamp, sapisid, origin]).encode()).hexdigest()}"

def extract_set_cookies(req: httpx.Response) -> Dict[str, str]:
    return {pair[0]:''.join(pair[1:]) for x in req.headers.get_list("set-cookie") if (pair := x.split(";")[0].split("="))}

def inject_osid(cookies: Dict[str, str], osids: Dict[str, str], service: str) -> Dict[str, str]:
    cookies_with_osid = deepcopy(cookies)
    cookies_with_osid["OSID"] = osids[service]
    return cookies_with_osid
    
def is_headers_syntax_good(headers: dict[str, str]) -> bool:
    try:
        httpx.Headers(headers)
        return True
    except:
        return False
