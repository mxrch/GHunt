import httpx
import time

from datetime     import date
from urllib.parse import urlencode
from json         import loads as JSON_LOADS

# grabs todays date with special formatting for json request url ( assemble_calendar_url() )
def get_min_date():
    today = date.today()

    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    offset /= 60
    offset /= 60
    offset *= -1

    d1 = today.strftime("%Y-%m-%d")
    d1 += "T00:00:00"
   
    offset = format_timezone(offset)

    d1 += offset
    return d1

# assembling the json request url endpoint
def assemble_calendar_url(calendarId, singleEvents, maxAttendees, maxResults, sanitizeHtml, timeMin, API_key, email):
    base_url = "https://clients6.google.com/calendar/v3/calendars/{0}/events?".format(email)
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

# splitting date format (ex. 2020-10-18T20:15:00+04:00)
def split_date_formats(date_str):
    start_date    = date_str.split("T")[0]
    start_hour    = date_str.split(":")[0][11:]
    start_minutes = date_str.split(":")[1]
    GMT           = format_timezone(date_str.split(":")[2][3:])
    return "{} {}:{} GMT {}".format(start_date, start_hour, start_minutes, GMT)

# formats time zone to our needs
def format_timezone(tz):
    tz = int(tz)
    if tz >= 0:
        tz = "+{:02d}:00".format(tz)
    else:
        # it doesn't need - character, because offset will have itself
        tz = "{:03d}:00".format(tz)
    return tz

# main method of calendar.py
def fetch_calendar(email):
    url_endpoint = "https://calendar.google.com/calendar/u/0/embed?src={}&hl=en".format(email)
    print("\nGoogle Calendar : " + url_endpoint)
    req = httpx.get(url_endpoint)

    source = req.text

    try:
        # parsing parameters from source code
        calendarId   = source.split('title\":\"')[1].split('\"')[0]
        singleEvents = "true"
        maxAttendees = 1
        maxResults   = 250
        sanitizeHtml = "true"
        timeMin      = get_min_date()
        API_key      = source.split('developerKey\":\"')[1].split('\"')[0]
    except IndexError:
        return None


    json_calendar_endpoint = assemble_calendar_url(calendarId, singleEvents, maxAttendees, maxResults, sanitizeHtml, timeMin, API_key, email)
    myJSON = httpx.get(json_calendar_endpoint)

    myJSON_Object = JSON_LOADS(myJSON.text)

    events_dict = {}

    try:
        for json_iter in myJSON_Object["items"]:
            event_title = json_iter["summary"]
            start_time  = split_date_formats( json_iter["start"]["dateTime"] )
            end_time    = split_date_formats( json_iter["end"]["dateTime"]   )

            events_dict[event_title] = start_time + "####" + end_time
            
            # print(json_calendar_endpoint)
    except KeyError:
        return None

    return events_dict
