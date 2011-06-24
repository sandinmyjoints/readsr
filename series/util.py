import tweepy
from django.conf import settings

# Return a tweepy.API instance configured to use the global cache #########
def get_tweepy_api():
	# set up and return a twitter api object
	auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
	auth.set_access_token(settings.TWITTER_ACCESS_KEY, settings.TWITTER_ACCESS_SECRET)
	api = tweepy.API(auth, cache=settings.TWEEPY_CACHE)	
	return api