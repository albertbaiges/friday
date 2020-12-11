

# This python file provides a convenient way of retrieving a list of countries and 
# the list of Alpha-3 codes for this countries.

# countryName[i] has its alpha-3 code on countryCodes[i]

import requests
from lxml import html
import re

def country_aplha3_lists():
    response = requests.get("https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3")
    tree = html.fromstring(response.text)
    codes = tree.xpath('//div/div[@class="plainlist"]')
    fipsPairs = codes[0].text_content()[63:]
    fipsPairs = fipsPairs.replace(u'\xa0', u' ') # Prevents \xa0 between words
    fipsPairs = re.sub(" \(.*\)", "", fipsPairs)
    listFipsPairs = fipsPairs.split("\n")[:-1] # Up to -1 to remove a last empty string in the list
    countryCodes = []
    countryNames = []

    for i in range(len(listFipsPairs)):
        (code, *country) = listFipsPairs[i].split()
        countryCodes.append(code)
        countryNames.append(" ".join(country))

    return countryNames, countryCodes