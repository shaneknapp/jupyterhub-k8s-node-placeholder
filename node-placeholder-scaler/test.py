#! /usr/bin/env python3

import datetime
import zoneinfo

import scaler.calendar


def test_calendar_events():
    """
    Test calendar event fetching and parsing.

    Uses a public Google Calendar with known events.
    """

    tz = zoneinfo.ZoneInfo(key="America/Los_Angeles")

    # test calendar with known events
    zero_events_noon_june = datetime.datetime(2023, 6, 14, 12, 0, 0, tzinfo=tz)
    one_event_five_pm_april = datetime.datetime(2023, 4, 27, 17, 0, 0, tzinfo=tz)
    three_events_eight_thirty_pm_march = datetime.datetime(
        2023, 3, 6, 20, 30, 0, tzinfo=tz
    )

    # this is a public calendar with known events
    calendar = scaler.calendar.get_calendar(
        "https://calendar.google.com/calendar/ical/c_s47m3m1nuj3s81187k3b2b5s5o%40group.calendar.google.com/public/basic.ics"
    )
    zero_events = scaler.calendar.get_events(calendar, time=zero_events_noon_june)
    one_event = scaler.calendar.get_events(calendar, time=one_event_five_pm_april)
    three_events = scaler.calendar.get_events(
        calendar, time=three_events_eight_thirty_pm_march
    )

    assert len(zero_events) == 0
    assert len(one_event) == 1
    assert len(three_events) == 3


def main():
    test_calendar_events()
    print("All tests passed.")


if __name__ == "__main__":
    main()
