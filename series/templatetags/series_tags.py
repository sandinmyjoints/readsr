from django import template
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

register = template.Library()



# Register the template tag so it is available to templates
#register.tag("slice_string", do_slice_string)