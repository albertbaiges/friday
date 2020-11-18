
import pandas as pd
import re


dataset = pd.read_csv("text_emotion.csv")

#print(dataset)

dataset = dataset.drop(["tweet_id", "author"], axis = "columns")

#print(dataset)

f = open("training_emotions.txt", "wt")
print("Printing the strings in content")
sentiments = []
contents = []
for (label, content) in dataset.items():
    #print(label)
    for index, value in content.items():
        if(label == "sentiment"):
            sentiments.append(value)
        else:
            #print(value)
            valueCleaned = re.sub("(@[A-Za-z0-9_-]*[ ])|(#[A-Za-z0-9_-]*[ ])|(http[s]*[.:/A-Za-z0-9_-]*|[.,;:])|[^a-zA-Z ]", "", value)
            contents.append(valueCleaned)

for i in range(len(sentiments)):
    f.write("__label__" + sentiments[i] + " " + contents[i] + "\n")

f.close()
