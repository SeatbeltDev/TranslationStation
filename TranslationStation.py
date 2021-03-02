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

#startup event
@client.event
async def on_ready():
    global activeLangs

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

#welcome new members through DM
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
    guild = discord.utils.get(client.guilds, name = GUILD)

    if message.author == client.user: return #ignore bot's own messages
    if message.channel.name == 'test': return #ignore test channel

    #Commands
    if message.content.startswith('*'):
        command = message.content[1:]

        #Lang roles self-service
        if command == 'langs':# and message.channel.name == 'choose_language':
            m = await message.channel.send('React to this message to choose your language(s).')
            for lang in activeLangs:
                await m.add_reaction(flagEmojis[lang])

        elif command.startswith('addlang'):
            lang = removeprefix(command, 'addlang').lower()
            
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

            #create channel
            # print(guild.categories)
            # print(guild.categories.get(name = 'General'))
            # await guild.create_text_channel(langName,
                # category = guild.categories.get(name = 'GENERAL'))
            # await guild.create_text_channel(langName,
                # category = guild.categories.get(name = 'GENERAL'))

            await message.channel.send(f'**{langName.title()}** role and channels successfully created')
        
        elif command.startswith('rlang'):
            lang = removeprefix(command, 'rlang').lower()

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

            #delete role
            if lang not in activeLangs:
                await message.channel.send(f'**{langName.title()}** is not an active language')
                return

            #delete role
            activeLangs.remove(lang)
            await role.delete()
            await message.channel.send(f'Removed **{langName.title()}** role and channels')
            
            #delete channels
            pass

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
            trans = t.translate(message.content,
                dest = googletrans.LANGCODES[ch.name]).text
            response = f'{message.author}: {trans}'
            await ch.send(response)
        await message.add_reaction('✅')
    
    #SIMPLE TRANSLATE EN>ES
    # trans = t.translate(message.content, dest = 'es').text
    # response = f'{message.author}: {trans}'
    # channel = client.get_channel(803733879391256587) #change channel
    # await channel.send(response)
    # await message.add_reaction('✅')

#Respons to reactions
@client.event
async def on_reaction_add(reaction, user):
    #print(user.name)
    if user == client.user: return

    if reaction.message.content == 'React to this message to choose your language(s).':
        if reaction.emoji in flagEmojisR:
            await user.add_roles(get(user.guild.roles,
                name = googletrans.LANGUAGES[flagEmojisR[reaction.emoji]]))

#handle errors - catch bad message and write to file
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Undhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)