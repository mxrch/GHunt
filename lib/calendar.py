import httpx
from dateutil.relativedelta import relativedelta
from beautifultable import BeautifulTable
from termcolor import colored

import time
import json
from datetime     import datetime, timezone
from urllib.parse import urlencode


# assembling the json request url endpoint
def assemble_api_req(calendarId, singleEvents, maxAttendees, maxResults, sanitizeHtml, timeMin, API_key, email):
    base_url = f"https://clients6.google.com/calendar/v3/calendars/{email}/events?"
    params = {
        "calendarId": calendarId,
        "singleEvents": singleEvents,
        "maxAttendees": maxAttendees,
        "maxResults": maxResults,
        "timeMin": timeMin,
        "key": API_key
    }
    base_url += urlencode(params, doseq=True)
    return base_url

# from iso to datetime object in utc
def get_datetime_utc(date_str):
    date = datetime.fromisoformat(date_str)
    margin = date.utcoffset()
    return date.replace(tzinfo=timezone.utc) - margin

# main method of calendar.py
def fetch(email, client, config):
    if not config.calendar_cookies:
        cookies = {"CONSENT": config.default_consent_cookie}
        client.cookies = cookies
    url_endpoint = f"https://calendar.google.com/calendar/u/0/embed?src={email}"
    print("\nGoogle Calendar : " + url_endpoint)
    req = client.get(url_endpoint + "&hl=en")
    source = req.text
    try:
        # parsing parameters from source code
        calendarId   = source.split('title\":\"')[1].split('\"')[0]
        singleEvents = "true"
        maxAttendees = 1
        maxResults   = 250
        sanitizeHtml = "true"
        timeMin      = datetime.strptime(source.split('preloadStart\":\"')[1].split('\"')[0], '%Y%m%d').replace(tzinfo=timezone.utc).isoformat()
        API_key      = source.split('developerKey\":\"')[1].split('\"')[0]
    except IndexError:
        return False

    json_calendar_endpoint = assemble_api_req(calendarId, singleEvents, maxAttendees, maxResults, sanitizeHtml, timeMin, API_key, email)
    req = client.get(json_calendar_endpoint)
    data = json.loads(req.text)
    events = []
    try:
        for item in data["items"]:
            title = item["summary"]
            start  = get_datetime_utc(item["start"]["dateTime"])
            end    = get_datetime_utc(item["end"]["dateTime"])

            events.append({"title": title, "start": start, "end": end})
    except KeyError:
        return False

    return {"status": "available", "events": events}

def out(events):
    limit = 5
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    after = [date for date in events if date["start"] >= now][:limit]
    before = [date for date in events if date["start"] <= now][:limit]
    print(f"\n=> The {'next' if after else 'last'} {len(after) if after else len(before)} event{'s' if (len(after) > 1) or (not after and len(before) > 1) else ''} :")
    target = after if after else before

    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_GRID)
    table.columns.header = [colored(x, attrs=['bold']) for x in ["Name", "Datetime (UTC)", "Duration"]]
    for event in target:
        title = event["title"]
        duration = relativedelta(event["end"], event["start"])
        if duration.days or duration.hours or duration.minutes:
            duration = (f"{(str(duration.days) + ' day' + ('s' if duration.days > 1 else '')) if duration.days else ''} "
                f"{(str(duration.hours) + ' hour' + ('s' if duration.hours > 1 else '')) if duration.hours else ''} "
                f"{(str(duration.minutes) + ' minute' + ('s' if duration.minutes > 1 else '')) if duration.minutes else ''}").strip()
        else:
            duration = "?"
        date = event["start"].strftime("%Y/%m/%d %H:%M:%S")
        table.rows.append([title, date, duration])
    print(table)