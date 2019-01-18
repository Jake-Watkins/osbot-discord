#Version 0.1
import discord
from urllib.request import urlopen, Request
import sys
import io
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime
import traceback
import git
import os
import math
from bs4 import BeautifulSoup as soup
from operator import itemgetter

TOKEN = 'NTIzOTUxNDczMjEwNTU2NDE2.DvhEDA.cBUM5PjFaVPgDWLd-PNVXP3qsz8'

##probably want to move this to local storage to not make too many reqeusts
##and just update once a day
ItemIdDBUrl = "https://rsbuddy.com/exchange/names.json"
PriceUrl = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item="
getracker = "https://ge-tracker.com/item/"
hiscoreURL = "http://crystalmathlabs.com/tracker/track.php?player="
updateCMLURL = "https://crystalmathlabs.com/tracker/update.php?player="
client = discord.Client()
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('OsBot.json', scope)
gspreadclient = gspread.authorize(creds)
sheet = gspreadclient.open('CC Drops').sheet1
listSheet = gspreadclient.open('to get list').sheet1
pp = pprint.PrettyPrinter()
cwd = os.getcwd()
g = git.cmd.Git(cwd)
EHPURL = cwd+'/Supplies Calculator - Old School RuneScape XP Tracker - Crystal Math Labs.html'
message = ""

def getEHPrates():
    EHPdict = {}
    pagesoup = soup(open(EHPURL), "html.parser")
    ttp = pagesoup.find("div",{"id":"ehprates"}).text
    ttp = ttp[ttp.find('Attack'):]
    ttp = ttp[ttp[1:].find('Attack')+1:]
    ttp = ttp[ttp[1:].find('Attack')+1:]
    skills = ttp.replace("None", "/h").split('/h')
    skill = ''
    val = []
    for entry in skills:
        if(entry== ''):
            EHPdict[skill] = val
        else:
            if(entry[0].isalpha()):
                if(skill!=''):
                    EHPdict[skill] = val
                line = entry.split(":")
                skill = line[0]
                if(skill!='Hitpoints'):
                    val = [[0, int(line[2].split(' ')[1].replace(',',''))]]
            else:
                line = entry.split(":")
                val.append([int(line[0].split(' ')[0].replace(',','')), int(line[1].split(' ')[1].replace(',',''))])
    return EHPdict

def loadXPtable():
    table = []
    xp = 0
    for lvl in range(1,99):
        diff = int(lvl + 300 * math.pow(2, float(lvl)/7))
        xp+=diff
        table.append(int(xp/4))
    return table

def loadItems():
    data = ""
    with urlopen(ItemIdDBUrl) as url:
        data = json.loads(url.read().decode())
    return data

xptable = loadXPtable()
ehprates = getEHPrates()
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

def getprice(id):
    r = Request(getracker + id.replace(' ', '-'), headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(r) as url:
        #data = json.loads(url.read().decode())
        html = url.read()
        pagesoup = soup(html, "html.parser")
        td = pagesoup.find("td",{"id":"item_stat_overall"}).text
        return (int)(td.replace(",",""))


def findValue(id):
    price = 0
    with urlopen(PriceUrl + id) as url:
        data = json.loads(url.read().decode())
    price = str(data['item']['current']['price'])
    value = convertToNumber(price.lower().strip())


    return price, value

def xpTillNextLevel(xp, lvl):
    rtn = 0
    try:
        rtn = xptable[lvl-1] - xp
    except IndexError:
        print(lvl, " out of bounds")
    return rtn

def EHPTillNextLevel(item):
    values = ehprates[item[0]]
    xprate = values[0][1]
    for i in range(0,len(values)):
        if(item[2] > values[i][0]):
            xprate = values[i][1]
    return float(item[3])/float(xprate), xprate

def getstats(username):
    stats = []
    r = Request(hiscoreURL + username, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(r) as url:
        #data = json.loads(url.read().decode())
        html = url.read()
        pagesoup = soup(html, "html.parser")
        stats_table = pagesoup.find("table",{"id":"stats_table"})
        tr = stats_table.findAll("tr")
        # 0 = title, 1 = overall, 25 = EHP
        for i in range(2,25):
            entries = tr[i].findAll("td")

            item = [entries[0].a.text, int(entries[3]["title"].replace(',','')), int(entries[1]["title"].replace(',',''))]
            if(item[1]<99):
                item.append(xpTillNextLevel(item[2], item[1]))
                (ehp, xp) = EHPTillNextLevel(item)
                item.append(ehp)
                item.append(xp)
                stats.append(item)

    return stats

def updateCML(username):
    r = Request(updateCMLURL + username, headers={'User-Agent': 'Mozilla/5.0'})
    urlopen(r)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    (items, length) = splitMessage(message.content)

    if message.content.startswith('$update'):
            client.change_presence(game = discord.Game(name = "updating"), status = discord.Status("idle"), afk = True)
            await client.send_message(message.channel, 'updating...'.format(message))
            await client.send_message(message.channel, 'pulling...'.format(message))
            g.pull ()
            await client.send_message(message.channel, 'restarting...'.format(message))

            os.execl(sys.executable, sys.executable, *sys.argv)

    if message.content.startswith('$help'):
        msg = '$help, $listdrops, $add, $lookup, $update, $fastestlevel'.format(message)
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

    if message.content.lower().startswith('$fastestlevel'):
        if(length < 2):
            await client.send_message(message.channel, "username not specified \n Usage: $fastestlevel rsname")
        else:
            username = message.content.split(' ',1)[1]
            updateCML(username.replace(' ','_'))
            stats = getstats(username.replace(' ','+'))
            stats = sorted(stats, key = itemgetter(4))
            embed = discord.Embed(title="EHP until level", description="Max effeciency minutes until level", color=0x00ff00)
            for row in stats:
                embed.add_field(value=format(row[3], ",d")+"xp for " + format(round(row[4]*60,2),",.2f") + " minutes at " + format(row[5],",d") + " xp/h", name=row[0], inline=False)

            await client.send_message(message.channel, embed=embed)

    if message.content.lower().startswith('$foo'):
        namecol = listSheet.col_values(1)
        pricecol = 3
        for i in range(1, len(namecol)):
            try:
                print("updating " + namecol[i] + " - " + str(getprice(namecol[i])))
                if(listSheet.cell(5,i))=="FALSE"):
                    print("to be updated")
            except:
                traceback.print_exc()
                await client.send_message(message.channel, "could not find item "+ namecol[i])
            #listSheet.update_cell(pricecol, i, getprice(namecol[i]))
        await client.send_message(message.channel, "updated")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    client.change_presence(game = None, status = None, afk = False)

client.run(TOKEN)
