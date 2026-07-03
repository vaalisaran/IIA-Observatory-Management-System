import logging

from events.models import CalendarEvent, UserCalendarSettings

logger = logging.getLogger(__name__)


def get_google_service(user_settings):
    """Google Calendar Service is disabled."""
    return None


def sync_event_to_google(event):
    """Sync a Django CalendarEvent to Google Calendar (Disabled)."""
    return


def sync_event_to_caldav(event):
    """CalDAV (Radicale) sync has been removed. This is a no-op stub."""
    return


def delete_from_external_calendars(event):
    """Delete event from external calendars. CalDAV removed; Google sync disabled."""
    return
