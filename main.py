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
import fasttext
import plotly.express as px


nltk.download("punkt") # Pre-trained to tokenize in English
nltk.download("stopwords") # List of stopwords, for multiple languages


######### WORDLIST FILTERS SENSITIVITIES [%] #########
spamSensitivity = 20
toxicitySensitivity = 20



#GET THE LIST OF COUNTRIES, SCRAPPING WIKIPEDIA
#response = requests.get("https://en.wikipedia.org/wiki/List_of_sovereign_states")
#tree = html.fromstring(response.text)
#table = tree.xpath("//table[1]/tbody/tr/td[1]//a/text()")
#regex = re.compile('^([ ]+)|.[^a-zA-Z ].|([ ]+)$|[^a-zA-Z ]'); # Try to reduce complexity of this regex, but maintaining functionality
#countries = list(filter(lambda x: x!="" and x!= " Other states " and x!="and", list(map(lambda x: regex.sub("", x), table))))
#countries = countries[3:-142]

# SETTING UP THE DATAFRAME FOR COUNTRIES
#dfCountries = pd.DataFrame(index = countries, columns = ["Counter", "Fips"])
#dfCountries.loc[:, "Counter"] = 0
unkownCountries = 0
#print(df)

# SETTING UP THE DATAFRAME FOR SENTIMENTS
sentiments = ["empty", "sadness", "enthusiasm", "neutral", "worry", "surprise", "love", "fun", "hate", "happiness", "toxic"]
sentimentDF = pd.DataFrame(index = sentiments, columns = ["Counter"])
sentimentDF.loc[:, :] = 0


# GET THE 3 CODE FIPS FOR COUNTRIES
response = requests.get("https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3")
tree = html.fromstring(response.text)
codes = tree.xpath('//div/div[@class="plainlist"]')
fipsPairs = codes[0].text_content()[63:]
print(fipsPairs)
fipsPairs = fipsPairs.replace(u'\xa0', u' ') # Prevents \xa0 between words
fipsPairs = re.sub(" \(.*\)", "", fipsPairs)
listFipsPairs = fipsPairs.split("\n")[:-1] # Up to -1 to remove a last empty string in the list

countryCodes = []
countryNames = []

for i in range(len(listFipsPairs)):
   (code, *country) = listFipsPairs[i].split()
   countryCodes.append(code)
   countryNames.append(" ".join(country))

dfCountries = pd.DataFrame(index = countryNames, columns = ["Counter"])
dfCountries.loc[:, "Counter"] = 0
dfCountries.insert(1, "Code", countryCodes)


#print(dfCountries)
print(dfCountries.to_string())

# CRAWL TWITTER DATA
consumer_key= 'CKXyrLIRjOoEPwDisGM3uLvSN'
consumer_secret= '4F9Xg0kawfekbMkt96Tjo97o7RzTz2LV9UKxYiuc5nVFOOOT9K'
access_token= '988767977796403201-vqhmrMjU30V2FceVUGC6AyQeox1FAOD'
access_token_secret= 'bCr1GYdXEofxbI09ix96Y943uLsnop7wRftAMgi044lfd'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser = JSONParser())


keyword = "@MKBHD"  #KEYWORD TO SEARCH
numTweets = 1
tweets = api.search(keyword + " -filter:retweets", count = numTweets, tweet_mode='extended')

translator = Translator()

dfTweets = pd.DataFrame(columns = ["Tweet"])
#print(dfTweets)


