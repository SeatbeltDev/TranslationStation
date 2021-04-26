#Extra/Helper Methods
import googletrans

def removeprefix(string, remove):
    return string[len(remove)+1:]

# Takes in a list of langcodes, outputs string of capitalized languages separated by spaces
def langCodesListToString(langs):
    outList = ''
    for lang in langs:
        outList += f'{googletrans.LANGUAGES[lang].title()}, '
    return outList[:-2]

helpText = '''
**Welcome to Translation Station Help!**
Translation Station is a bot that translates messages.

__Users' Quick-Start Guide__
    Use `*langs` to see active languages and pick the ones you want to see
    Use `*mylangs` to see you languages and remove any you don't want

__Admins' Quick-Start Guide__
    Use `*alangs` to see all possible languages and `*addlang (language)` to add one at a time.
    Use `*addcat (name)` to add a category.
    You may remove languages or categories at any time with `*rlang` and `*rcat`.
    DO NOT remove categories or language roles manually. Use the bot's commands.


__User Commands__
`*help`\t-\tshow this message

`*langs`\t-\tshow active languages and choose which ones you want to see
`*mylangs`\t-\tshow your chosen languages and remove any

__Admin Commands__
*for language names, use either its code (id) or its name (indonesian)*

`*alangs`\t-\tshow all active and inactive languages
`*addlang (language)`\t-\tmake a language active
`*rlang (language)`\t-\tmake a language inactive

`*addcat (name)`\t-\tadd category
`*rcat (name)`\t-\tremove category

`*stop`\t-\tshut down bot
'''