from django import template
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

register = template.Library()

def do_slice_string(parser, token):
	"""
	The template tag's syntax is {% reading_calendar year month reading_list %}
    """

	try:
		tag_name, year, month, reading_list = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
	return ReadingCalendarNode(year, month, reading_list)
	

class SliceStringNode(template.Node):
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


# Register the template tag so it is available to templates
register.tag("slice_string", do_slice_string)