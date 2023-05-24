from ghunt.helpers.utils import get_httpx_client
from ghunt import globals as gb

import requests, re, waybackpy, argparse, trio, httpx

async def hunt(as_client: httpx.AsyncClient, channel_url: str, json_file: bool=None):
    # later: add a way to change this later
    User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"
    r = requests.get(channel_url)
    matchChannelID = re.search("(https?:\/\/)(www\.)?youtube\.com\/(channel)\/[\w-]+", r.text)
    # later: maybe add a prompt here to ask the user if the channel ID looks valid? and if it doesn't, it can iterate through all the different channel IDs and ask for each one? Also, add error handling if no match found
    channelIDURL = matchChannelID.group(0)
    # later: add a way to let the user
    # later: switch to memento API for access to more archives?
    waybackpy_url_object = waybackpy.Url(channelIDURL, User_Agent)
    nearest_archive_url = waybackpy_url_object.near(year=2019)
    # later: add a way to see if there are any archives at all, and if there are any before Plus IDs were removed?
    rArchived = requests.get(nearest_archive_url)
    # later: add error handling if request fails
    matchGAIAID = re.search("(?:https?:\/\/plus.google.com\/)([0-9]+)", rArchived.text)
    # later: add error handling if no match found
    gaia_id = matchGAIAID.group(1)
    from ghunt.modules import gaia
    await gaia.hunt(None, gaia_id, json_file)
