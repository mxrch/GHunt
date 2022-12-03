from datetime import datetime
from typing import *

from ghunt.helpers.utils import get_datetime_utc
from ghunt.objects.apis import Parser


class ConferenceProperties(Parser):
    def __init__(self):
        self.allowed_conference_solution_types: List[str] = []

    def _scrape(self, conference_props_data: Dict[str, any]):
        if (types := conference_props_data.get("allowedConferenceSolutionTypes")):
            self.allowed_conference_solution_types = types

class Calendar(Parser):
    def __init__(self):
        self.id: str = ""
        self.summary: str = ""
        self.time_zone: str = ""
        self.conference_properties: ConferenceProperties = ConferenceProperties()

    def _scrape(self, calendar_data: Dict[str, any]):
        self.id = calendar_data.get("id")
        self.summary = calendar_data.get("summary")
        self.time_zone = calendar_data.get("timeZone")
        conference_props_data = calendar_data.get("conferenceProperties")
        if conference_props_data:
            self.conference_properties._scrape(conference_props_data)

class CalendarReminder(Parser):
    def __init__(self):
        self.method: str = ""
        self.minutes: int = 0

    def _scrape(self, reminder_data: Dict[str, any]):
        self.method = reminder_data.get("method")
        self.minutes = reminder_data.get("minutes")

class CalendarPerson(Parser):
    def __init__(self):
        self.email: str = ""
        self.display_name: str = ""
        self.self: bool = None

    def _scrape(self, person_data: Dict[str, any]):
        self.email = person_data.get("email")
        self.display_name = person_data.get("displayName")
        self.self = person_data.get("self")

class CalendarTime(Parser):
    def __init__(self):
        self.date_time: datetime = None # ISO Format
        self.time_zone: str = ""

    def _scrape(self, time_data: Dict[str, any]):
        if (date_time := time_data.get("dateTime")):
            try:
                self.date_time = get_datetime_utc(date_time)
            except ValueError:
                self.date_time = None
        self.time_zone = time_data.get("timeZone")

class CalendarReminders(Parser):
    def __init__(self):
        self.use_default: int = 0
        self.overrides: List[CalendarReminder] = []

    def _scrape(self, reminders_data: Dict[str, any]):
        self.use_default = reminders_data.get("useDefault")
        if (overrides := reminders_data.get("overrides")):
            for reminder_data in overrides:
                reminder = CalendarReminder()
                reminder._scrape(reminder_data)
                self.overrides.append(reminder)

class CalendarEvent(Parser):
    def __init__(self):
        self.id: str = ""
        self.status: str = ""
        self.html_link: str = ""
        self.created: datetime = "" # ISO Format
        self.updated: datetime = "" # ISO Format
        self.summary: str = ""
        self.description: str = ""
        self.location: str = ""
        self.creator: CalendarPerson = CalendarPerson()
        self.organizer: CalendarPerson = CalendarPerson()
        self.start: CalendarTime = CalendarTime()
        self.end: CalendarTime = CalendarTime()
        self.recurring_event_id: str = ""
        self.original_start_time: CalendarTime = CalendarTime()
        self.visibility: str = ""
        self.ical_uid: str = ""
        self.sequence: int = 0
        self.guest_can_invite_others: bool = None
        self.reminders: CalendarReminders = CalendarReminders()
        self.event_type: str = ""

    def _scrape(self, event_data: Dict[str, any]):
        self.id = event_data.get("id")
        self.status = event_data.get("status")
        self.html_link = event_data.get("htmlLink")
        if (date_time := event_data.get("created")):
            try:
                self.created = get_datetime_utc(date_time)
            except ValueError:
                self.created = None
        if (date_time := event_data.get("updated")):
            try:
                self.updated = get_datetime_utc(date_time)
            except ValueError:
                self.updated = None
        self.summary = event_data.get("summary")
        self.description = event_data.get("description")
        self.location = event_data.get("location")
        if (creator_data := event_data.get("creator")):
            self.creator._scrape(creator_data)
        if (organizer_data := event_data.get("organizer")):
            self.organizer._scrape(organizer_data)
        if (start_data := event_data.get("start")):
            self.start._scrape(start_data)
        if (end_data := event_data.get("end")):
            self.end._scrape(end_data)
        self.recurring_event_id = event_data.get("recurringEventId")
        if (original_start_data := event_data.get("originalStartTime")):
            self.original_start_time._scrape(original_start_data)
        self.visibility = event_data.get("visibility")
        self.ical_uid = event_data.get("iCalUID")
        self.sequence = event_data.get("sequence")
        self.guest_can_invite_others = event_data.get("guestsCanInviteOthers")
        if (reminders_data := event_data.get("reminders")):
            self.reminders._scrape(reminders_data)
        self.event_type = event_data.get("eventType")

class CalendarEvents(Parser):
    def __init__(self):
        self.summary: str = ""
        self.updated: datetime = "" # ISO Format
        self.time_zone: str = ""
        self.access_role: str = ""
        self.default_reminders: List[CalendarReminder] = []
        self.next_page_token: str = ""
        self.items: List[CalendarEvent] = []

    def _scrape(self, events_data: Dict[str, any]):
        self.summary = events_data.get("summary")
        if (date_time := events_data.get("updated")):
            try:
                self.updated = get_datetime_utc(date_time)
            except ValueError:
                self.updated = None
        self.time_zone = events_data.get("timeZone")
        self.access_role = events_data.get("accessRole")
        if (reminders_data := events_data.get("defaultReminders")):
            for reminder_data in reminders_data:
                reminder = CalendarReminder()
                reminder._scrape(reminder_data)
                self.default_reminders.append(reminder)
        self.next_page_token = events_data.get("nextPageToken")
        if (items_data := events_data.get("items")):
            for item_data in items_data:
                event = CalendarEvent()
                event._scrape(item_data)
                self.items.append(event)