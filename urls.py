from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from registration import backends, views
from series.forms import FullNameRegistrationForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	#(r'^readsr/', include('series.urls')),
    (r'^admin/', include(admin.site.urls)),
	# django-registration has a url entry for accounts/register, but it uses a default form.
	# we want to use the form that allows for a new user's full name to be entered, so 
	# we'll grab accounts/register here before it gets to the django-registration urls.
	url(r'^accounts/register/$',
        views.register,
        {'backend': 'registration.backends.default.DefaultBackend', 'form_class': FullNameRegistrationForm},
        name='registration_register'),
	# below line is for django-registration
	(r'^accounts/', include('registration.backends.default.urls')),
	(r'^accounts/profile/$', 'series.views.account_profile'),
	# below lines were for using django's default installed registration/account system
	# but django-registration takes care of these
    #(r'^accounts/login/$',  login ),
	#(r'^accounts/logout/$', 'series.views.logout_user'),	
	#(r'^accounts/register/$', 'series.views.register'),
	(r'^', include('series.urls')),
    
)

