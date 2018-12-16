#Version 0.1
import discord
from urllib.request import urlopen
import sys
import json

TOKEN = 'NTIzOTUxNDczMjEwNTU2NDE2.DvhEDA.cBUM5PjFaVPgDWLd-PNVXP3qsz8'

##probably want to move this to local storage to not make too many reqeusts
##and just update once a day
ItemIdDBUrl = "https://rsbuddy.com/exchange/names.json"



client = discord.Client()

def processMessage(str):
    link = str.split(" ")[-1]
    item = str.rsplit(' ', 1)[0].split(' ', 1)[1]
    return item, link

def finditemId(str):
    id = -1
    data = ""
    with urlopen(ItemIdDBUrl) as url:
        data = json.loads(url.read().decode())


    for item in data:
        #print(data[item]['name'])
        if(data[item]['name'].lower()==str.lower()):
            return item

    print(str)
    return id

def findValue(id):
    return 0

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        msg = 'need to impliment'.format(message)
        await client.send_message(message.channel, msg)


    if message.content.startswith('$add'):
        item, link = processMessage(message.content)
        try :
            ##check if valid link
            urlopen(link)

            print('link is valid')
            ##check if valid item & price

            ItemId = finditemId(item)

            print('item is valid: '  + ItemId)

            #find value of item

            value = findValue(ItemId)

            msg = 'Adding '+ item +' to user {0.author.mention}'.format(message)
            await client.send_message(message.channel, msg)

        except:
            print("Unexpected error:", sys.exc_info()[0])
            msg = 'last item was not a valid link, please try again with format $add item name link: '.format(message)
            await client.send_message(message.channel, msg)


    if message.content.startswith('$lookup'):
        msg = 'need to impliment'.format(message)
        await client.send_message(message.channel, msg)



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
