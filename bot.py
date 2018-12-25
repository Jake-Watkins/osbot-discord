#Version 0.1
import discord
from urllib.request import urlopen
import sys
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime
import traceback
import git
import os

TOKEN = 'NTIzOTUxNDczMjEwNTU2NDE2.DvhEDA.cBUM5PjFaVPgDWLd-PNVXP3qsz8'

##probably want to move this to local storage to not make too many reqeusts
##and just update once a day
ItemIdDBUrl = "https://rsbuddy.com/exchange/names.json"
PriceUrl = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item="
client = discord.Client()
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('OsBot.json', scope)
gspreadclient = gspread.authorize(creds)
sheet = gspreadclient.open('CC Drops').sheet1
pp = pprint.PrettyPrinter()
cwd = os.getcwd()
g = git.cmd.Git(cwd)
message = ""

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
def convertToNumber(st):
    multiplier = 1
    if(st[-1]=='k'):
        multiplier = 1000
        st = st[:-1]
    elif(st[-1]=='m'):
        multiplier = 1000000
        st = st[:-1]
    elif(st[-1]=='b'):
        multiplier = 1000000000
        st = st[:-1]
    return int(float(st) * multiplier)


def findValue(id):
    price = 0
    with urlopen(PriceUrl + id) as url:
        data = json.loads(url.read().decode())
    price = str(data['item']['current']['price'])
    value = convertToNumber(price.lower().strip())
    return price, value



@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('$update'):
            await client.send_message(message.channel, 'updating...'.format(message))
            await client.send_message(message.channel, 'pulling...'.format(message))
            g.pull ()
            await client.send_message(message.channel, 'restarting...'.format(message))

            os.execl(sys.executable, sys.executable, *sys.argv)

    if message.content.startswith('$help'):
        msg = '$help, $listdrops, $add, $lookup, $update'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.lower().startswith('$listdrops'):
        id = message.mentions[0].id
        idcol = sheet.col_values(1)
        droplist = []
        for i in range(1, len(idcol)):
            if id == idcol[i]:
                row = sheet.row_values(i+1)
                droplist.append(row)

        for row in droplist:
            new_row = []
            new_row.append("[" + row[1] + "](" + row[3] + ")")
            await client.send_message(message.channel, new_row)


    if message.content.lower().startswith('$test'):

        msg = {
    "content": "this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```",
    "embed": {
    "title": "title ~~(did you know you can have markdown here too?)~~",
    "description": "this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```",
    "url": "https://discordapp.com",
    "color": 4353867,
    "timestamp": "2018-12-25T18:03:23.735Z",
    "footer": {
    "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png",
    "text": "footer text"
    },
    "thumbnail": {
    "url": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "image": {
    "url": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "author": {
    "name": "author name",
    "url": "https://discordapp.com",
    "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "fields": [
    {
    "name": "🤔",
    "value": "some of these properties have certain limits..."
    },
    {
    "name": "😱",
    "value": "try exceeding some of them!"
    },
    {
    "name": "🙄",
    "value": "an informative error should show up, and this view will remain as-is until all issues are fixed"
    },
    {
    "name": "<:thonkang:219069250692841473>",
    "value": "these last two",
    "inline": true
    },
    {
    "name": "<:thonkang:219069250692841473>",
    "value": "are inline fields",
    "inline": true
    }
    ]
    }
    }
        await client.send_message(message.channel, msg)


    if message.content.lower().startswith('$add'):
        item, link = processMessage(message.content)
        try :
            ##check if valid link
            urlopen(link)

            print('link is valid')
            ##check if valid item & price

            ItemId = finditemId(item)

            print('item is valid: '  + ItemId)

            #find value of item

            shortprice,value = findValue(ItemId)
            print("price is valid")
            msg = 'Adding '+ item +' to user {0.author.mention}'.format(message) + ' value: ' + shortprice
            print("message is valid")
            now = datetime.datetime.now()
            date = [str(now.month),'/' ,str(now.day),'/', str(now.year)]
            row = [message.author.id,item, value, link, "".join(date)]
            sheet.insert_row(row, 2)
            await client.send_message(message.channel, msg)

        except:
            traceback.print_exc()
            print("Unexpected error:", sys.exc_info()[0])
            msg = 'last item was not a valid link, please try again with format $add item name link: '.format(message)
            await client.send_message(message.channel, msg)


    if message.content.lower().startswith('$lookup'):
        id = message.mentions[0].id
        idcol = sheet.col_values(1)
        pcol = sheet.col_values(3)
        sum = 0
        for i in range(1, len(idcol)):
            if id == idcol[i]:
                sum = sum + int(pcol[i].replace(',', ""))

        msg = '{0.author.mention}'.format(message) + " has contributed " + str("{:,}".format(sum))+ "gp total"

        await client.send_message(message.channel, msg)



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for server in client.servers:
        for channel in server.channels:
            if channel.permissions_for(client.user).send_messages:  
                await client.send_message(channel,  'started succesfully'.format(message))
    

client.run(TOKEN)
