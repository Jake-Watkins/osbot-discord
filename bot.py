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

def loadItems():
    data = ""
    with urlopen(ItemIdDBUrl) as url:
        data = json.loads(url.read().decode())
    return data

data = loadItems()

def splitMessage(str):
    items = str.split(' ')
    return items, len(items)

def processMessage(str):
    link = str.split(' ')[-1]
    item = str.rsplit(' ', 1)[0].split(' ', 1)[1]
    return item, link

def finditemId(data, str):
    id = -1
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

    (items, length) = splitMessage(message)

    if message.content.startswith('$update'):
            client.change_presence(game = discord.Game(name = "updating"), status = discord.Status("idle"), afk = True)
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
        embed = discord.Embed(title="Drops", description="", color=0x00ff00)
        for row in droplist:
            new_row = []
            embed.add_field(value=row[2] +" : ["+row[4] + "](" + row[3] + ")", name=row[1], inline=False)

        await client.send_message(message.channel, embed=embed)

    if message.content.lower().startswith('$test'):
        await client.send_message(message.channel, "testing".format(message))

        await client.send_message(message.channel, "finished testing".format(message))


    if message.content.lower().startswith('$add'):
        item, link = processMessage(message.content)
        try :
            ##check if valid link
            urlopen(link)

            print('link is valid')
            ##check if valid item & price

            ItemId = finditemId(data, item)

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
    client.change_presence(game = None, status = None, afk = False)

client.run(TOKEN)