spamTweetsCounter = 0
toxicTweetsCounter = 0
for tweet in tweets["statuses"]:
   # Getting text in the text
   tweetText = tweet["full_text"]
   #print(tweetText)
   ############ EARLY SPAM DETECTION ############ 
   # Find hashtags in the tweet
   hashtags = re.findall("#[A-Za-z0-9_]*", tweet["full_text"])
   # Find phone number in the tweet
   telf = re.findall("[0-9]{9}", tweet["full_text"])
   # DEBUG -> Display detected hashtags and/or phone number
   #print("telefono", telf)
   #print("num hashtags", len(hashtags))
   # Mark as spam if too many hashtags or if contains phone number
   if((len(hashtags) > 8) or telf):
      # DEBUG -> Display if it was marked as spam
      #print("Detected as spam")
      spamTweetsCounter = spamTweetsCounter + 1
      #continue       # Skip further analysis
   
   # FUTHER SPAM DETECTION
   # Clean de tweet text -> Removing hashtags and URLs
   tweetCleaned = re.sub("(@[A-Za-z0-9_-]*[ ])|(#[A-Za-z0-9_-]*[ ])|http[s]*[.:/A-Za-z0-9_-]*|[.,;:]", "", tweetText)
                        # There is no need to remove phone number because there are not, if it had phone number it was directly spam
   #print(tweetCleaned)
   #Removing special characters
   tweetCleaned = re.sub("[^a-zA-Z ]", "", tweetCleaned) 
   #print(tweetCleaned)
   # Separate text into individual words (only works for english -> punkt is pretrained for english)
   tweetTokens = word_tokenize(tweetCleaned)
   #print(tweetTokens)
   # Convert text tokens to lower case
   for i in range(len(tweetTokens)):
      tweetTokens[i] = tweetTokens[i].lower()
   #print(tweetTokens)
   # Remove stop words (tweetTokensNo)(S)top(W)ords
   englishStopWords = stopwords.words("english")
   tweetTokensNoSW = list(filter(lambda x: x not in englishStopWords, tweetTokens))
   #print(tweetTokensNoSW)
   tweetNoSW = ' '.join(tweetTokensNoSW)


   spamWordList = ["cash", "offer", "free", "samples", "exclusive", "discount", "been", "selected", "offer",
                  "giveaway", "purchase", "now", "lose", "weight", "fast", "buy", "now", "click", "here", "entry", "win", "tickets",
                  "chances", "to", "winner", "cash", "membership", "claim", "link", "please", "confirm", "subscribe", "reply", "shop", "money", "back", "guarantee", 
                  "discount", "viagra", "order", "act", "action", "apply", "online", "direct", "call", "clearance", "deal", "expire", "get", "started", "important",
                  "information", "instant", "limited", "time", "new", "customers", "only", "offer", "expires", "once", "lifetime", "read", "special", "promotion",
                  "take", "last", "urgent", "stock", "stocks", "bargain", "best", "price", "bonus", "email", "marketing", "gift", "access", "trial", "incredible", 
                  "deal", "do", "today", "unlimited", "visit", "website", "avoid", "cancel", "cheap", "certified", "congratulations", "credit", "card",
                  "easy", "terms", "grant", "hosting", "info", "information", "member", "out", "debt", "giving", "away", "guaranteed", "join", "millions",
                  "age", "restrictions", "winning", "consolidate", "earn", "extra", "hidden", "nude", "nudes", "message", "dm"]
   
   #tokens = word_tokenize(tweetCleanned)
   isSpam = 0
   for token in tweetTokensNoSW:
         if(token in spamWordList):
            isSpam = isSpam + 1

   #print("Number of spam words", isSpam)


   prob = isSpam/len(tweetTokensNoSW)*100 # Will consider it to be spam above 20-25 %
   #print(len(tweetTokensNoSW))
   #print(prob)
   if(prob >= toxicitySensitivity):
      #print("Detected to be spam")
      spamTweetsCounter += 1
      #continue

   model = fasttext.train_supervised("training.txt")
   #print("Joined cleaned tweet")
   #print(' '.join(tweetTokensNoSW))
   #print(' '.join(tweetTokensNoSW))
   #print("Is spam detected with fasttext?")
   prediction = model.predict(tweetNoSW)
   #print(prediction)

   # TOXICITY DETECTION % TODO: Reduce the wordlist, we do not need so many words and slows down the app
   toxicityWordList = ["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes",
                     "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch",
                     "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob",
                     "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmunch", "buttplug", "c0ck",
                     "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch",
                     "cockmuncher", "cocks", "cocksuck ", "cocksucked ", "cocksucker", "cocksucking", "cocksucks ", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox",
                     "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick ", "cuntlicker ", "cuntlicking ", "cunts", "cyalis",
                     "cyberfuc", "cyberfuck ", "cyberfucked ", "cyberfucker", "cyberfuckers", "cyberfucking ", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa",
                     "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates ", "ejaculating ", "ejaculatings", "ejaculation",
                     "ejakulate", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy",
                     "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck ", "fingerfucked ", "fingerfucker ", "fingerfuckers", "fingerfucking",
                     "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked",
                     "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme ", "fucks", "fuckwhit", "fuckwit", "fudge packer", 
                     "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged ", "gangbangs ", "gaylord", "gaysex", 
                     "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex ", "hell", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", 
                     "jack-off ", "jackoff", "jap", "jerk-off ", "jism", "jiz ", "jizm ", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", 
                     "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lmfao", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", 
                     "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", 
                     "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked ", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking ", "mothafuckings", "mothafucks", 
                     "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", 
                     "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers ", 
                     "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim ", "orgasims ", "orgasm", "orgasms ", "p0rn", "pawn", "pecker", "penis", "penisfucker", 
                     "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses ", "pissflaps", 
                     "pissin ", "pissing", "pissoff ", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks ", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys ", "rectum", 
                     "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", 
                     "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters ", 
                     "shitting", "shittings", "shitty ", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", 
                     "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", 
                     "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"]
   
   isToxic = 0
   for token in tweetTokensNoSW:
         if(token in toxicityWordList):
            isToxic = isToxic + 1
   
   prob = isToxic/len(tweetTokensNoSW)*100
   if(prob >= toxicitySensitivity):
      #print("Detected to be toxic")
       sentimentDF.loc["toxic", "Counter"] += 1
      #continue



   # SENTIMENT ANALISIS
   model_emotions = fasttext.train_supervised("training_emotions.txt")
   prediction_emotion = model_emotions.predict(tweetNoSW)
   print("Reached")
   sentiment = re.sub("__label__", "", prediction_emotion[0][0]);
   print(sentiment);
   sentimentDF.loc[sentiment, "Counter"] += 1

   # TWEET LOCATION

   ############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION PROCESS FOR THE TWEETS ############
   DEBUG_CLASSIFICATION_COUNTRIES = False
   #########################################################################################
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



fig = px.bar(sentimentDF, x=sentiments, y='Counter')
fig.show()


############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION INFO FOR THE TWEETS ############
DEBUG_CLASSIFIED_COUNTRIES = False
if(DEBUG_CLASSIFIED_COUNTRIES):
   print(dfCountries)
   print("Number of tweets without contry:", unkownCountries)
   print(dfCountries.loc["Spain"])
######################################################################################
#print(dfTweets)

fig = px.choropleth(dfCountries, locations="Code",
                    color="Counter", color_continuous_scale=px.colors.sequential.Plasma)
fig.show()
