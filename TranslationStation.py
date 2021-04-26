#Translation Station Discord Bot
import os
import discord
import googletrans
import csv
from dotenv import load_dotenv
from googletrans import Translator
from discord.utils import get
from extra import *


#global vars from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
t = Translator()

intents = discord.Intents.all() #give bot all intents/permissions
client = discord.Client(intents = intents)

#Globals
# english, spanish, japanese, germna, french, chinese (simplified),
# hindi, arabic, bengali, russian, portuguese, indonesian
flagEmojis = {'en':'🇬🇧', 'es':'🇪🇸', 'ja':'🇯🇵', 'de':'🇩🇪', 'fr':'🇫🇷', 'zh-cn':'🇨🇳',
              'hi':'🇮🇳', 'ar':'🇸🇦', 'bn':'🇧🇩', 'ru':'🇷🇺', 'pt':'🇵🇹', 'id':'🇮🇩',
              'af':'🇿🇦', 'haw':'🏝️', 'ko':'🇰🇷', 'he':'🇮🇱', 'ga':'🇮🇪', 'it':'🇮🇹',
              'is':'🇮🇸', 'vi':'🇻🇳'}
flagEmojisR = {i: d for d, i in flagEmojis.items()}
activeLangsDict = {} #['en', 'es', 'ja', 'de', 'fr', 'zh-cn', 'hi', 'ar', 'bn', 'ru']
tCategoriesDict = {}

#Startup event
@client.event
async def on_ready():
    global activeLangsDict
    global tCategoriesDict
    
    # guild = discord.utils.get(client.guilds, name = GUILD)
    for g in client.guilds:
        guild = g
    
        print( #display bot name and server info
            f'{client.user} is connected to the following guild: '
            f'{guild.name} (id: {guild.id})'
        )

        print('Members: ' + ', '.join([member.name for member in guild.members]))

        # Startup Prep

        # TODO FIX LANGS WITH PARENTHESES NON-MANUALLY
        # for lang in googletrans.LANGCODES:
        #     if '(' in lang:
        #         print(f'old name: "{lang}"')
        #         newName = ''
        #         for char in lang:
        #             if char == ' ':
        #                 continue
        #             elif char == '(':
        #                 newName += '-'
        #                 continue
        #             elif char == ')':
        #                 continue
        #             newName += char
        #         print(f'new name: "{newName}"')

        #         langCode = googletrans.LANGCODES[lang]
        #         print(f'Setting LANGUAGES[{langCode}] = {newName}')
        #         googletrans.LANGUAGES[langCode] = newName
        #         print(f'Setting LANGCODES[{newName}] = {langCode}')
        #         googletrans.LANGCODES[newName] = langCode
        #         print(f'{langCode}/{langName} modified')
        googletrans.LANGUAGES['zh-cn'] = 'chinese-simplified'
        googletrans.LANGCODES['chinese-simplified'] = 'zh-cn'
        googletrans.LANGUAGES['zh-tw'] = 'chinese-traditional'
        googletrans.LANGUAGES['chinese-traditional'] = 'zh-tw'
        googletrans.LANGUAGES['ku'] = 'kurdish-kurmanji'
        googletrans.LANGUAGES['kurdish-kurmanji'] = 'ku'
        googletrans.LANGUAGES['my'] = 'myanmar-burmese'
        googletrans.LANGCODES['myanmar-burmese'] = 'my'

        print('Translated categories:')
        tCategoriesDict[guild] = []
        for cat in guild.categories:
            if '↔' in cat.name:
                tCategoriesDict[guild].append(cat)
                print(cat.name)

        print('Active languages:')
        if (len(tCategoriesDict[guild]) == 0):
            print('Loading active languages from memory')
            try:
                with open(f'{guild}_data.csv', newline = '') as data:
                        dataRead = csv.reader(data, delimiter = ' ', quotechar = '|')
                        for row in dataRead:
                            activeLangsDict[g] = row
                            print(activeLangsDict[g])
            except:
                activeLangsDict[g] = []
                print(f'No {guild}_data.csv file. Active languages set to none')
        else:
            activeLangsDict[g] = []
            for lang in tCategoriesDict[guild][0].channels:
                langName = lang.name
                langCode = googletrans.LANGCODES[langName]
                # print(f'{langName}, {langCode}')
                activeLangsDict[g].append(langCode)
            print(activeLangsDict[g])

        botChannel = discord.utils.get(guild.channels, name = 'general')
        await botChannel.send('Howdy! Type *help for help.')
        print('Bot ready!')
    
# REMOVED, unnecessary 
# Welcome new members through DM
# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     guild = discord.utils.get(client.guilds, name = GUILD)

#     await member.dm_channel.send(
#         f'Hey {member.name}! Welcome to {guild.name}.'
#     )

