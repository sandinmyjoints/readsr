import datetime
from swingtime.conf import settings as swingtime_settings

# Set Swingtime settings
# A "strftime" string for formatting start and end time selectors in forms
swingtime_settings.TIMESLOT_TIME_FORMAT = '%I:%M %p'

# Used for creating start and end time form selectors as well as time slot grids.
# Value should be datetime.timedelta value representing the incremental 
# differences between temporal options
swingtime_settings.TIMESLOT_INTERVAL = datetime.timedelta(minutes=30)

# A datetime.time value indicting the starting time for time slot grids and form
# selectors
swingtime_settings.TIMESLOT_START_TIME = datetime.time(9)

# A datetime.timedelta value indicating the offset value from 
# TIMESLOT_START_TIME for creating time slot grids and form selectors. The for
# using a time delta is that it possible to span dates. For instance, one could
# have a starting time of 3pm (15:00) and wish to indicate a ending value 
# 1:30am (01:30), in which case a value of datetime.timedelta(hours=10.5) 
# could be specified to indicate that the 1:30 represents the following date's
# time and not the current date.
swingtime_settings.TIMESLOT_END_TIME_DURATION = datetime.timedelta(hours=+14)

# Indicates a minimum value for the number grid columns to be shown in the time
# slot table.
swingtime_settings.TIMESLOT_MIN_COLUMNS = 4

# Indicate the default length in time for a new occurrence, specifed by using
# a datetime.timedelta object
swingtime_settings.DEFAULT_OCCURRENCE_DURATION = datetime.timedelta(hours=+1)

# If not None, passed to the calendar module's setfirstweekday function.
swingtime_settings.CALENDAR_FIRST_WEEKDAY = 6