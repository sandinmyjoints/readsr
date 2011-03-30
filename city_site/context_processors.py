from django.conf import settings
from city_site.models import CitySite
from django.contrib.sites.models import Site

def city_site(request):
	"""
	Adds the current CitySite based on the settings file to the template context.
	"""

	try:
		city_site = CitySite.objects.get(pk=settings.SITE_ID)
		return { 'city_site': city_site }
	except Site.DoesNotExist:
		return { 'city_site': ""}
		