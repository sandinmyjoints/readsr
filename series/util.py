import tweepy
from django.conf import settings

def get_tweepy_api():
    """
    Return a tweepy.API instance configured to use the global cache
    """
    
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(settings.TWITTER_ACCESS_KEY, settings.TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth, cache=settings.TWEEPY_CACHE) 
    return api