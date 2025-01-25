from pathlib import Path
from PIL import Image
import hashlib
from typing import *
from time import time
from datetime import datetime, timezone
from dateutil.parser import isoparse
from copy import deepcopy
import jsonpickle
import json
from packaging.version import parse as parse_version

import httpx
import imagehash
from io import BytesIO

from ghunt import globals as gb
from ghunt import version as current_version
from ghunt.lib.httpx import AsyncClient


def get_httpx_client() -> httpx.AsyncClient:
    """
        Returns a customized to better support the needs of GHunt CLI users.
    """
    return AsyncClient(http2=True, timeout=15)
    # return AsyncClient(http2=True, timeout=15, proxies="http://127.0.0.1:8282", verify=False)

def oprint(obj: any) -> str:
    serialized = jsonpickle.encode(obj)
    pretty_output = json.dumps(json.loads(serialized), indent=2)
    print(pretty_output)

def chunkify(lst, n):
    """
        Cut a given list to chunks of n items.
    """
    k, m = divmod(len(lst), n)
    for i in range(n):
        yield lst[i*k+min(i, m):(i+1)*k+min(i+1, m)]

def within_docker() -> bool:
    return Path('/.dockerenv').is_file()

def gen_sapisidhash(sapisid: str, origin: str, timestamp: str = str(int(time()))) -> str:
    return f"{timestamp}_{hashlib.sha1(' '.join([timestamp, sapisid, origin]).encode()).hexdigest()}"

def inject_osid(cookies: Dict[str, str], osids: Dict[str, str], service: str) -> Dict[str, str]:
    cookies_with_osid = deepcopy(cookies)
    cookies_with_osid["OSID"] = osids[service]
    return cookies_with_osid
    
def is_headers_syntax_good(headers: Dict[str, str]) -> bool:
    try:
        httpx.Headers(headers)
        return True
    except:
        return False

async def get_url_image_flathash(as_client: httpx.AsyncClient, image_url: str) -> str:
    req = await as_client.get(image_url)
    img = Image.open(BytesIO(req.content))
    flathash = imagehash.average_hash(img)
    return str(flathash)

async def is_default_profile_pic(as_client: httpx.AsyncClient, image_url: str) -> Tuple[bool, str]:
    """
        Returns a boolean which indicates if the image_url
        is a default profile picture, and the flathash of
        the image.
    """
    flathash = await get_url_image_flathash(as_client, image_url)
    if imagehash.hex_to_flathash(flathash, 8) - imagehash.hex_to_flathash("000018183c3c0000", 8) < 10 :
        return True, str(flathash)
    return False, str(flathash)

def get_class_name(obj) -> str:
        return str(obj).strip("<>").split(" ")[0]

def get_datetime_utc(date_str):
    """Converts ISO to datetime object in UTC"""
    date = isoparse(date_str)
    margin = date.utcoffset()
    return date.replace(tzinfo=timezone.utc) - margin

def ppnb(nb: float|int) -> float:
    """
        Pretty print float number
        Ex: 3.9 -> 3.9
            4.0 -> 4
            4.1 -> 4.1
    """
    try:
        return int(nb) if nb % int(nb) == 0.0 else nb
    except ZeroDivisionError:
        if nb == 0.0:
            return 0
        else:
            return nb

def parse_oauth_flow_response(body: str):
    """
        Correctly format the response sent by android.googleapis.com
        during the Android OAuth2 Login Flow.
    """
    return {sp[0]:'='.join(sp[1:]) for x in body.split("\n") if (sp := x.split("="))}

def humanize_list(array: List[any]):
    """
        Transforms a list to a human sentence.
        Ex : ["reader", "writer", "owner"] -> "reader, writer and owner".
    """
    if len(array) <= 1:
        return ''.join(array)

    final = ""
    for nb, item in enumerate(array):
        if nb == 0:
            final += f"{item}"
        elif nb+1 < len(array):
            final += f", {item}"
        else:
            final += f" and {item}"
    return final

def unicode_patch(txt: str):
    bad_chars = {
        "é": "e",
        "è": "e",
        "ç": "c",
        "à": "a"
    }
    return txt.replace(''.join([*bad_chars.keys()]), ''.join([*bad_chars.values()]))

def show_version():
    new_version, new_metadata = check_new_version()
    print()
    gb.rc.print(f"> GHunt {current_version.metadata.get('version', '')} ({current_version.metadata.get('name', '')}) <".center(53), style="bold")
    print()
    if new_version:
        gb.rc.print(f"🥳 New version {new_metadata.get('version', '')} ({new_metadata.get('name', '')}) is available !", style="bold red")
        gb.rc.print(f"🤗 Run 'pipx upgrade ghunt' to update.", style="bold light_pink3")
    else:
        gb.rc.print("🎉 You are up to date !", style="light_pink3")
        

def check_new_version() -> tuple[bool, dict[str, str]]:
    """
        Checks if there is a new version of GHunt available.
    """
    req = httpx.get("https://raw.githubusercontent.com/mxrch/GHunt/master/ghunt/version.py")
    if req.status_code != 200:
        return False, {}
    
    raw = req.text.strip().removeprefix("metadata = ")
    data = json.loads(raw)
    new_version = data.get("version", "")
    new_name = data.get("name", "")

    if parse_version(new_version) > parse_version(current_version.metadata.get("version", "")):
        return True, {"version": new_version, "name": new_name}
    return False, {}