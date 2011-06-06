from calendar import HTMLCalendar
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

class ReadingCalendar(HTMLCalendar):
		
    def __init__(self, readings):
        super(ReadingCalendar, self).__init__()
        self.readings = self.group_by_day(readings)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.readings:
                cssclass += ' filled'
                body = ['<ul>']
                for reading in self.readings[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % reading.get_absolute_url())
                    body.append(esc(reading.series.primary_name))
                    body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '<span class="dayNumber">%d</span> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<span class="dayNumberNoReadings">%d</span>' % (day))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ReadingCalendar, self).formatmonth(year, month)

    def group_by_day(self, readings):
        field = lambda reading: reading.date_and_time.day
        return dict(
            [(day, list(items)) for day, items in groupby(readings, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)