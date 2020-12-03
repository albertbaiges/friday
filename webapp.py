import dash
import dash_core_components as dcc
import dash_html_components as dhtml
import pandas as pd
from dash.dependencies import Input, Output, State
import re
from googletrans import Translator
import nltk 
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
import fasttext
import plotly.express as px
from langdetect import detect 
from nltk.tokenize.toktok import ToktokTokenizer
import unidecode

from countries import country_aplha3_lists
import crawlTwitter

######### WORDLIST FILTERS SENSITIVITIES [%] #########
spamSensitivity = 35
toxicitySensitivity = 35


# SET UP

# NLTK Data
nltk.download("punkt") # Pre-trained to tokenize in English
nltk.download("stopwords") # List of stopwords, for multiple languages

# Spanish tokenizer
toktok = ToktokTokenizer() #Used to tokenize spanish sentences

# Dictionary: Country Name in Country's language to english (differents) and common namings
countryNamesTrans = {"Deutschland": "Germany", "España": "Spain", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland", 
                    "England": "United Kingdom of Great Britain and Northern Ireland", "USA": "United States of America"}

# Supported emotions/sentiments
sentiments = ["empty", "sadness", "enthusiasm", "neutral", "worry", "surprise", "love", "fun", "hate", "happiness"]

# Obtaining lists of countries and alpha3 codes
countryNames, countryCodes = country_aplha3_lists() # Assigned using destructuring

# FastText Models
modelSpam = fasttext.train_supervised("training.txt", thread=32)
modelEmotions = fasttext.train_supervised("training_emotions.txt", thread = 32)

# Detection by dictionaries dictionaries
def spamPercentage(words):
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
    for token in words: 
        if(token in spamWordList):
            isSpam = isSpam + 1
    #print("Number of spam words", isSpam)
    percentage = isSpam/len(words)*100 
    #print(percentage)
    return percentage


def toxicPercentage(words):
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
    for token in words:
        if(token in toxicityWordList):
            isToxic = isToxic + 1
    percentage = isToxic/len(words)*100
    print(percentage)
    print("")
    return percentage


# Dash application
app = dash.Dash(__name__)
app.title = "FRIDAY"

 # Dash - DOM
app.layout = dhtml.Div(
    children = [
        dhtml.Div( id="search",
            children = [
                dhtml.Img(id="friday", src = app.get_asset_url('fridayLogo.png'), width = 400),
                dcc.Textarea(id = "keyword"), 
                dcc.Textarea(id = "numTweets"),
                dhtml.Button('Submit', id='submit', n_clicks=0),
                dhtml.P("Both boxes must be filled", id = "emptyPrompt")
                
        ]),
        dcc.Loading(
            dhtml.Div( id= "results",
                children = [
                    dhtml.Div(id = "sentimentsContainer",
                        children = [
                            dcc.Graph(id = "sentiments")
                        ]
                    ),
                    dhtml.P(
                        id = "spam_holder"
                    ),
                    
                    dhtml.P(
                        id = "unkownCountry"
                    ),
                    dhtml.P(
                        id = "unsupportedLanguage"
                    ), 
                    dhtml.P(
                        id = "toxicTweets"
                    ), 
                    dhtml.Div( id = "mapContainer",
                        children  =[
                            dcc.Graph(id = "worldmap")
                        ]    
                    )
                ]
        ), type="graph", loading_state = {"is_loading": True})
    ]
)

# DASH CALLBACK

