from dateutil.relativedelta import relativedelta
from datetime import datetime
import json
from geopy import distance
from geopy.geocoders import Nominatim
from typing import *

import httpx
from alive_progress import alive_bar

from ghunt import globals as gb
from ghunt.objects.base import *
from ghunt.helpers.utils import *
from ghunt.objects.utils import *
from ghunt.helpers.knowledge import get_gmaps_type_translation


def get_datetime(datepublished: str):
    """
        Get an approximative date from the maps review date
        Examples : 'last 2 days', 'an hour ago', '3 years ago'
    """
    if datepublished.split()[0] in ["a", "an"]:
        nb = 1
    else:
        if datepublished.startswith("last"):
            nb = int(datepublished.split()[1])
        else:
            nb = int(datepublished.split()[0])

    if "minute" in datepublished:
        delta = relativedelta(minutes=nb)
    elif "hour" in datepublished:
        delta = relativedelta(hours=nb)
    elif "day" in datepublished:
        delta = relativedelta(days=nb)
    elif "week" in datepublished:
        delta = relativedelta(weeks=nb)
    elif "month" in datepublished:
        delta = relativedelta(months=nb)
    elif "year" in datepublished:
        delta = relativedelta(years=nb)
    else:
        delta = relativedelta()

    return (datetime.today() - delta).replace(microsecond=0, second=0)

async def get_reviews(as_client: httpx.AsyncClient, gaia_id: str) -> Tuple[str, Dict[str, int], List[MapsReview], List[MapsPhoto]]:
    """Extracts the target's statistics, reviews and photos."""
    next_page_token = ""
    agg_reviews = []
    agg_photos = []
    stats = {}

    req = await as_client.get(f"https://www.google.com/locationhistory/preview/mas?authuser=0&hl=en&gl=us&pb={gb.config.templates['gmaps_pb']['stats'].format(gaia_id)}")
    if req.status_code == 302 and req.headers["Location"].startswith("https://www.google.com/sorry/index"):
        return "failed", stats, [], []

    data = json.loads(req.text[5:])
    if not data[16][8]:
        return "empty", stats, [], []
    stats = {sec[6]:sec[7] for sec in data[16][8][0]}
    total_reviews = stats["Reviews"] + stats["Ratings"] + stats["Photos"]
    if not total_reviews:
        return "empty", stats, [], []

    with alive_bar(total_reviews, receipt=False) as bar:
        for category in ["reviews", "photos"]:
            first = True
            while True:
                if first:
                    req = await as_client.get(f"https://www.google.com/locationhistory/preview/mas?authuser=0&hl=en&gl=us&pb={gb.config.templates['gmaps_pb'][category]['first'].format(gaia_id)}")
                    first = False
                else:
                    req = await as_client.get(f"https://www.google.com/locationhistory/preview/mas?authuser=0&hl=en&gl=us&pb={gb.config.templates['gmaps_pb'][category]['page'].format(gaia_id, next_page_token)}")
                data = json.loads(req.text[5:])

                new_reviews = []
                new_photos = []
                next_page_token = ""

                # Reviews
                if category == "reviews":
                    if not data[24]:
                        return "private", stats, [], []
                    reviews_data = data[24][0]
                    if not reviews_data:
                        break
                    for review_data in reviews_data:
                        review = MapsReview()
                        review.id = review_data[6][0]
                        review.date = datetime.utcfromtimestamp(review_data[6][1][3] / 1000000)
                        if len(review_data[6][2]) > 15 and review_data[6][2][15]:
                            review.comment = review_data[6][2][15][0][0]
                        review.rating = review_data[6][2][0][0]

                        review.location.id = review_data[1][14][0]
                        review.location.name = review_data[1][2]
                        review.location.address = review_data[1][3]
                        review.location.tags = review_data[1][4] if review_data[1][4] else []
                        review.location.types = [x for x in review_data[1][8] if x]
                        if review_data[1][0]:
                            review.location.position.latitude = review_data[1][0][2]
                            review.location.position.longitude = review_data[1][0][3]
                        # if len(review_data[1]) > 31 and review_data[1][31]:
                            # print(f"Cost level : {review_data[1][31]}")
                            # review.location.cost_level = len(review_data[1][31])
                        new_reviews.append(review)
                        bar()

                    agg_reviews += new_reviews

                    if not new_reviews or len(data[24]) < 4 or not data[24][3]:
                        break
                    next_page_token = data[24][3].strip("=")

                # Photos
                elif category == "photos" :
                    if not data[22]:
                        return "private", stats, [], []
                    photos_data = data[22][1]
                    if not photos_data:
                        break
                    for photo_data in photos_data:
                        photos = MapsPhoto()
                        photos.id = photo_data[0][10]
                        photos.url = photo_data[0][6][0].split("=")[0]
                        date = photo_data[0][21][6][8]
                        photos.date = datetime(date[0], date[1], date[2], date[3]) # UTC
                        # photos.approximative_date = get_datetime(date[8][0]) # UTC

                        if len(photo_data) > 1:
                            photos.location.id = photo_data[1][14][0]
                            photos.location.name = photo_data[1][2]
                            photos.location.address = photo_data[1][3]
                            photos.location.tags = photo_data[1][4] if photo_data[1][4] else []
                            photos.location.types = [x for x in photo_data[1][8] if x] if photo_data[1][8] else []
                            if photo_data[1][0]:
                                photos.location.position.latitude = photo_data[1][0][2]
                                photos.location.position.longitude = photo_data[1][0][3]
                            if len(photo_data[1]) > 31 and photo_data[1][31]:
                                photos.location.cost_level = len(photo_data[1][31])
                        new_photos.append(photos)
                        bar()

                    agg_photos += new_photos

                    if not new_photos or len(data[22]) < 4 or not data[22][3]:
                        break
                    next_page_token = data[22][3].strip("=")

    return "", stats, agg_reviews, agg_photos

