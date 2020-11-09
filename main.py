import tweepy
from tweepy.parsers import JSONParser
import requests
import re
from googletrans import Translator
from lxml import html
import pandas as pd
import nltk 
nltk.download("punkt")
from nltk.tokenize import word_tokenize 


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
unkownCountries = 0;
#print(df)


# CRAWL TWITTER DATA
consumer_key= 'CKXyrLIRjOoEPwDisGM3uLvSN'
consumer_secret= '4F9Xg0kawfekbMkt96Tjo97o7RzTz2LV9UKxYiuc5nVFOOOT9K'
access_token= '988767977796403201-vqhmrMjU30V2FceVUGC6AyQeox1FAOD'
access_token_secret= 'bCr1GYdXEofxbI09ix96Y943uLsnop7wRftAMgi044lfd'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser = JSONParser())

keyword = "#lasenzabv"  #KEYWORD TO SEARCH
numTweets = 1
tweets = api.search(keyword + " -filter:retweets", count = numTweets, tweet_mode='extended')

translator = Translator()

dfTweets = pd.DataFrame(columns = ["Tweet"])
#print(dfTweets)

############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION PROCESS FOR THE TWEETS ############
DEBUG_CLASSIFICATION_COUNTRIES = False
#########################################################################################
#print("Reached")
for tweet in tweets["statuses"]:
   print(tweet["full_text"])
   regexHash = re.compile("(#[A-Za-z0-9_]*)")
   hashtags = regexHash.findall(tweet["full_text"])
   telf = re.findall("[0-9]{9}", tweet["full_text"]);
   print("telefono", telf)
   print("num hashtags", len(hashtags))
   if((len(hashtags) > 8) or telf):
      print("Detected as spam")
      continue

   stopWordSpam = ["buy", "now", "click ", "here", "free", "shop" , "money", "back", "guarantee"]
   tokens = word_tokenize(tweet["full_text"])
   print(tokens)
   try: 
      loc = translator.translate(tweet["user"]["location"], dest = 'en').text
      if(DEBUG_CLASSIFICATION_COUNTRIES): print("The location of the tweet:", loc)
      flagUnkown = True
      for word in loc.split():
         if(DEBUG_CLASSIFICATION_COUNTRIES): print("Checking", word)
         if (word in dfCountries.index):
            if(DEBUG_CLASSIFICATION_COUNTRIES): print(word, "appears in the dataframe")
            dfCountries.loc[word, "Counter"] += 1
            if(DEBUG_CLASSIFICATION_COUNTRIES): print("Increased cound for", word, "in the dataframe")
            flagUnkown = False
            break

      if(flagUnkown):
         if(DEBUG_CLASSIFICATION_COUNTRIES): print("Could not find a country")
         unkownCountries += 1
      #print(tweet["text"])
   except Exception as er:
      unkownCountries += 1
      if(DEBUG_CLASSIFICATION_COUNTRIES): print("Something went wrong:", er) 
   #dfTweets = dfTweets.append({"Tweet": tweet["text"]}, ignore_index = True)

############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION INFO FOR THE TWEETS ############
DEBUG_CLASSIFIED_COUNTRIES = False
if(DEBUG_CLASSIFIED_COUNTRIES):
   print(dfCountries)
   print("Number of tweets without contry:", unkownCountries)
   print(dfCountries.loc["Spain"])
######################################################################################
#print(dfTweets)




