import re

from django.conf import settings
from django.contrib.sites.models import Site

from profiles import urls

import tweepy

from series.models import Series, Contact
from series.util import get_tweepy_api

MAX_SERIES_SIDEBAR_LIST = 5 # The maximum number of series to list in the sidebar.

def series_list(request):
    """
    Grabs the current list of all readings series for this city_site based on the settings 
    file to the template context. If there are more than MAX_SERIES_SIDEBAR_LIST, show only
    that many series and provide a link to the full list.
    """

    try:
        series_list = Series.objects.filter(site__exact=settings.SITE_ID)
        if series_list.count() > MAX_SERIES_SIDEBAR_LIST:
            more_series = series_list.count() - MAX_SERIES_SIDEBAR_LIST
            series_list = series_list[:MAX_SERIES_SIDEBAR_LIST]
            
        return { 'series_list': series_list, 'more_series': more_series }
    except Site.DoesNotExist:
        return { 'series_list': ""}

def contact(request):
    """
    Adds the current contact (the series-specific model that is associated with
    a User) to the template context.
    """
    try:
        # This should return a queryset of either zero (if no user is logged in) or
        # one (logged-in user) contact objects.
        if Contact.objects.filter(user__exact=request.user.id).count() == 0:
            return { 'contact': "" }
        else:
            #c = Contact.objects.filter(user__exact=request.user.id)[:1]
            c = Contact.objects.get(user__exact=request.user.id)
            return { 'contact': c }
    except Exception as ex:
        if settings.DEBUG:
            print "Exception in contact context processor: %s" % ex
        return { 'contact': "" }

def tweets(request):
    """
    Adds the most recent tweets to the template context.
    """
    try:
        return { 'tweets': get_latest_tweets() }
    except Exception as ex:
        if settings.DEBUG:
            print "Exception in tweets context processor: %s" % ex
        return { 'tweets': "" }

def get_latest_tweets():
    user = 'readsr'
    messages_to_display = 5
    api = get_tweepy_api()
    statuses = api.user_timeline(count=messages_to_display)
    messages = []

    for status in statuses:
        # Replaces the @username mentions with a URL    
        replaced_mentions = re.sub(r'\b(@\w+)\b', r'<a href="http://twitter.com/\1">\1</a>',status.text);
        # Replaces the #tag's with a URL
        replaced_hashtags = re.sub(r'\b(#\w+)\b', r'<a href="http://twitter.com/#!/search?q=%23\1">\1</a>',replaced_mentions);
        # Replaces the published times with a URL
        replaced_times = (replaced_hashtags + " "+
            "<span class='tiny-font'><a href='http://twitter.com/#!/"+
            user+"/status/"+str(status.id)+"'>"+str(status.created_at)+
            "</a></span>")
        messages.append(replaced_times)
        
    return messages