def avg_location(locs: Tuple[float, float]):
    """
        Calculates the average location
        from a list of (latitude, longitude) tuples.
    """
    latitude = []
    longitude = []
    for loc in locs:
        latitude.append(loc[0])
        longitude.append(loc[1])

    latitude = sum(latitude) / len(latitude)
    longitude = sum(longitude) / len(longitude)
    return latitude, longitude

def translate_confidence(percents: int):
    """Translates the percents number to a more human-friendly text"""
    if percents >= 100:
        return "Extremely high"
    elif percents >= 80:
        return "Very high"
    elif percents >= 60:
        return "Little high"
    elif percents >= 40:
        return "Okay"
    elif percents >= 20:
        return "Low"
    elif percents >= 10:
        return "Very low"
    else:
        return "Extremely low"

def sanitize_location(location: Dict[str, str]):
    """Returns the nearest place from a Nomatim location response."""
    not_country = False
    not_town = False
    town = "?"
    country = "?"
    if "city" in location:
        town = location["city"]
    elif "village" in location:
        town = location["village"]
    elif "town" in location:
        town = location["town"]
    elif "municipality" in location:
        town = location["municipality"]
    else:
        not_town = True
    if not "country" in location:
        not_country = True
        location["country"] = country
    if not_country and not_town:
        return False
    location["town"] = town
    return location

def calculate_probable_location(geolocator: Nominatim, reviews_and_photos: List[MapsReview|MapsPhoto], gmaps_radius: int):
    """Calculates the probable location from a list of reviews and the max radius."""
    tmprinter = TMPrinter()
    radius = gmaps_radius

    locations = {}
    tmprinter.out(f"Calculation of the distance of each review...")
    for nb, review in enumerate(reviews_and_photos):
        if not review.location.position.latitude or not review.location.position.longitude:
            continue
        if review.location.id not in locations:
            locations[review.location.id] = {"dates": [], "locations": [], "range": None, "score": 0}
        location = (review.location.position.latitude, review.location.position.longitude)
        for review2 in reviews_and_photos:
            location2 = (review2.location.position.latitude, review2.location.position.longitude)
            dis = distance.distance(location, location2).km

            if dis <= radius:
                locations[review.location.id]["dates"].append(review2.date)
                locations[review.location.id]["locations"].append(location2)

        maxdate = max(locations[review.location.id]["dates"])
        mindate = min(locations[review.location.id]["dates"])
        locations[review.location.id]["range"] = maxdate - mindate
        tmprinter.out(f"Calculation of the distance of each review ({nb}/{len(reviews_and_photos)})...")

    tmprinter.clear()

    locations = {k: v for k, v in
                 sorted(locations.items(), key=lambda k: len(k[1]["locations"]), reverse=True)}  # We sort it

    tmprinter.out("Identification of redundant areas...")
    to_del = []
    for id in locations:
        if id in to_del:
            continue
        for id2 in locations:
            if id2 in to_del or id == id2:
                continue
            if all([loc in locations[id]["locations"] for loc in locations[id2]["locations"]]):
                to_del.append(id2)
    for hash in to_del:
        del locations[hash]

    tmprinter.out("Calculating confidence...")

    maxrange = max([locations[hash]["range"] for hash in locations])
    maxlen = max([len(locations[hash]["locations"]) for hash in locations])
    minreq = 3
    mingroups = 3

    score_steps = 4
    for hash, loc in locations.items():
        if len(loc["locations"]) == maxlen:
            locations[hash]["score"] += score_steps * 4
        if loc["range"] == maxrange:
            locations[hash]["score"] += score_steps * 3
        if len(locations) >= mingroups:
            others = sum([len(locations[h]["locations"]) for h in locations if h != hash])
            if len(loc["locations"]) > others:
                locations[hash]["score"] += score_steps * 2
        if len(loc["locations"]) >= minreq:
            locations[hash]["score"] += score_steps

    panels = sorted(set([loc["score"] for loc in locations.values()]), reverse=True)

    maxscore = sum([p * score_steps for p in range(1, score_steps + 1)])
    for panel in panels:
        locs = [loc for loc in locations.values() if loc["score"] == panel]
        if len(locs[0]["locations"]) == 1:
            panel /= 2
        if len(reviews_and_photos) < 4:
            panel /= 2
        confidence = translate_confidence(panel / maxscore * 100)
        for nb, loc in enumerate(locs):
            avg = avg_location(loc["locations"])
            while True:
                try:
                    location = geolocator.reverse(f"{avg[0]}, {avg[1]}", timeout=10).raw["address"]
                    break
                except:
                    pass
            location = sanitize_location(location)
            locs[nb]["avg"] = location
            del locs[nb]["locations"]
            del locs[nb]["score"]
            del locs[nb]["range"]
            del locs[nb]["dates"]

        tmprinter.clear()

        return confidence, locs

