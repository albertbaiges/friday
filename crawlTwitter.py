# This file provides a convenient way to interact with Twitter API
# It is based and relies on Tweepy

import tweepy
from tweepy.parsers import JSONParser


def tweetsWithKeywordJSON(keyword, samples):
    consumer_key= 'CKXyrLIRjOoEPwDisGM3uLvSN'
    consumer_secret= '4F9Xg0kawfekbMkt96Tjo97o7RzTz2LV9UKxYiuc5nVFOOOT9K'
    access_token= '988767977796403201-vqhmrMjU30V2FceVUGC6AyQeox1FAOD'
    access_token_secret= 'bCr1GYdXEofxbI09ix96Y943uLsnop7wRftAMgi044lfd'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # ONLY RETRIEVES UP TO 100 TWEETS
    #api = tweepy.API(auth, parser = JSONParser())
    #tweets = api.search(keyword + " -filter:retweets", count = samples, tweet_mode='extended')
    #return tweets

    # ALLOWS RETRIEVING MORE THAN 100, BUT HAVE TO BE CAREFUL WITH TWITTER API RATE LIMIT
    api = tweepy.API(auth)
    tweets = []
    for tweet in tweepy.Cursor(api.search, q=keyword, tweet_mode='extended').items(int(samples)):
        tweets.append(tweet)
    return tweets
