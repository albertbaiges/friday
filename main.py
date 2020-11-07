import tweepy
from tweepy.parsers import JSONParser
import requests
import re
import goslate
from lxml import html
import pandas as pd


#GET THE LIST OF COUNTRIES, SCRAPPING WIKIPEDIA
response = requests.get("https://en.wikipedia.org/wiki/List_of_sovereign_states")
tree = html.fromstring(response.text)
table = tree.xpath("//table[1]/tbody/tr/td[1]//a/text()")
regex = re.compile('^([ ]+)|.[^a-zA-Z ].|([ ]+)$|[^a-zA-Z ]'); # Try to reduce complexity of this regex, but maintaining functionality
countries = list(filter(lambda x: x!="" and x!= " Other states " and x!="and", list(map(lambda x: regex.sub("", x), table))))
countries = countries[3:-142]

# SETTING UP THE DATAFRAME
dfCountries = pd.DataFrame(index = countries, columns = ["Counter"])
dfCountries.loc[:, :] = 0
#print(df)


# CRAWL TWITTER DATA
consumer_key= 'CKXyrLIRjOoEPwDisGM3uLvSN'
consumer_secret= '4F9Xg0kawfekbMkt96Tjo97o7RzTz2LV9UKxYiuc5nVFOOOT9K'
access_token= '988767977796403201-vqhmrMjU30V2FceVUGC6AyQeox1FAOD'
access_token_secret= 'bCr1GYdXEofxbI09ix96Y943uLsnop7wRftAMgi044lfd'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser = JSONParser())

keyword = "#TrumpvsBiden" 
numTweets = 2
tweets = api.search(keyword + " -filter:retweets", count = numTweets)

#gs = goslate.Goslate()

dfTweets = pd.DataFrame(columns = ["Tweet"])
#print(dfTweets)
for tweet in tweets["statuses"]:
   #print(tweet["user"]["location"], gs.translate( tweet["user"]["location"],'en'))
   dfTweets = dfTweets.append({"Tweet": tweet["text"]}, ignore_index = True)

print(dfTweets)




