from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from series import views
from series.models import Series

# series views
urlpatterns = patterns('',
    # Example:
	(r'^readings/', include('reading.urls')),
	url(r'^$', views.index, name="index"),
	#url(r'^upcoming/$', views.upcoming, name="upcoming"),
	url(r'^about/$', views.about, name="about"),
	(r'^(?P<series_id>\d+)/readings/', include('reading.urls')),
	url(r'^(?P<series_id>\d+)/$', views.detail_series, name="detail-series"),
	url(r'^edit/$', views.edit_series, name="create-series"), 
	url(r'^(?P<series_id>\d+)/edit/$', views.edit_series, name="edit-series"),
	url(r'^(?P<series_id>\d+)/remove/$', views.remove_series, name="remove-series"),
	url(r'^contact/(?P<contact_id>\d+)/$', views.detail_contact, name="detail-contact"),
	url(r'^contact/list/$', views.contact_list, name="list-contact"),
	url(r'^contact/edit/$', views.edit_contact, name="create-contact"),
	url(r'^contact/(?P<contact_id>\d+)/edit/$', views.edit_contact, name="edit-contact"),	
	url(r'^venue/list/$', views.venue_list, name="list-venue"),
	url(r'^venue/edit/$', views.edit_venue, name="create-venue"),
	url(r'^venue/(?P<venue_id>\d+)/$', views.detail_venue, name="detail-venue"),
	url(r'^venue/(?P<venue_id>\d+)/edit/$', views.edit_venue, name="edit-venue"),
	url(r'^affiliate/list/$', views.affiliate_list, name="list-affiliate"),
	url(r'^affiliate/(?P<affiliate_id>\d+)/$', views.edit_affiliate, name="detail-affiliate"),
	url(r'^affiliate/edit/$', views.edit_affiliate, name="create-affiliate"),
	url(r'^affiliate/(?P<affiliate_id>\d+)/edit/$', views.edit_affiliate, name="edit-affiliate"),
)

if settings.DEBUG:		
	urlpatterns += patterns('', 
	(r'^media/(?P<path>.*)$', 
	'django.views.static.serve', 
	{'document_root': '/Users/wbert/Sites/django/readsr/media', 'show_indexes': True }))

#if settings.DEBUG:
#    urlpatterns += patterns('',
#        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/wbert/Sites/css'}),
#    )

