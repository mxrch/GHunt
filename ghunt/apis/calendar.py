from ghunt.objects.base import GHuntCreds
from ghunt.errors import *
import ghunt.globals as gb
from ghunt.objects.apis import GAPI, EndpointConfig
from ghunt.parsers.calendar import Calendar, CalendarEvents

import httpx

from typing import *
import inspect
import json
from datetime import datetime, timezone


class CalendarHttp(GAPI):
    def __init__(self, creds: GHuntCreds, headers: Dict[str, str] = {}):
        super().__init__()
        
        if not headers:
            headers = gb.config.headers

        base_headers = {}

        headers = {**headers, **base_headers}

        self.hostname = "clients6.google.com"
        self.scheme = "https"

        self._load_api(creds, headers)

    async def get_calendar(self, as_client: httpx.AsyncClient, calendar_id: str) -> Tuple[bool, Calendar]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None
            require_key = "calendar", # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/calendar/v3/calendars/{calendar_id}"

        req = await self._query(endpoint.name, as_client, base_url)

        # Parsing
        data = json.loads(req.text)

        calendar = Calendar()
        if "error" in data:
            return False, calendar
        
        calendar._scrape(data)

        return True, calendar

    async def get_events(self, as_client: httpx.AsyncClient, calendar_id: str, params_template="next_events",
                        time_min=datetime.today().replace(tzinfo=timezone.utc).isoformat(), max_results=250, page_token="") -> Tuple[bool, CalendarEvents]:
        endpoint = EndpointConfig(
            name = inspect.currentframe().f_code.co_name,
            verb = "GET",
            data_type = None, # json, data or None
            authentication_mode = "sapisidhash", # sapisidhash, cookies_only, oauth or None
            require_key = "calendar", # key name, or None
        )
        self._load_endpoint(endpoint)

        base_url = f"/calendar/v3/calendars/{calendar_id}/events"

        params_templates = {
            "next_events": {
                "calendarId": calendar_id,
                "singleEvents": True,
                "maxAttendees": 1,
                "maxResults": max_results,
                "timeMin": time_min # ISO Format
            },
            "from_beginning": {
                "calendarId": calendar_id,
                "singleEvents": True,
                "maxAttendees": 1,
                "maxResults": max_results
            },
            "max_from_beginning": {
                "calendarId": calendar_id,
                "singleEvents": True,
                "maxAttendees": 1,
                "maxResults": 2500 # Max
            }
        }

        if not params_templates.get(params_template):
            raise GHuntParamsTemplateError(f"The asked template {params_template} for the endpoint {endpoint.name} wasn't recognized by GHunt.")

        params = params_templates[params_template]
        if page_token:
            params["pageToken"] = page_token

        req = await self._query(endpoint.name, as_client, base_url, params=params)

        # Parsing
        data = json.loads(req.text)

        events = CalendarEvents()
        if not data:
            return False, events
        
        events._scrape(data)

        return True, events