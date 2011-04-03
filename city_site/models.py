from django.db import models
from django.contrib.sites.models import Site
from django.contrib.localflavor.us.models import USStateField

class CitySite(Site):
	"""
	An extension of Django's Site model that associates a location in the US (city and state)
	with a given Django site.
	"""
	city = models.CharField(max_length=100)
	state = USStateField()
	
	def _get_city_and_state(self):
		return u'%s, %s' % (city, state)
		
	city_and_state = property(_get_city_and_state)
	
	def __unicode__(self):
		return city_and_state
		