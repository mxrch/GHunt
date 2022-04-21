import json
import urllib.parse
from io import BytesIO
from urllib.parse import unquote as parse_url

from PIL import Image

from lib.search import search as gdoc_search
from lib.utils import *


def get_channel_data(client, channel_url):
    data = None

    retries = 2
    for retry in list(range(retries))[::-1]:
        req = client.get(f"{channel_url}/about")
        source = req.text
        try:
            data = json.loads(source.split('var ytInitialData = ')[1].split(';</script>')[0])
        except (KeyError, IndexError):
            if retry == 0:
                return False
            continue
        else:
            break

    handle = data["metadata"]["channelMetadataRenderer"]["vanityChannelUrl"].split("/")[-1]
    tabs = [x[list(x.keys())[0]] for x in data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]]
    about_tab = [x for x in tabs if x["title"].lower() == "about"][0]
    channel_details = about_tab["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]

    out = {
        "name": None,
        "description": None,
        "channel_urls": [],
        "email_contact": False,
        "views": None,
        "joined_date": None,
        "primary_links": [],
        "country": None
        }

    out["name"] = data["metadata"]["channelMetadataRenderer"]["title"]

    out["channel_urls"].append(data["metadata"]["channelMetadataRenderer"]["channelUrl"])
    out["channel_urls"].append(f"https://www.youtube.com/c/{handle}")
    out["channel_urls"].append(f"https://www.youtube.com/user/{handle}")

    out["email_contact"] = "businessEmailLabel" in channel_details

    out["description"] = channel_details["description"]["simpleText"] if "description" in channel_details else None
    out["views"] = channel_details["viewCountText"]["simpleText"].split(" ")[0] if "viewCountText" in channel_details else None
    out["joined_date"] = channel_details["joinedDateText"]["runs"][1]["text"] if "joinedDateText" in channel_details else None
    out["country"] = channel_details["country"]["simpleText"] if "country" in channel_details else None

    if "primaryLinks" in channel_details:
        for primary_link in channel_details["primaryLinks"]:
            title = primary_link["title"]["simpleText"]
            url = parse_url(primary_link["navigationEndpoint"]["urlEndpoint"]["url"].split("&q=")[-1])
            out["primary_links"].append({"title": title, "url": url})

    return out

def youtube_channel_search(client, query):
    try:
        link = "https://www.youtube.com/results?search_query={}&sp=EgIQAg%253D%253D"
        req = client.get(link.format(urllib.parse.quote(query)))
        source = req.text
        data = json.loads(
            source.split('window["ytInitialData"] = ')[1].split('window["ytInitialPlayerResponse"]')[0].split(';\n')[0])
        channels = \
        data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0][
            "itemSectionRenderer"]["contents"]
        results = {"channels": [], "length": len(channels)}
        for channel in channels:
            if len(results["channels"]) >= 10:
                break
            title = channel["channelRenderer"]["title"]["simpleText"]
            if not query.lower() in title.lower():
                continue
            avatar_link = channel["channelRenderer"]["thumbnail"]["thumbnails"][0]["url"].split('=')[0]
            if avatar_link[:2] == "//":
                avatar_link = "https:" + avatar_link
            profile_url = "https://youtube.com" + channel["channelRenderer"]["navigationEndpoint"]["browseEndpoint"][
                "canonicalBaseUrl"]
            req = client.get(avatar_link)
            img = Image.open(BytesIO(req.content))
            hash = str(image_hash(img))
            results["channels"].append({"profile_url": profile_url, "name": title, "hash": hash})
        return results
    except (KeyError, IndexError):
        return False


def youtube_channel_search_gdocs(client, query, data_path, gdocs_public_doc):
    search_query = f"site:youtube.com/channel \\\"{query}\\\""
    search_results = gdoc_search(search_query, data_path, gdocs_public_doc)
    channels = []

    for result in search_results:
        sanitized = "https://youtube.com/" + ('/'.join(result["link"].split('/')[3:5]).split("?")[0])
        if sanitized not in channels:
            channels.append(sanitized)

    if not channels:
        return False

    results = {"channels": [], "length": len(channels)}
    channels = channels[:5]

    for profile_url in channels:
        data = None
        avatar_link = None

        retries = 2
        for retry in list(range(retries))[::-1]:
            req = client.get(profile_url, follow_redirects=True)
            source = req.text
            try:
                data = json.loads(source.split('var ytInitialData = ')[1].split(';</script>')[0])
                avatar_link = data["metadata"]["channelMetadataRenderer"]["avatar"]["thumbnails"][0]["url"].split('=')[0]
            except (KeyError, IndexError) as e:
                #import pdb; pdb.set_trace()
                if retry == 0:
                    return False
                continue
            else:
                break
        req = client.get(avatar_link)
        img = Image.open(BytesIO(req.content))
        hash = str(image_hash(img))
        title = data["metadata"]["channelMetadataRenderer"]["title"]
        results["channels"].append({"profile_url": profile_url, "name": title, "hash": hash})
    return results


def get_channels(client, query, data_path, gdocs_public_doc):
    from_youtube = youtube_channel_search(client, query)
    from_gdocs = youtube_channel_search_gdocs(client, query, data_path, gdocs_public_doc)
    to_process = []
    if from_youtube:
        from_youtube["origin"] = "youtube"
        to_process.append(from_youtube)
    if from_gdocs:
        from_gdocs["origin"] = "gdocs"
        to_process.append(from_gdocs)
    if not to_process:
        return False
    return to_process


def get_confidence(data, query, hash):
    score_steps = 4

    for source_nb, source in enumerate(data):
        for channel_nb, channel in enumerate(source["channels"]):
            score = 0

            if hash == imagehash.hex_to_flathash(channel["hash"], 8):
                score += score_steps * 4
            if query == channel["name"]:
                score += score_steps * 3
            if query in channel["name"]:
                score += score_steps * 2
            if ((source["origin"] == "youtube" and source["length"] <= 5) or
                    (source["origin"] == "google" and source["length"] <= 4)):
                score += score_steps
            data[source_nb]["channels"][channel_nb]["score"] = score

    channels = []
    for source in data:
        for channel in source["channels"]:
            found_better = False
            for source2 in data:
                for channel2 in source2["channels"]:
                    if channel["profile_url"] == channel2["profile_url"]:
                        if channel2["score"] > channel["score"]:
                            found_better = True
                            break
                if found_better:
                    break
            if found_better:
                continue
            else:
                channels.append(channel)
    channels = sorted([json.loads(chan) for chan in set([json.dumps(channel) for channel in channels])],
                      key=lambda k: k['score'], reverse=True)
    panels = sorted(set([c["score"] for c in channels]), reverse=True)
    if not channels or (panels and panels[0] <= 0):
        return 0, []

    maxscore = sum([p * score_steps for p in range(1, score_steps + 1)])
    for panel in panels:
        chans = [c for c in channels if c["score"] == panel]
        if len(chans) > 1:
            panel -= 5
        return (panel / maxscore * 100), chans


def extract_usernames(channels):
    return [chan['profile_url'].split("/user/")[1] for chan in channels if "/user/" in chan['profile_url']]
