from django.db import models
from series.models import Series
from django.contrib.sites.models import Site

class Reading(models.Model):
	
	date_and_time = models.DateTimeField("Date and Time")
	series = models.ForeignKey(Series)
	description = models.CharField("Description", max_length=200, blank=True, null=True)

#	def __init__(self, date_and_time=None, series=None, description=None):
#		super(Reading, self).__init__()
#		self.date_and_time = date_and_time
#		self.series = series
#		self.description = description
		
	def __unicode__(self):
		return "%s on %s at %s" % (self.series.primary_name, self.date_and_time.date(), self.date_and_time.time())
		
	def date(self):
		return self.date_and_time.date()
		
	def time(self):
		return self.date_and_time.time()
		
	@models.permalink
	def get_absolute_url(self):
		return ('detail-reading', (), { 
			'reading_id': self.id })
	
	class Meta(object):
		ordering = ('date_and_time',)