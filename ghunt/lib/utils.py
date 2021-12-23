from pathlib import Path
from PIL import Image
import hashlib
from typing import *
from time import time
from copy import deepcopy

import httpx
import imagehash
from io import BytesIO

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

async def get_image_flathash(as_client: httpx.AsyncClient, image_url: str):
    req = await as_client.get(image_url)
    img = Image.open(BytesIO(req.content))
    flathash = imagehash.average_hash(img)
    return flathash

async def is_default_profile_pic(as_client: httpx.AsyncClient, image_url: str):
    flathash = await get_image_flathash(as_client, image_url)
    if flathash - imagehash.hex_to_flathash("000018183c3c0000", 8) < 10 :
        return True
    return False