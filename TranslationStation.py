#Translation Station Discord Bot
import os
import discord
import random
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
              'hi':'🇮🇳', 'ar':'🇸🇦', 'bn':'🇧🇩', 'ru':'🇷🇺', 'pt':'🇵🇹', 'id':'🇮🇩'}
flagEmojisR = {i: d for d, i in flagEmojis.items()}
activeLangs = ['en', 'es', 'ja', 'de', 'fr', 'zh-cn', 'hi', 'ar', 'bn', 'ru']
tCategories = []

#Startup event
@client.event
async def on_ready():
    global activeLangs
    global tCategories

    # for guild in client.guilds:
    #     if guild.name == GUILD: #find our server
    #         break
    guild = discord.utils.get(client.guilds, name = GUILD)
    
    print( #display bot name and server info
        f'{client.user} is connected to the following guild: '
        f'{guild.name} (id: {guild.id})'
    )

    print ('Members: ' + ', '.join([member.name for member in guild.members]))

    print('Active languages:')
    with open('data.csv', newline = '') as data:
                dataRead = csv.reader(data, delimiter = ' ', quotechar = '|')
                for row in dataRead:
                    activeLangs = row
                    print(activeLangs)
    
    print('Translated categories:')
    for cat in guild.categories:
        if '↔' in cat.name:
            tCategories.append(cat)
            print(cat.name)

    botChannel = discord.utils.get(guild.channels, name = 'bot_commands')
    await botChannel.send('Howdy')
    

#Welcome new members through DM
@client.event
async def on_member_join(member):
    await member.create_dm()
    guild = discord.utils.get(client.guilds, name = GUILD)

    await member.dm_channel.send(
        f'Hey {member.name}! Welcome to {guild.name}.'
    )

#Translate on message
@client.event
async def on_message(message):
    global activeLangs
    global tCategories
    guild = discord.utils.get(client.guilds, name = GUILD)

    # if message.author == client.user: return #ignore bot's own messages
    if message.author.bot: return #ignore bot's own messages

    #Commands
    if message.content.startswith('*'):
        command = message.content[1:].lower()
        
        #General User Commands
        
        if command == 'help':
            await message.channel.send(helpText)

        elif command == 'langs':
            m = await message.channel.send('React to this message to choose your language(s).')
            for lang in activeLangs:
                await m.add_reaction(flagEmojis[lang])
        
        elif command == 'alangs':
            unusedLangs = list(set(flagEmojis.keys()) - set(activeLangs))
            await message.channel.send(f'Active languages: {activeLangs}\nLangs not used: {unusedLangs}')#\nTranslated Categories: {tCategories}')
        
        #Admin Commands

        elif discord.utils.get(message.author.roles, name = 'Admin') is None:
            # stop here if user doesn't have 'Admin' role
            print(f'{message.author.name} tried to use "{message.content}" command.')
            await message.channel.send('You do not have permission to use that command.')
            return

        elif command.startswith('emb'):
            msg = removeprefix(command, 'emb')

            embed = discord.Embed(description = msg)
            
            embed.set_author(name = message.author.display_name,
                icon_url = message.author.avatar_url)
            
            await message.channel.send(embed = embed)

        elif command.startswith('th'):
            # Testing webhooks
            # This isn't going to work for the final product

            msg = removeprefix(command, 'th')

            print(f'About to try sending webhook msg: {msg}')
            profilePic = await message.author.avatar_url.read()
            print('middle')
            webhook = await message.channel.create_webhook(name = message.author.display_name, avatar = profilePic)

            print(f'Sending webhook message: {msg}')
            await webhook.send(msg)
            await webhook.delete()

        elif command.startswith('addcat'):
            categoryName = removeprefix(command, 'addcat') + ' ↔'

            newCategory = await guild.create_category(categoryName)
            tCategories.append(newCategory)

            #create channel and set view permissions
            for lang in activeLangs:
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
            cat = discord.utils.get(tCategories, name = categoryName)
            
            #delete all channels in cat first
            for chan in cat.channels:
                await chan.delete()

            #delete cat
            await cat.delete()
            tCategories.remove(cat)

            await message.channel.send(f'{cat} category removed.')

        elif command.startswith('addlangs'):
            langs = removeprefix(command, 'addlang').split()

            for lang in langs:
                msg = f'*addlang {lang}'
                print(f'Calling message: ({msg})')
                # msg = discord.Message(content = '*')
                print(f'Message object: {msg}')
                await on_message(msg)

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

            if lang in activeLangs: #lang already active
                    await message.channel.send(f'**{langName.title()}** is already an active language')    
                    return

            '''Automate setup for new lang'''
            
            activeLangs.append(lang)

            #create role
            await guild.create_role(name = langName) #add random color would be nice
            print(f'{langName.title()} role created')

            #create channels
            for cat in tCategories:
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

            if lang not in activeLangs:
                await message.channel.send(f'**{langName.title()}** is not an active language')
                return
            
            #remove from active
            activeLangs.remove(lang)

            #delete role
            await role.delete()
            await message.channel.send(f'Removed **{langName.title()}** role and channels')
            
            #delete channels
            for cat in tCategories:
                for chan in cat.channels:
                    if chan.name == langName:
                        await chan.delete()
                # await cat.create_text_channel(langName)
            print(f'{langName.title()} channels removed')

        elif command == 'stop':
            print('Saving data...')
            
            with open('data.csv', 'w', newline = '') as data:
                dataWrite = csv.writer(data, delimiter = ' ', quotechar = '|')
                dataWrite.writerow(activeLangs)

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

            response = f'{message.author}: {translatedMsg}'
            await ch.send(response)

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

    if reaction.message.content == 'React to this message to choose your language(s).':
        if reaction.emoji in flagEmojisR:
            await user.add_roles(get(user.guild.roles,
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