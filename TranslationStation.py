#Translation Station Discord Bot
import os
import discord
import random
import googletrans
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
flagEmojis = {'en':'🇬🇧', 'es':'🇪🇸', 'ja':'🇯🇵', 'de':'🇩🇪', 'fr':'🇫🇷',
              'zh-cn':'🇨🇳', 'hi':'🇮🇳', 'ar':'🇸🇦', 'bn':'🇧🇩', 'ru':'🇷🇺',
              'pt':'🇵🇹', 'id':'🇮🇩'}
activeFlagEmojis = {'en':'🇬🇧', 'es':'🇪🇸', 'ja':'🇯🇵', 'de':'🇩🇪', 'fr':'🇫🇷',
                   'zh-cn':'🇨🇳', 'hi':'🇮🇳', 'ar':'🇸🇦', 'bn':'🇧🇩', 'ru':'🇷🇺'}
flagEmojisR = {i: d for d, i in activeFlagEmojis.items()}

#startup event
@client.event
async def on_ready():
    # for guild in client.guilds:
    #     if guild.name == GUILD: #find our server
    #         break
    guild = discord.utils.get(client.guilds, name = GUILD)
    
    print( #display bot name and server info
        f'{client.user} is connected to the following guild: '
        f'{guild.name} (id: {guild.id})'
    )

    print ('Members: ' + ', '.join([member.name for member in guild.members]))

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
    if message.author == client.user: return #ignore bot's own messages
    if message.channel.name == 'test': return #ignore test channel

    #Commands
    if message.content.startswith('*'):
        command = message.content[1:]

        #Lang roles self-service
        if command == 'langs':# and message.channel.name == 'choose_language':
            m = await message.channel.send('React to this message to choose your language(s).')
            for flag in flagEmojis:
                await m.add_reaction(activeFlagEmojis.get(flag))

        elif command.startswith('addlang'):
            print('nice')
            lang = message.content[len('addlang ')+1:]
            print(lang)
    
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
                name = googletrans.LANGUAGES[flagEmojisR.get(reaction.emoji)]))

#handle errors - catch bad message and write to file
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Undhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)