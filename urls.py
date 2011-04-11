from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

from registration import backends, views

from series.forms import FullNameRegistrationForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
	# django-registration has a url entry for accounts/register, but it uses a default form.
	# We want to use the form that allows for a new user's full name to be entered, so 
	# we'll grab accounts/register here before it gets to the django-registration urls.
	url(r'^accounts/register/$',
        views.register,
        {'backend': 'registration.backends.default.DefaultBackend', 'form_class': FullNameRegistrationForm},
        name='registration_register'),
	# Below line includes the URLs from django-registration.
	(r'^accounts/', include('registration.backends.default.urls')),
	# below lines were for using django's default installed registration/account system
	# but django-registration takes care of these
	#(r'^accounts/logout/$', 'series.views.logout_user'),	
	#(r'^accounts/register/$', 'series.views.register'),

	# This includes the URLs from django-profiles
	url(r'^profiles/create/$',
        'profiles.views.create_profile',
        name='profiles_create_profile'),
    url(r'^profiles/edit/$',
        'series.views.edit_profile',
        name='profiles_edit_profile'),
    url(r'^profiles/(?P<username>\w+)/$',
        'series.views.profile_detail',
        name='profiles_profile_detail'),
	#(r'^profiles/', include('profiles.urls')), # default configuration from the profiles app

	# This was the old way of doing an account profile, through the series app.
	#(r'^accounts/profile/$', 'series.views.account_profile'),
	
	#(r'^readsr/', include('series.urls')),
	(r'^', include('series.urls')),
    
)

