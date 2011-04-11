from django.conf import settings
from django.contrib.sites.models import Site

from profiles import urls

from series.models import Series, Contact

def series_list(request):
	"""
	Adds the current list of all readings series for this cityiste based on the settings file to the template context.
	"""

	try:
		series_list = Series.objects.filter(site__exact=settings.SITE_ID)
		return { 'series_list': series_list }
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
		print "contact is %s" % Contact.objects.filter(user__exact=request.user.id)
		print "contact is is %d" % request.user.id
		print "user is %s" % request.user
		if Contact.objects.filter(user__exact=request.user.id).count() == 0:
			return { 'contact': "" }
		else:
			#c = Contact.objects.filter(user__exact=request.user.id)[:1]
			c = Contact.objects.get(user__exact=request.user.id)
			return { 'contact': c }
	except Exception as ex:
		print "exception: %s" % ex
		return { 'contact': "" }