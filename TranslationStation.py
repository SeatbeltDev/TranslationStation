#Translation Station Discord Bot
import os
import discord
import random
import googletrans
from dotenv import load_dotenv
from googletrans import Translator


#global vars from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
t = Translator()

intents = discord.Intents.all() #give bot all intents/permissions
client = discord.Client(intents = intents)

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

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return #ignore bot's own messages

#     quotes = [
#         'bababooey',
#         'bruh',
#         'mama mia'
#     ]

#     if message.channel.id == '803685130257301534':
#         response = 'asdfasdf'
#         await message.channel.send(response)
#     elif message.content == 'e':
#         #respond to 'e' with a random quote
#         response = random.choice(quotes)
#         await message.channel.send(response)
#     elif message.content == 'raise-exception':
#         raise discord.DiscordException

#test translate
@client.event
async def on_message(message):
    if message.author == client.user:
        return #ignore bot's own messages
    
    if message.channel.name == 'bot_test':#786722399482937355:
        print('nice')
        #await message.channel.send('nice')
    #hello
    print(googletrans.LANGCODES[message.channel.name])

    print(message.channel.category.channels)
    for ch in message.channel.category.channels:
        # if(ch == message.channel): continue
        print('asivuy3ris')
        print(ch.name)
        print(googletrans.LANGCODES[ch.name])
        trans = t.translate(message.content,
            dest = googletrans.LANGCODES[ch.name]).text
        response = f'{message.author}: {trans}'
        await ch.send(response)
        await message.add_reaction('✅')
        

    # trans = t.translate(message.content, dest = 'es').text
    # response = f'{message.author}: {trans}'
    # channel = client.get_channel(803733879391256587) #change channel
    # await channel.send(response)
    # await message.add_reaction('✅')
    

#handle errors - catch bad message and write to file
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Undhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)