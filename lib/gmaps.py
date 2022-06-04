from datetime import datetime
from dateutil.relativedelta import relativedelta
from geopy import distance
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from lib.utils import *


def scrape(gaiaID, client, cookies, config, headers, regex_rev_by_id, is_headless):
    def get_datetime(date_published):
        if date_published.split()[0] == "a":
            nb = 1
        else:
            nb = int(date_published.split()[0])
        if "minute" in date_published:
            delta = relativedelta(minutes=nb)
        elif "hour" in date_published:
            delta = relativedelta(hours=nb)
        elif "day" in date_published:
            delta = relativedelta(days=nb)
        elif "week" in date_published:
            delta = relativedelta(weeks=nb)
        elif "month" in date_published:
            delta = relativedelta(months=nb)
        elif "year" in date_published:
            delta = relativedelta(years=nb)
        else:
            delta = relativedelta()
        return (datetime.today() - delta).replace(microsecond=0, second=0)

    tmprinter = TMPrinter()

    base_url = f"https://www.google.com/maps/contrib/{gaiaID}/reviews?hl=en"
    print(f"\nGoogle Maps : {base_url.replace('?hl=en', '')}")

    tmprinter.out("Initial request...")

    req = client.get(base_url)
    source = req.text

    data = source.split(';window.APP_INITIALIZATION_STATE=')[1].split(';window.APP_FLAGS')[0].replace("\\", "")

    if "/maps/reviews/data" not in data:
        tmprinter.out("")
        print("[-] No reviews")
        return False

    chrome_options = get_chrome_options_args(is_headless)
    options = {
        'connection_timeout': None  # Never timeout, otherwise it floods errors
    }

    tmprinter.out("Starting browser...")

    driver_path = get_driverpath()
    driver = webdriver.Chrome(executable_path=driver_path, seleniumwire_options=options, options=chrome_options)
    driver.header_overrides = headers
    wait = WebDriverWait(driver, 15)

    tmprinter.out("Setting cookies...")
    driver.get("https://www.google.com/robots.txt")
    
    if not config.gmaps_cookies:
        cookies = {"CONSENT": config.default_consent_cookie}
    for k, v in cookies.items():
        driver.add_cookie({'name': k, 'value': v})

    tmprinter.out("Fetching reviews page...")
    reviews = []
    try:
        driver.get(base_url)

        #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.section-scrollbox')))
        #scrollbox = driver.find_element(By.CSS_SELECTOR, 'div.section-scrollbox')
        tab_info = None
        try:
            tab_info = driver.find_element(by=By.XPATH, value="//span[contains(@aria-label, 'review') and contains(@aria-label, 'rating')]")
        except NoSuchElementException:
            pass
        
        if tab_info and tab_info.text:
            scroll_max = sum([int(x) for x in tab_info.text.split() if x.isdigit()])
        else:
            return False

        tmprinter.clear()
        print(f"[+] {scroll_max} reviews found !")

        scrollbox = tab_info.find_element(By.XPATH, "../../../..")
        timeout = scroll_max * 2.5
        timeout_start = time()
        reviews_elements = driver.find_elements(by=By.XPATH, value="//div[@data-review-id][@aria-label]")
        tmprinter.out(f"Fetching reviews... ({len(reviews_elements)}/{scroll_max})")
        while len(reviews_elements) < scroll_max:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollbox)
            reviews_elements = driver.find_elements(by=By.XPATH, value='//div[@data-review-id][@aria-label]')
            tmprinter.out(f"Fetching reviews... ({len(reviews_elements)}/{scroll_max})")
            if time() > timeout_start + timeout:
                tmprinter.out(f"Timeout while fetching reviews !")
                break

        tmprinter.out("Fetching internal requests history...")
        requests = [r.url for r in driver.requests if "locationhistory" in r.url]
        tmprinter.out(f"Fetching internal requests... (0/{len(requests)})")
        for nb, load in enumerate(requests):
            req = client.get(load)
            data += req.text.replace('\n', '')
            tmprinter.out(f"Fetching internal requests... ({nb + 1}/{len(requests)})")

        tmprinter.out(f"Fetching reviews location... (0/{len(reviews_elements)})")
        rating = 0
        for nb, review in enumerate(reviews_elements):
            id = review.get_attribute("data-review-id")
            location = re.compile(regex_rev_by_id.format(id)).findall(data)[0]
            try:
                stars = review.find_element(By.CSS_SELECTOR, 'span[aria-label$="stars "]')
            except Exception:
                stars = review.find_element(By.CSS_SELECTOR, 'span[aria-label$="star "]')
            rating += int(stars.get_attribute("aria-label").strip().split()[0])
            date = get_datetime(stars.find_element(By.XPATH, "following-sibling::span").text)
            reviews.append({"location": location, "date": date})
            tmprinter.out(f"Fetching reviews location... ({nb + 1}/{len(reviews_elements)})")

        rating_avg = rating / len(reviews)
        tmprinter.clear()
        print(f"[+] Average rating : {int(rating_avg) if int(rating_avg) / round(rating_avg, 1) == 1 else round(rating_avg, 1)}/5 stars !")
        # 4.9 => 4.9, 5.0 => 5, we don't show the 0
    except TimeoutException as e:
        print("Error fetching reviews, it is likely that Google has changed the layout of the reviews page.")
    return reviews


