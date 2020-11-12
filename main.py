import tweepy
from tweepy.parsers import JSONParser
import requests
import re
from googletrans import Translator
from lxml import html
import pandas as pd
import nltk 
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords

nltk.download("punkt") # Pre-trained to tokenize in English
nltk.download("stopwords") # List of stopwords, for multiple languages


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

spamTweetsCounter = 0
for tweet in tweets["statuses"]:
   # Getting text in the text
   tweetText = tweet["full_text"]
   print(tweetText)
   ############ EARLY SPAM DETECTION ############ 
   # Find hashtags in the tweet
   hashtags = re.findall("#[A-Za-z0-9_]*", tweet["full_text"])
   # Find phone number in the tweet
   telf = re.findall("[0-9]{9}", tweet["full_text"])
   # DEBUG -> Display detected hashtags and/or phone number
   print("telefono", telf)
   print("num hashtags", len(hashtags))
   # Mark as spam if too many hashtags or if contains phone number
   if((len(hashtags) > 8) or telf):
      # DEBUG -> Display if it was marked as spam
      print("Detected as spam")
      spamTweetsCounter = spamTweetsCounter + 1
      continue       # Skip further analysis
   
   # FUTHER SPAM DETECTION
   # Clean de tweet text -> Removing hashtags and URLs
   tweetCleaned = re.sub("(@[A-Za-z0-9_-]*[ ])|(#[A-Za-z0-9_-]*[ ])|http[s]*[.:/A-Za-z0-9_-]*|[.,;:]", "", tweet["full_text"])
                        # There is no need to remove phone number because there are not, if it had phone number it was directly spam
   print(tweetCleaned)

   # Separate text into individual words (only works for english -> punkt is pretrained for english)
   tweetTokens = word_tokenize(tweetCleaned)
   print(tweetTokens)
   # Convert text tokens to lower case
   for i in range(len(tweetTokens)):
      tweetTokens[i] = tweetTokens[i].lower()
   print(tweetTokens)
   # Remove stop words (tweetTokensNo)(S)top(W)ords
   englishStopWords = stopwords.words("english")
   tweetTokensNoSW = list(filter(lambda x: x not in englishStopWords, tweetTokens))
   print(tweetTokensNoSW)

   #earlyFilter= ["buy", "now", "click ", "here", "free", "shop" , "money", "back", "guarantee", "discount", "viagra", "order", "here"]
   #tokens = word_tokenize(tweetCleanned)
#
   #for token in tokens:
   #   i = tokens.index(token)
   #   if (token == "shop" and tokens[i+1] == "now"):
   #      print("it contained shop now")
   #   elif (token == "buy" and tokens[i+1] == "now"):
   #      print("it contained buy now")
   #   elif (token == "click" and tokens[i+1] == "here"):
   #      print("it contained click here")
   #      elif (token == "order" and tokens[i+1] == "here"):
   #      print("it contained order here")
   #   elif (token == "money" and tokens[i+1] == "back" and tokens[i+2] == "guarantee"):
   #      print("it contained money back guarantee")
#
   #print(tokens)
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




