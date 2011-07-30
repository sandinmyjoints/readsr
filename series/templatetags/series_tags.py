from datetime import date
from itertools import groupby

from django import template
from django.conf import settings
from django.utils.html import conditional_escape as esc

from series.models import Series

register = template.Library()

MAX_SERIES_SIDEBAR_LIST = 5

@register.inclusion_tag("sidebar_series_list.html")
def show_series_list(max_series=MAX_SERIES_SIDEBAR_LIST):
    """ 
    An inclusion tag that grabs a given number of series to display in a sidebar list.
    """
    
    try:
        series_list = Series.objects.filter(site__exact=settings.SITE_ID)
        if series_list.count() > max_series:
            more_series = series_list.count() - max_series
            series_list = series_list[:max_series]
            
        return { 'series_list': series_list, 'more_series': more_series }
    except Site.DoesNotExist:
        return { 'series_list': '', 'more_series': ''}
    

# Register the template tag so it is available to templates
#register.tag("slice_string", do_slice_string)