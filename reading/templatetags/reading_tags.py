from calendar import HTMLCalendar
from django import template
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

register = template.Library()

def do_reading_calendar(parser, token):
	"""
	The template tag's syntax is {% reading_calendar year month reading_list %}
    """

	try:
		tag_name, year, month, reading_list = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
	return ReadingCalendarNode(year, month, reading_list)
	

class ReadingCalendarNode(template.Node):
	"""
	Process a particular node in the template. Fail silently.
	"""
	
	def __init__(self, year, month, reading_list):
		try:
			self.year = template.Variable(year)
			self.month = template.Variable(month)
			self.reading_list = template.Variable(reading_list)
		except ValueError:
			raise template.TemplateSyntaxError
		
	def render(self, context):
		try:
			# Get the variables from the context so the method is thread-safe.
			my_reading_list = self.reading_list.resolve(context)
			my_year = self.year.resolve(context)
			my_month = self.month.resolve(context)
			cal = ReadingCalendar(my_reading_list)
			return cal.formatmonth(int(my_year), int(my_month))
		except ValueError:
			return			
		except template.VariableDoesNotExist:
			return


class ReadingCalendar(HTMLCalendar):
	"""
	Overload Python's calendar.HTMLCalendar to add the appropriate reading events to
	each day's table cell.
	"""
	
	def __init__(self, readings):
		super(ReadingCalendar, self).__init__()
		# create a list of all the days in the month,
		# and each day has within it a list of the events on that day
		self.readings = self.group_by_day(readings)
		self.setfirstweekday(6) 
		for day in self.readings:
			for reading in self.readings[day]:
				pass

	def formatday(self, day, weekday):
		# 0 is Monday
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
		#print "formatmonth year=%s, month=%s" % (year, month)
		self.year, self.month = year, month
		return super(ReadingCalendar, self).formatmonth(year, month)

	def group_by_day(self, readings):
		field = lambda reading: reading.date_and_time.day
		return dict(
			[(day, list(items)) for day, items in groupby(readings, field)]
		)

	def day_cell(self, cssclass, body):
		return '<td class="%s">%s</td>' % (cssclass, body)

# Register the template tag so it is available to templates
register.tag("reading_calendar", do_reading_calendar)