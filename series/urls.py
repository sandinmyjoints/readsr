from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from series import views
from series.models import Series

urlpatterns = patterns('',
    url(r'^readings/', include('reading.urls')),
    url(r'^about/$', views.about, name="about"),
    url(r'^list/$', views.list_series, name="list-series"),
    url(r'^(?P<series_id>\d+)/readings/', include('reading.urls')),
    url(r'^(?P<series_id>\d+)/$', views.index, name="detail-series"),
    url(r'^tag/(?P<tag_slug>\w+)/$', views.list_by_tag, name="list-by-tag"),
    # url(r'^taglist/$', views.list_tags, name="list-tags"),
    url(r'^taglist/$', direct_to_template, { "template": "list_tags.html" }, name="list-tags"),
    url(r'^edit/$', views.create_series, name="create-series"), 
    url(r'^(?P<series_id>\d+)/edit/$', views.edit_series, name="edit-series"),
    url(r'^(?P<series_id>\d+)/remove/$', views.remove_series, name="remove-series"),
    # Detail-contact should not be needed now since django-profiles will handle these views.
    url(r'^contact/(?P<contact_id>\d+)/$', views.contact_detail, name="detail-contact"), 
    url(r'^contact/(?P<contact_id>\d+)/edit/$', views.edit_user_series, name="edit-user-series"),
    #url(r'^contact/list/$', views.contact_list, name="list-contact"),
    #url(r'^contact/edit/$', views.edit_contact, name="create-contact"),
    #url(r'^contact/(?P<contact_id>\d+)/edit/$', views.edit_contact, name="edit-contact"),  
    url(r'^venue/list/$', views.venue_list, name="list-venue"),
    url(r'^venue/edit/$', views.edit_venue, name="create-venue"),
    url(r'^venue/(?P<venue_id>\d+)/$', views.venue_detail, name="detail-venue"),
    url(r'^venue/(?P<venue_id>\d+)/edit/$', views.edit_venue, name="edit-venue"),
    url(r'^affiliate/list/$', views.affiliate_list, name="list-affiliate"),
    url(r'^affiliate/(?P<affiliate_id>\d+)/$', views.edit_affiliate, name="detail-affiliate"),
    url(r'^affiliate/edit/$', views.edit_affiliate, name="create-affiliate"),
    url(r'^affiliate/(?P<affiliate_id>\d+)/edit/$', views.edit_affiliate, name="edit-affiliate"),
    url(r'^site/', views.site_redirect, name="site-redirect"),
    url(r'^$', views.index, name="index"),
)

if settings.DEBUG:      
    urlpatterns += patterns('', 
    url(r'^splash/$', views.splash, name="splash"),
    (r'^media/(?P<path>.*)$', 
    'django.views.static.serve', 
    {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }))

#if settings.DEBUG:
#    urlpatterns += patterns('',
#        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/wbert/Sites/css'}),
#    )