def avg_location(locs):
    latitude = []
    longitude = []
    for loc in locs:
        latitude.append(float(loc[0]))
        longitude.append(float(loc[1]))

    latitude = sum(latitude) / len(latitude)
    longitude = sum(longitude) / len(longitude)
    return latitude, longitude


def translate_confidence(percents):
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


def get_confidence(geolocator, data, gmaps_radius):
    tmprinter = TMPrinter()
    radius = gmaps_radius

    locations = {}
    tmprinter.out(f"Calculation of the distance of each review...")
    for nb, review in enumerate(data):
        hash = hashlib.md5(str(review).encode()).hexdigest()
        if hash not in locations:
            locations[hash] = {"dates": [], "locations": [], "range": None, "score": 0}
        location = review["location"]
        for review2 in data:
            location2 = review2["location"]
            dis = distance.distance(location, location2).km

            if dis <= radius:
                locations[hash]["dates"].append(review2["date"])
                locations[hash]["locations"].append(review2["location"])

        maxdate = max(locations[hash]["dates"])
        mindate = min(locations[hash]["dates"])
        locations[hash]["range"] = maxdate - mindate
        tmprinter.out(f"Calculation of the distance of each review ({nb}/{len(data)})...")

    tmprinter.out("")

    locations = {k: v for k, v in
                 sorted(locations.items(), key=lambda k: len(k[1]["locations"]), reverse=True)}  # We sort it

    tmprinter.out("Identification of redundant areas...")
    to_del = []
    for hash in locations:
        if hash in to_del:
            continue
        for hash2 in locations:
            if hash2 in to_del or hash == hash2:
                continue
            if all([loc in locations[hash]["locations"] for loc in locations[hash2]["locations"]]):
                to_del.append(hash2)
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

    # for hash,loc in locations.items():
    #    print(f"{hash} => {len(loc['locations'])} ({int(loc['score'])/40*100})")

    panels = sorted(set([loc["score"] for loc in locations.values()]), reverse=True)

    maxscore = sum([p * score_steps for p in range(1, score_steps + 1)])
    for panel in panels:
        locs = [loc for loc in locations.values() if loc["score"] == panel]
        if len(locs[0]["locations"]) == 1:
            panel /= 2
        if len(data) < 4:
            panel /= 2
        confidence = translate_confidence(panel / maxscore * 100)
        for nb, loc in enumerate(locs):
            avg = avg_location(loc["locations"])
            #import pdb; pdb.set_trace()
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
        tmprinter.out("")
        return confidence, locs
