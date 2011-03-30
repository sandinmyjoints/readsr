from django.conf import settings
from django.contrib.sites.models import Site
from series.models import Series

def series_list(request):
	"""
	Adds the current list of all readings series for this cityiste based on the settings file to the template context.
	"""

	try:
		series_list = Series.objects.filter(site__exact=settings.SITE_ID)
		return { 'series_list': series_list }
	except Site.DoesNotExist:
		return { 'series_list': ""}
