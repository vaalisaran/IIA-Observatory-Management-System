# Generated migration to remove CalDAV/Radicale fields from events models.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        # Remove caldav_event_path from CalendarEvent
        migrations.RemoveField(
            model_name="calendarevent",
            name="caldav_event_path",
        ),
        # Remove CalDAV fields from UserCalendarSettings
        migrations.RemoveField(
            model_name="usercalendarsettings",
            name="caldav_url",
        ),
        migrations.RemoveField(
            model_name="usercalendarsettings",
            name="caldav_user",
        ),
        migrations.RemoveField(
            model_name="usercalendarsettings",
            name="caldav_password",
        ),
        migrations.RemoveField(
            model_name="usercalendarsettings",
            name="caldav_calendar_name",
        ),
        migrations.RemoveField(
            model_name="usercalendarsettings",
            name="is_caldav_synced",
        ),
    ]
