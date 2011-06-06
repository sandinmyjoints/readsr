from calendar import HTMLCalendar
from django import template
from reading.reading_calendar import ReadingCalendar

register = template.Library()

def do_reading_calendar(parser, token):
	try:
        # syntax is {% reading_calendar year month reading_list %}
#		tag_name, year, month = token.split_contents()
		tag_name, year, month, reading_list = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
#	return ReadingCalendarNode(year, month)
	return ReadingCalendarNode(year, month, reading_list)
	

class ReadingCalendarNode(template.Node):
#	def __init__(self, year, month):
	def __init__(self, year, month, reading_list):
		try:
			#print "incoming year is %s, incoming month is %s" % (year, month)
			self.year = template.Variable(year)
			self.month = template.Variable(month)
			self.reading_list = template.Variable(reading_list)
		except ValueError:
			raise template.TemplateSyntaxError
		
	def render(self, context):
		try:
			my_reading_list = self.reading_list.resolve(context)
			my_year = self.year.resolve(context)
			my_month = self.month.resolve(context)
			print "args are %d %d %d" % (int(my_year), int(my_month), True)
			cal = ReadingCalendar(my_reading_list)
			#cal = HTMLCalendar()
			response = cal.formatmonth(int(my_year), int(my_month))
			print "response is %s" % response
			return response
		except ValueError:
			return			
		except template.VariableDoesNotExist:
			return
		
register.tag("reading_calendar", do_reading_calendar)
		