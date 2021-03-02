#Extra/Helper Methods
from googletrans import Translator

def removeprefix(string, remove):
    return string[len(remove)+1:]

def langToCode(lang):
    #get lang as langcode
    tlang = lang
    if lang in googletrans.LANGUAGES:
        langName = googletrans.LANGUAGES[lang]
    elif lang in googletrans.LANGCODES:
        langName = lang
        tlang = googletrans.LANGCODES[lang]
    else: #bad input
        bad = True
        out = 'Enter a valid language code (ex: en, es, zh-cn) or the name of a language (ex: english, spanish, chinese (simplified)'
    print('eeeeeeeeeeeeeeeee')
    return tlang, langName, bad, out