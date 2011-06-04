from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from reading import views

# reading views
urlpatterns = patterns('',
	url(r'^$', views.list_readings),
	url(r'^list_readings/$', views.list_readings, name="list-readings"),
	url(r'^list_readings/month/(?P<num_months>\d+)/$', views.list_readings_month, name="list-readings-by-months"),
	url(r'^list_readings/month/(?P<num_months>\d+)/(?P<ajax>\d+)/(?P<index>\d+)/$', views.list_readings_month, name="list-readings-by-months-ajax"),
	url(r'^list_readings/date/(?P<year>\d+)/(?P<month>\d+)/(?P<date>\d+)/$', views.list_readings_date, name="list-readings-by-date"),
	url(r'^(?P<reading_id>\d+)/$', views.detail_reading, name="detail-reading"),
	url(r'^edit/$', views.edit_reading, name="create-reading"), 
	url(r'^(?P<reading_id>\d+)/edit/$', views.edit_reading, name="edit-reading"),
	url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)/$', views.calendar, name="calendar"),
)