#Extra/Helper Methods

def removeprefix(string, remove):
    return string[len(remove)+1:]

helpText = '''
**Welcome to Translation Station Help!**

__User Commands__
*langs\t-\tasdf

__Admin Commands__
*for language names, use either its code (id) or its name (indonesian)*

*alangs\t-\tprint active and inactive languages
*addlang [lang]\t-\tmake a language active
*rlang [lang]\t-\tmake a language inactive

*addcat [name]\t-\tadd category
*rcat [name]\t-\tremove category

*stop\t-\tshut down bot
'''