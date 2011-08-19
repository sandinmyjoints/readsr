# Django settings for dcreadings project.
import os, sys
import tweepy

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# Add swingtime development version -- TODO need to find a better way of doing this
SWINGTIME_PATH = os.path.abspath(os.path.join(os.path.join(ROOT_PATH, ".."), "django-swingtime"))
sys.path.insert(0, SWINGTIME_PATH)

# to import rrule2text until I get it installable
# TODO fix this
RRULE2TEXT_PATH = os.path.abspath(os.path.join(os.path.join(ROOT_PATH, ".."), "rrule2text"))
sys.path.insert(0, RRULE2TEXT_PATH)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('William', 'william.bert@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'django_db',                      # Or path to database file if using sqlite3.
        'USER': 'django_db',                      # Not used with sqlite3.
        'PASSWORD': 'Fqw3EtedHfrMPqZB',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#		'HOST': '/var/mysql/mysql.sock',
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
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
SECRET_KEY = '9(ff*vntzzm^v&lw69j2k5(6y&parqy-u4i9lcad_j-o38+zuz'

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
    # "series.context_processors.series_list",
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

TWITTER_CONSUMER_KEY = "oZpnsipBP1jBhGbPp5eCUA"
TWITTER_CONSUMER_SECRET = "pi48qgRK2O0SmOlpWIDZtFsFh6AlaAcGY6IOyeY7IE"
TWITTER_ACCESS_KEY = "307415363-Lb84FJbNjH6zyUSpDL0YYY9ovp8CQiIDXWbv5TcR"
TWITTER_ACCESS_SECRET = "GXZBz82nLkytDbnFaU1nHrNhavCuhnKTFx3ACS59k"

BITLY_USER = "readsr"
BITLY_KEY = "R_8b4787749bdbc284709fc4dca825cc9b"

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