#Translate on message
@client.event
async def on_message(message):
    global activeLangsDict
    global tCategoriesDict
    # guild = discord.utils.get(client.guilds, name = GUILD)
    guild = message.guild

    # if message.author == client.user: return #ignore bot's own messages
    if message.author.bot: return #ignore bot's own messages

    #Commands
    if message.content.startswith('*'):
        command = message.content[1:].lower()
        
        #General User Commands
        
        if command == 'help':
            await message.channel.send(helpText)

        elif command == 'langs':
            aLangsNames = langCodesListToString(activeLangsDict[guild])
            if aLangsNames == '': aLangsNames = 'None'

            m = await message.channel.send(f'Active languages: `{aLangsNames}`\nReact to this message to choose your language(s).')
            for lang in activeLangsDict[guild]:
                await m.add_reaction(flagEmojis[lang])
        
        elif command == 'mylangs':
            myLangs = []

            for role in message.author.roles:
                if role.name in googletrans.LANGCODES:
                    roleCode = googletrans.LANGCODES[role.name]

                    if roleCode in activeLangsDict[guild]:
                        myLangs.append(roleCode)

            myLangsString = ''
            if len(myLangs) > 0:
                myLangsString = langCodesListToString(myLangs)
            else:
                myLangsString = 'None'

            m = await message.channel.send(f'{message.author.name}\'s languages: `{myLangsString}`\nClick a reaction to remove a language.')
            
            for lang in myLangs:
                await m.add_reaction(flagEmojis[lang])

        #Admin Commands
        
        elif not message.author.permissions_in(message.channel).administrator:
            # stop here if user doesn't have 'Admin' role
            print(f'{message.author.name} tried to use "{message.content}" command.')
            await message.channel.send('You do not have permission to use that command.')
            return

        elif command == 'info':
            await message.channel.send(f'Guild: {client.guilds}')

        elif command == 'alangs':
            aLangsNames = langCodesListToString(activeLangsDict[guild])
            if aLangsNames == '': aLangsNames = 'None'
            unusedLangs = list(set(flagEmojis.keys()) - set(activeLangsDict[guild]))
            unusedLangsPretty = langCodesListToString(unusedLangs)
            await message.channel.send(f'Active languages: \n`{aLangsNames}`\nLangs not used: \n`{unusedLangsPretty}`')#\nTranslated Categories: {tCategories}')

        elif command.startswith('emb'):
            pass
            # msg = removeprefix(command, 'emb')

            # embed = discord.Embed(description = msg)
            
            # embed.set_author(name = message.author.display_name,
            #     icon_url = message.author.avatar_url)
            
            # await message.channel.send(embed = embed)

        elif command.startswith('th'):
            # Testing webhooks
            # This isn't going to work for the final product
            pass

            # msg = removeprefix(command, 'th')

            # print(f'About to try sending webhook msg: {msg}')
            # profilePic = await message.author.avatar_url.read()
            # print('middle')
            # webhook = await message.channel.create_webhook(name = message.author.display_name, avatar = profilePic)

            # print(f'Sending webhook message: {msg}')
            # await webhook.send(msg)
            # await webhook.delete()

        elif command.startswith('addcat'):
            categoryName = removeprefix(command, 'addcat') + ' ↔'

            newCategory = await guild.create_category(categoryName)
            tCategoriesDict[guild].append(newCategory)

            #create channel and set view permissions
            print(f'Active langs: {activeLangsDict[guild]}')
            for lang in activeLangsDict[guild]:
                # print(f'Adding {lang}')
                chan = await newCategory.create_text_channel(googletrans.LANGUAGES[lang])
                role = discord.utils.get(guild.roles, name = chan.name)

                #default role cannot view
                await chan.set_permissions(guild.default_role, view_channel = False)
                #lang role can view
                await chan.set_permissions(role, view_channel = True)
            
            print(f'{newCategory} category created and populated with active language categories.')
        
        elif command.startswith('rcat'):
            categoryName = removeprefix(command, 'rcat') + ' ↔'

            #TODO clean up, get category from tCategories[] instead of just grabbing it
            cat = discord.utils.get(tCategoriesDict[guild], name = categoryName)
            
            #delete all channels in cat first
            for chan in cat.channels:
                await chan.delete()

            #delete cat
            await cat.delete()
            tCategoriesDict[guild].remove(cat)

            await message.channel.send(f'{cat} category removed.')

        elif command.startswith('addlangs'):
            pass
            # langs = removeprefix(command, 'addlang').split()

            # for lang in langs:
            #     msg = f'*addlang {lang}'
            #     print(f'Calling message: ({msg})')
            #     # msg = discord.Message(content = '*')
            #     print(f'Message object: {msg}')
            #     await on_message(msg)

        elif command.startswith('addlang'):
            #maybe allow multiple langs i.e. 'addlang id pt'
            lang = removeprefix(command, 'addlang')
            
            #get lang as langcode
            if lang in googletrans.LANGUAGES:
                langName = googletrans.LANGUAGES[lang]
            elif lang in googletrans.LANGCODES:
                langName = lang
                lang = googletrans.LANGCODES[lang]
            else: #bad input
                await message.channel.send('Enter a valid language code (ex: en, es, zh-cn) or the name of a language (ex: english, spanish, chinese (simplified)')
                return

            if lang in activeLangsDict[guild]: #lang already active
                    await message.channel.send(f'**{langName.title()}** is already an active language')    
                    return

            '''Automate setup for new lang'''
            
            activeLangsDict[guild].append(lang)

            #create role
            await guild.create_role(name = langName) #add random color would be nice
            print(f'{langName.title()} role created')

            #create channels
            for cat in tCategoriesDict[guild]:
                chan = await cat.create_text_channel(langName)
                role = discord.utils.get(guild.roles, name = chan.name)

                #default role cannot view
                await chan.set_permissions(guild.default_role, view_channel = False)
                #lang role can view
                await chan.set_permissions(role, view_channel = True)
            print(f'{langName.title()} channels created')

            await message.channel.send(f'**{langName.title()}** role and channels successfully created')

        elif command.startswith('rlang'):
            #maybe multiple langs i.e. 'rlang id pt'
            lang = removeprefix(command, 'rlang')
            print(f'Removing lang: {lang}')

            #get lang as langcode (copy/pasted from addlang)
            if lang in googletrans.LANGUAGES:
                langName = googletrans.LANGUAGES[lang]
            elif lang in googletrans.LANGCODES:
                langName = lang
                lang = googletrans.LANGCODES[lang]
            else: #bad input
                await message.channel.send('Enter a valid language code (ex: en, es, zh-cn) or the name of a language (ex: english, spanish, chinese (simplified)')
                return

            role = discord.utils.get(guild.roles, name = langName)

            if lang not in activeLangsDict[guild]:
                await message.channel.send(f'**{langName.title()}** is not an active language')
                return

            #remove from active
            activeLangsDict[guild].remove(lang)

            #delete role
            print(f'langname: {langName}')
            await role.delete()
            await message.channel.send(f'Removed **{langName.title()}** role and channels')

            #delete channels
            for cat in tCategoriesDict[guild]:
                for chan in cat.channels:
                    if chan.name == langName:
                        await chan.delete()
                # await cat.create_text_channel(langName)
            print(f'{langName.title()} channels removed')

        elif command == 'stop':
            for g in client.guilds:
                print(f'Saving data for server: {g}')
                
                with open(f'{message.guild}_data.csv', 'w', newline = '') as data:
                    dataWrite = csv.writer(data, delimiter = ' ', quotechar = '|')
                    dataWrite.writerow(activeLangsDict[g])

            await message.channel.send('Buh bye!')
            await client.close()
            print('Bot shut down')
    

    #Other events
    else:
        #Translate and send to each language channel in station
        for ch in message.channel.category.channels:
            if ch == message.channel: continue #ignore message's channel
            if ch.name not in googletrans.LANGCODES: continue #ignore non lang channels

            translatedMsg = t.translate(message.content,
                dest = googletrans.LANGCODES[ch.name]).text
            
            # TEXT OPTION
            # response = f'{message.author}: {translatedMsg}'
            # await ch.send(response)

            # EMBED OPTION
            embed = discord.Embed(description = translatedMsg)
            
            embed.set_author(name = message.author.display_name,
                icon_url = message.author.avatar_url)
            
            await ch.send(embed = embed)

            # WEBHOOK OPTION
            # profilePic = await message.author.avatar_url.read()
            # webhook = await ch.create_webhook(name = message.author.display_name, avatar = profilePic)

            # await webhook.send(translatedMsg)
            # await webhook.delete()

        await message.add_reaction('✅')


#Respond to reactions
@client.event
async def on_reaction_add(reaction, user):
    #print(user.name)
    if user == client.user: return

    if 'React to this message to choose your language(s).' in reaction.message.content:
        if reaction.emoji in flagEmojisR:
            await user.add_roles(get(user.guild.roles,
                name = googletrans.LANGUAGES[flagEmojisR[reaction.emoji]]))

    if 'Click a reaction to remove a language.' in reaction.message.content:
        if reaction.emoji in flagEmojisR:
            await user.remove_roles(get(user.guild.roles,
                name = googletrans.LANGUAGES[flagEmojisR[reaction.emoji]]))

#Handle errors - catch bad message and write to file
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Undhandled message: {args[0]}\n')
        else:
            pass #raise

client.run(TOKEN)