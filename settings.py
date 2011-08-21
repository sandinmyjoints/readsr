# Django settings for dcreadings project.
import os
import tweepy

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://127.0.0.1:8000/readsr/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "	http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

STATIC_DOC_ROOT = os.path.join(ROOT_PATH, 'media')

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'series.middleware.AjaxMessaging',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.contrib.messages.context_processors.messages",
	"django.core.context_processors.request",
	"city_site.context_processors.city_site",
	"city_site.context_processors.all_city_sites",
	"series.context_processors.contact",
	"series.context_processors.tweets",
)


ROOT_URLCONF = 'readsr.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	# Set in local_settings
	''
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
	'django.contrib.humanize',
	'django.contrib.flatpages',
	'city_site',
	'series',
	'reading',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
	'contact_form',
	'hideemail',
	'registration',
	'profiles',
	'swingtime',
	'south',
	'taggit',
	'taggit_templatetags',
	'debug_toolbar',	
)


AUTH_PROFILE_MODULE = 'series.Contact'

ACCOUNT_ACTIVATION_DAYS = 7

# set in local_settings.py
EMAIL_HOST = ()
EMAIL_PORT = ()
EMAIL_HOST_USER = ()
EMAIL_HOST_PASSWORD = ()
EMAIL_USE_TLS = True

LOGIN_REDIRECT_URL = "/"

TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
TWITTER_ACCESS_KEY = ""
TWITTER_ACCESS_SECRET = ""

BITLY_USER = ""
BITLY_KEY = ""

TWEEPY_CACHE_DIR = os.path.join(ROOT_PATH, 'tweepy_cache')
 
TWEEPY_CACHE = tweepy.cache.FileCache(TWEEPY_CACHE_DIR, 3600)

# Override the absolute url for django user objects to use the profiles app
# detail page, per the instructions in the django-registration simple-backend docs.
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/profiles/%s/" % o.username
}

# Grab local settings from local settings fie
try:
 from local_settings import *
except ImportError:
 pass
