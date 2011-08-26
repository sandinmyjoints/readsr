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
    # we'll grab accounts/register here before it gets to the django-registration urls, and
    # pass in the custom form.
    url(r'^accounts/register/$',
        views.register,
        { 'backend': 'registration.backends.default.DefaultBackend', 'form_class': FullNameRegistrationForm },
        name='registration_register' ),

    # Include the URLs from django-registration.
    (r'^accounts/', include('registration.backends.default.urls')),

    # Intercept some of the django-profiles request and use our custom views to pass
    # in custom data related to user-owned series.
    # url(r'^profiles/create/$',
    #     'profiles.views.create_profile',
    #     name='profiles_create_profile'),
    url(r'^profiles/edit/$',
        'series.views.edit_profile',
        name='profiles_edit_profile'),
    url(r'^profiles/(?P<username>\w+)/$',
        'series.views.profile_detail',
        name='profiles_profile_detail'),

    # Include the URLs from django-profiles.
    (r'^profiles/', include('profiles.urls')),

    # Include the urls for the series app.
    (r'^', include('series.urls')),
    url(r'', include('social_auth.urls')),
    
)