def output(err: str, stats: Dict[str, int], reviews: List[MapsReview], photos: List[MapsPhoto], gaia_id: str):
    """Pretty print the Maps results, and do some guesses."""

    print(f"\nProfile page : https://www.google.com/maps/contrib/{gaia_id}/reviews")

    if err == "failed":
        print("\n[-] Your IP has been blocked by Google. Try again later.")

    reviews_and_photos: List[MapsReview|MapsPhoto] = reviews + photos
    if err != "private" and (err == "empty" or not reviews_and_photos):
        print("\n[-] No review.")
        return

    print("\n[Statistics]")
    for section, number in stats.items():
        if number:
            print(f"{section} : {number}")

    if err == "private":
        print("\n[-] Reviews are private.")
        return

    print("\n[Reviews]")
    avg_ratings = round(sum([x.rating for x in reviews]) / len(reviews), 1)
    print(f"[+] Average rating : {ppnb(avg_ratings)}/5\n")

    # I removed the costs calculation because of a Google update : https://github.com/mxrch/GHunt/issues/529

    # costs_table = {
    #     1: "Inexpensive",
    #     2: "Moderately expensive",
    #     3: "Expensive",
    #     4: "Very expensive"
    # }

    # total_costs = 0
    # costs_stats = {x:0 for x in range(1,5)}
    # for review in reviews_and_photos:
    #     if review.location.cost_level:
    #         costs_stats[review.location.cost_level] += 1
    #         total_costs += 1
    # costs_stats = dict(sorted(costs_stats.items(), key=lambda item: item[1], reverse=True)) # We sort the dict by cost popularity

    # if total_costs:
    #     print("[Costs]")
    #     for cost, desc in costs_table.items():
    #         line = f"> {ppnb(round(costs_stats[cost]/total_costs*100, 1))}% {desc} ({costs_stats[cost]})"
    #         style = ""
    #         if not costs_stats[cost]:
    #             style = "bright_black"
    #         elif costs_stats[cost] == list(costs_stats.values())[0]:
    #             style = "spring_green1"
    #         gb.rc.print(line, style=style)
            
    #     avg_costs = round(sum([x*y for x,y in costs_stats.items()]) / total_costs)
    #     print(f"\n[+] Average costs : {costs_table[avg_costs]}")
    # else:
    #     print("[-] No costs data.")

    types = {}
    for review in reviews_and_photos:
        for type in review.location.types:
            if type not in types:
                types[type] = 0
            types[type] += 1
    types = dict(sorted(types.items(), key=lambda item: item[1], reverse=True))

    types_and_tags = {}
    for review in reviews_and_photos:
        for type in review.location.types:
            if type not in types_and_tags:
                types_and_tags[type] = {}
            for tag in review.location.tags:
                if tag not in types_and_tags[type]:
                    types_and_tags[type][tag] = 0
                types_and_tags[type][tag] += 1
            types_and_tags[type] = dict(sorted(types_and_tags[type].items(), key=lambda item: item[1], reverse=True))
    types_and_tags = dict(sorted(types_and_tags.items()))

    if types_and_tags:
        print("\nTarget's locations preferences :")

        unknown_trads = []
        for type, type_count in types.items():
            tags_counts = types_and_tags[type]
            translation = get_gmaps_type_translation(type)
            if not translation:
                unknown_trads.append(type)
            gb.rc.print(f"\n🏨 [underline]{translation if translation else type.title()} [{type_count}]", style="bold")
            nb = 0
            for tag, tag_count in list(tags_counts.items()):
                if nb >= 7:
                    break
                elif tag.lower() == type:
                    continue
                print(f"- {tag} ({tag_count})")
                nb += 1

        if unknown_trads:
            print(f"\n⚠️ The following gmaps types haven't been found in GHunt\'s knowledge.")
            for type in unknown_trads:
                print(f"- {type}")
            print("Please open an issue on the GHunt Github or submit a PR to add it !")

    geolocator = Nominatim(user_agent="nominatim")

    confidence, locations = calculate_probable_location(geolocator, reviews_and_photos, gb.config.gmaps_radius)
    print(f"\n[+] Probable location (confidence => {confidence}) :")

    loc_names = []
    for loc in locations:
        loc_names.append(
            f"- {loc['avg']['town']}, {loc['avg']['country']}"
        )

    loc_names = set(loc_names)  # delete duplicates
    for loc in loc_names:
        print(loc)