#Version 0.1
import discord
from urllib.request import urlopen
import sys

TOKEN = 'NTIzOTUxNDczMjEwNTU2NDE2.DvhEDA.cBUM5PjFaVPgDWLd-PNVXP3qsz8'

client = discord.Client()

def processMessage(string):
    link = string.split(" ")[-1]
    item = string.rsplit(' ', 1)[0].split(' ', 1)[1]
    return item, link


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

            ##check if valid item & price
            


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
