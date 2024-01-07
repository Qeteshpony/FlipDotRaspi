import unidecode
from flipdot.fonts import narrow as font

def converter(text):
    newtext = ""
    for c in text:
        if c not in font.keys():
            c = unidecode.unidecode(c)
        newtext += c
    return newtext
