from django import template
from django.conf import settings
from django.utils.html import conditional_escape as esc
from django.contrib.sites.models import Site
from django.db.models import Count
from django.core.exceptions import FieldError

from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag

from series.models import Series

register = template.Library()

MAX_SERIES_SIDEBAR_LIST = 5
MAX_TAGS_SIDEBAR_LIST = 5

@register.inclusion_tag("sidebar_tag_list.html")
def show_tag_list(max_tags=MAX_TAGS_SIDEBAR_LIST):
    """ 
    An inclusion tag that grabs a given number of tags to display in a sidebar list.
    """
    
    try:    
        # Get all the tagged items for this app (Series)
        # TODO need to add a filter to get the Series object and check if its 
        # site is equal to the current site
        tag_list = TaggedItem.objects.filter(content_type__app_label="Series")
        # Get a list of all the tags IDs used by these tagged items
        tag_ids = tag_list.values_list('tag_id', flat=True)
        # filter the queryset to only contain the tags used by these items
        tag_list = Tag.objects.filter(id__in=tag_ids)
        # annotate queryset with the counts of each of the tags
        try:
            tag_list = tag_list.annotate(num_times=Count('taggeditem_items')).order_by('-num_times')
        except FieldError:
            tag_list = tag_list.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')
        
        # more_tags = 0
        # if tag_list.count() > max_tags:
        more_tags = tag_list.count() - max_tags
            # tag_list = tag_list[:max_tags]
            
        return { 'tag_list': tag_list[:max_tags], 'more_tags': more_tags > 0 and more_tags or 0 }
    except Site.DoesNotExist:
        return { 'tag_list': '', 'more_tags': 0 }
        
@register.inclusion_tag("sidebar_series_list.html")
def show_series_list(max_series=MAX_SERIES_SIDEBAR_LIST):
    """ 
    An inclusion tag that grabs a given number of series to display in a sidebar list.
    """
    
    try:
        series_list = Series.objects.filter(site__exact=settings.SITE_ID)
        more_series = 0
        if series_list.count() > max_series:
            more_series = series_list.count() - max_series
            series_list = series_list[:max_series]
            
        return { 'series_list': series_list, 'more_series': more_series }
    except Site.DoesNotExist:
        return { 'series_list': '', 'more_series': 0 }
    

# Register the template tag so it is available to templates
#register.tag("slice_string", do_slice_string)