@app.callback(
    [   # Output elements, modified everytime callback returns
        Output(component_id = "keyword", component_property = "style"),  # Used to style error nothing entered
        Output(component_id = "numTweets", component_property = "style"), # Used to style error nothing entered
        Output(component_id = "emptyPrompt", component_property = "style"), # Used to style error nothing entered
        Output(component_id="results", component_property = "style"), # Div that contains all results data and plots
        Output(component_id = "spam_holder", component_property = "children"), # Display spam counter
        Output(component_id = "unkownCountry", component_property = "children"), # Display unkown countries counter
        Output(component_id = "unsupportedLanguage", component_property = "children"), # Tweets written on an unsupported lang counter
        Output(component_id = "toxicTweets", component_property = "children"), # Tweets that are toxic
        Output(component_id = "worldmap", component_property = "figure"), # Graph holder for the world map
        Output(component_id = "sentiments", component_property = "figure") # Graph holder for the sentiments columns graph
    ],
    [   # Input element, triggers the callback
        Input(component_id = "submit", component_property  = "n_clicks") # Submit button
    
    ],
    [   # State, data that will get retrieved when callback is triggered
        State(component_id = "keyword", component_property  = "value"), # Keyword to search
        State(component_id = "numTweets", component_property  = "value") # Sample of tweets
    ]
)
def performAnalisis(n_clicksButton, keyword, numTweets):    
    if n_clicksButton == 0: # Prevent callback execution when page loads
        raise dash.exceptions.PreventUpdate # Do nothing, prevent updating contents

    if (keyword is None or numTweets is None): # Prevent updating result contents, but display warning/error
        return ({"border-color": "red"}, {"border-color": "red"}, {"display":"inline"},{}, "", "", "", "", {}, {})

    # PREPARE DATAFRAMES

    # Dataframe for sentiments
    sentimentDF = pd.DataFrame(index = sentiments, columns = ["Counter"])
    sentimentDF.loc[:, :] = 0

    # Dataframe for countries
    dfCountries = pd.DataFrame(index = countryNames, columns = ["Counter"])
    dfCountries.loc[:, "Counter"] = 0
    dfCountries.insert(1, "Code", countryCodes)
    #print(dfCountries)
    #print(dfCountries.to_string())

    #CRAWL TWITTER DATA
    # Obtain tweets to be analyzed
    tweets = crawlTwitter.tweetsWithKeywordJSON(keyword, numTweets)

    # Initialize counters
    spamTweetsCounter = 0
    unkownCountries = 0
    unsupportedTweetsCounter = 0
    toxicTweetsCounter = 0

    # Analyze tweets
    for tweet in tweets["statuses"]:
        tweetText = tweet["full_text"] # Getting text in the text
        print("Tweet Text:")
        print(tweetText)

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
            print("Detected as spam by early detection")
            spamTweetsCounter = spamTweetsCounter + 1
            continue       # Skip further analysis
        
        # FUTHER SPAM DETECTION
        # Clean de tweet text -> Removing hashtags and URLs
        tweetCleaned = re.sub("(@[A-Za-z0-9_-]*)|(#[A-Za-z0-9_-]*)|(http[s]*[.:/A-Za-z0-9_-]*)|[.,;:]", "", tweetText)
                                # There is no need to remove phone number because there are not, if it had phone number it was directly spam
        #print(tweetCleaned)
        #Removing special characters
        tweetCleaned = re.sub("[^a-zA-Z ]", "", tweetCleaned)
        # Remove spaces being of sentence
        tweetCleaned = re.sub("^[ ]*", "", tweetCleaned)
        #Removing extra spaces
        tweetCleaned = re.sub("[ ]+", " ", tweetCleaned)
        # Skip futher analysis if tweet cleaned has no text in it 
        print("Tweet Cleaned:")
        print(tweetCleaned)

        if(tweetCleaned == "" or re.sub("[ ]+", "", tweetCleaned) == ""):
            continue
        language = detect(tweetCleaned)
        if(language == "en"):
            # Separate text into individual words (only works for english -> punkt is pretrained for english)
            tweetTokens = word_tokenize(tweetCleaned)
            #print(tweetTokens)
            # Convert text tokens to lower case
            for i in range(len(tweetTokens)):
                tweetTokens[i] = tweetTokens[i].lower()
            #print(tweetTokens)
            if(len(tweetTokens) == 0):
                print("It was an empty tweet, skipping")
                continue
            # Remove stop words (tweetTokensNo)(S)top(W)ords
            englishStopWords = stopwords.words("english")
            tweetTokensNoSW = list(filter(lambda x: x not in englishStopWords, tweetTokens))
            #print(tweetTokensNoSW)
            if(len(tweetTokensNoSW)==0):
                continue
            tweetNoSW = ' '.join(tweetTokensNoSW)

            percentageSpam = spamPercentage(tweetTokensNoSW)
            
            #print(len(tweetTokensNoSW))
            #print(prob)
            if(percentageSpam >= spamSensitivity):
                print("Detected to be spam by dictionary")
                spamTweetsCounter += 1
                continue

            #print("Joined cleaned tweet")
            #print(' '.join(tweetTokensNoSW))
            #print(' '.join(tweetTokensNoSW))
            #print("Is spam detected with fasttext?")
            prediction = modelSpam.predict(tweetNoSW)
            #print(prediction)

            percentageSpam = toxicPercentage(tweetTokensNoSW)
            if(percentageSpam >= toxicitySensitivity):
                print("Detected to be toxic by dictionary")
                toxicTweetsCounter += 1
                #continue



            # SENTIMENT ANALISIS
            prediction_emotion = modelEmotions.predict(tweetNoSW)
            sentiment = re.sub("__label__", "", prediction_emotion[0][0]);
            #print(sentiment);
            sentimentDF.loc[sentiment, "Counter"] += 1
        
        elif (language == "es"):
            print("Tweet detected to be spanish")

            # Separate text into individual words (only works for english -> punkt is pretrained for english)
            tweetTokens = toktok.tokenize(tweetCleaned)
            #print(tweetTokens)
            # Convert text tokens to lower case
            for i in range(len(tweetTokens)):
                tweetTokens[i] = tweetTokens[i].lower()
            print(tweetTokens)
            if(len(tweetTokens) == 0):
                print("It was an empty tweet, skipping")
                continue
            # Remove stop words (tweetTokensNo)(S)top(W)ords
            spanishStopWords = stopwords.words("spanish")
            tweetTokensNoSW = list(filter(lambda x: x not in spanishStopWords, tweetTokens))
            print(tweetTokensNoSW)
            if(len(tweetTokensNoSW)==0):
                continue
            tweetNoSW = ' '.join(tweetTokensNoSW)
            print(tweetNoSW)

            spamWordlistSpa = ["dinero", "oferta", "gratis", "muestras", "exclusivas", "descuento", "seleccionado", "sorteo", "compra", "ahora", "ahorra", "perder", "pierde", "peso", "rapido",
                            "comprar", "tickets", "entradas", "ganar", "click", "here", "aqui", "oportunidad", "oportunidades", "ganador", "miembro", "reclamar", "reclama", "link",
                            "confirma", "confirmar", "suscribete", "suscripcion", "responder", "tienda", "obten", "devolucion", "asegurada", "asegurar", "descuento", "viagra", "oderna",
                            "online", "llama", "acuerdo", "expirar", "expirar", "empezar", "empezado", "importante", "informacion", "instantaneo", "limitado", "tiempo", "nuevo", "cliente",
                            "clientes", "solo", "toda", "vida", "leer", "especial", "promocion", "quitar", "ultimo", "stock", "unidad", "unidades", "negociar", "chollo", "mejor", "ilimitado",
                            "hoy", "trato", "visita", "website", "web", "pagina", "evitar", "evita", "cancelar", "barato", "certificado", "felicidades", "credito", "tarjeta", "facil", "terminos",
                            "garantizar", "garantizado", "hosting", "info", "debito", "regalando", "unete", "miles", "millones", "edad", "mayor", "legal", "nude", "desnudo", "desnudos",
                            "mesaje", "masajes", "mensajes", "mensaje", "dm", "direct", "message", "rebaja", "rebajas", "ingreso", "urgente"]

            isSpam = 0
            for token in tweetTokensNoSW:
                if(token in spamWordlistSpa):
                    isSpam = isSpam + 1

            prob = isSpam/len(tweetTokensNoSW)*100

            if(prob >= spamSensitivity):
                print("Detected to be spam")
                spamTweetsCounter += 1
                #continue

        else:
            print("Unsupported language")
            unsupportedTweetsCounter += 1
        # TWEET LOCATION

        ############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION PROCESS FOR THE TWEETS ############
        DEBUG_CLASSIFICATION_COUNTRIES = False
        #########################################################################################
        
        #countryNamesTrans
        #countryNames
        #dfCountries.loc[word, "Counter"] += 1
        
        loc = tweet["user"]["location"]
        loc = unidecode.unidecode(loc)
        location = ""
        for countryName in list(countryNamesTrans.keys()):
            if(countryName in loc):
                location = countryNamesTrans.get(countryName)

        if(location == ""):
            for countryName in countryNames:
                if(countryName in re.sub("[,.]", "", loc).split()):
                    location = countryName

        if(location != ""):
            dfCountries.loc[location, "Counter"] += 1
        else: 
            unkownCountries += 1


    sentimentCols = px.bar(sentimentDF, x=sentiments, y='Counter')


    ############ DEBUG: DIPLAY THE COUNTRY CLASSIFICATION INFO FOR THE TWEETS ############
    DEBUG_CLASSIFIED_COUNTRIES = False
    if(DEBUG_CLASSIFIED_COUNTRIES):
        print(dfCountries)
        print("Number of tweets without contry:", unkownCountries)
        print(dfCountries.loc["Spain"])
    ######################################################################################
    #print(dfTweets)

    worldMap = px.choropleth(dfCountries, locations="Code",
                        color="Counter", color_continuous_scale=px.colors.sequential.Plasma)


    return ({}, {}, {"display": "none"}, {"display":"block"},'Tweets detected to be spam: \n{}'.format(spamTweetsCounter),
            'Tweets from unkown country: \n{}'.format(unkownCountries), 'Tweets in unsupported language: \n{}'.format(unsupportedTweetsCounter),
            'Tweets that are toxic: \n{}'.format(toxicTweetsCounter),
            worldMap, sentimentCols)

if __name__ == '__main__':
    app.run_server(debug=False)
