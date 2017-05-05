#!/usr/bin/python3
# Copyright (c) 2017 Tagan Hoyle
# This software is released under an EXAMPLE license.
# See LICENSE.md for full details.

from discord.ext import commands
import discord
from cogs.utils import checks, databases
import datetime, re
import json, asyncio
import copy
import logging
import traceback
import sys, os
import discord.errors
from collections import Counter

ExampleConfig = """{
    "Bot Token": "PUT THE BOTS TOKEN HERE", // This is the bots token
    "Bot Server": "123456789101112131", // This is the main server that the bot will function from
    "Bot Log": "123456789101112131", // This is the channel where the bot will log messages
    "Bot Welcome": "123456789101112131", // This is the channel where the bot is going to welcome platers
    "Bot Database Prefix": "vb_",

    // Just a quick message. Bot Log and Bot Welcome will be removed as the bot gets support for to be able to be used in multiple servers

    "Dev Mode": false,
    "Dev Token": "ONLY USE THIS IF YOU ARE GOING TO DEVELOP THE BOT",
    "Bot Server": "123456789101112131",
    "Dev Log": "123456789101112131",
    "Dev Welcome": "123456789101112131",
    "Dev Database Prefix": "vd_",

    "Database Host": "localhost",
    "Database Port": "3306",
    "Database Name": "Vector",
    "Database User": "VectorBot",
    "Database Pass": "",

    "Cogs": [
        "cogs.admin",
        "cogs.steams",
        "cogs.database",
        "cogs.utilities",
        "cogs.misc",
        "cogs.feeds",
        "cogs.support"
    ],

    "Owner": "123456789101112131",
    "Prefix": ["v!", "V!", "\\N{HEAVY EXCLAMATION MARK SYMBOL}"],
    "Description": "Hello!, I am the VectorBot!",
    "PM Help": true,

    "Email User": "user@example.com",
    "Email Pass": "example.password",
    "Email Incoming Server": "",
    "Email Outgoing Server": "",
    "IMAP Port": 143,
    "POP3 Port": 110,
    "SMTP Port": 25
}"""

Configs = {}
try:
    with open('configs.json', 'r') as file:
        Configs = json.load(file)
except FileNotFoundError:
    with open('configs.json', 'w+') as file:
        file.write(ExampleConfig)
    exit("Setup configs.json!!!")


defaultDir = os.getcwd()

DB = databases.DBC(database=Configs["Database Name"], user=Configs["Database User"], password=Configs["Database Pass"], host=Configs["Database Host"], port=Configs["Database Port"])

if Configs["Dev"] == False:
    currentToken = Configs["Bot Token"]
    currentLog = Configs["Bot Log"]
    currentWelcome = Configs["Bot Welcome"]
    currentDB = Configs["Bot Database Prefix"]
    #currentNotification = botNotification
else:
    currentToken = Configs["Dev Token"]
    currentLog = Configs["Dev Log"]
    currentWelcome = Configs["Dev Welcome"]
    currentDB = Configs["Dev Database Prefix"]
    #currentNotification = devNotification

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


#discord_logger = logging.getLogger('discord')
#discord_logger.setLevel(logging.CRITICAL)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='vectordev %s.log' % (datetime.datetime.utcnow()), encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#log.addHandler(handler)

help_attrs = dict(hidden=True)

bot = commands.Bot(command_prefix=Configs["Prefix"], description=Configs["Description"], pm_help=Configs["PM Help"], help_attrs=help_attrs)

async def log_message(message, timeOfMessage=datetime.datetime.utcnow()):
    print(message)
    channel = discord.Object(id=currentLog)
    await bot.send_message(channel, message + " | " + str(timeOfMessage))

async def twitch_notification():
    await bot.wait_until_ready()
    counter = 0
    channel = discord.Object(id=currentNotification)
    while not bot.is_closed:
        counter += 1
        await bot.send_message(channel, counter)
        await asyncio.sleep(60) # task runs every 60 seconds

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    await log_message("Started:")
    await bot.change_presence(game=discord.Game(name='vectoresports.co.za'))
    bot.currentLog = currentLog
    bot.currentWelcome = currentWelcome
    bot.currentNotification = currentNotification

@bot.event
async def on_resumed():
    await log_message("Resumed...")

@bot.event
async def on_message(message):
    msg = message.content
    author = message.author
    server = message.server
    channel = message.channel
    if message.reactions is not None:
        print(message.reactions)
    if message.author.id == bot.user.id:
        return
    if len(msg.split()) > 1:
        msg = msg.split(maxsplit=1)
        msg[0] = msg[0].lower()
        content = " ".join(msg)
        message.content = content
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)
    if message.content.lower().startswith("v!help") or message.content.startswith("\N{HEAVY EXCLAMATION MARK SYMBOL}help"):
        try:
            await bot.delete_message(message)
        except discord.errors.Forbidden():
            await databases.log_message(message)
        except ValueError:
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: Could not convert data to an integer""" % (author, author.id, server, server.id, channel, channel.id))
        except:
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id))

@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def do(ctx, times : int, *, command):
    """Repeats a command a specified number of times."""
    msg = copy.copy(ctx.message)
    msg.content = command
    for i in range(times):
        await bot.process_commands(msg)

@bot.command(pass_context=True, hidden=True)
@checks.admin_or_permissions(manage_server=True)
async def logout(ctx):
    """Logs Bot out of Discord"""
    await log_message("Logging Out!", datetime.datetime.utcnow())
    await bot.say("Logging Out")
    await asyncio.sleep(3)
    await bot.logout()

@bot.event
async def on_member_join(member):
    await log_message("Member: %s(%s) has gone joined the server %s(%s)" % (member.name, member.id, member.server.name, member.server.id), datetime.datetime.utcnow())
    channel = discord.Object(id=currentWelcome)
    em = discord.Embed(title='Welcome to %s!' % (member.server.name), description="""
Use these commands %s!
- V!help to get a PM about my commands!
- V!rules to see the rules!""" % (member.mention), color=0x2ecc71)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    em.set_thumbnail(url=member.avatar_url)
    await bot.send_message(channel, embed=em)

@bot.command(pass_context=True)
async def rules(ctx):
    msg = ctx.message
    server = msg.server
    author = msg.author
    channel = msg.channel
    await log_message("User %s(%s) ran command `rules` on server %s(%s) in channel %s(%s)" % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    em = discord.Embed(title='%s\'s rules!' % (server.name), description="""
1. No rudeness
2. No interfering in team practices
3. No troll logic
4. No spamming
5. Obey all Exco members and senior co-ordinators (This is not Senior Member server group)
6. Players are PROHIBITED from joining competitive rooms where the team/clan owner has not requested them  to join immediatly prior to them  joining. You can and probably will disturb a match. Owners are listed in channel descriptions.
7. No Racism, first tme offenders will be permanently branded. If you want be to an ignorant asshole, go back to the 60's. We will not be held liable if you are recorded, your IP is tracked, and you are held accountable for your actions. By being on this teamspeak you indemnify Vector eSports for any responsibility.
8. If you are playing another game in a competitive section that is designation for a specific game, you will be warned and forceably moved. If you do it again, you will be banned from this teamspeak.
9. Any security officers or senior members caught abusing their powers will be stripped of all privelages.
10. Senior members have no punishment or decisive authority in this community. If they  boss you around, report them by sending an email to admin@vectoresports.co.za - This goes for team captains aswell. Team captains should only have rights to the channel they are in.

e-Sports is a profession and here we are professionals.

Insta bans will be handed out for any offenders.""", color=0x992d22)
    try:
        await bot.delete_message(msg)
    except discord.errors.Forbidden():
        await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    except ValueError:
         await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: Could not convert data to an integer""" % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    except:
         await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    await bot.send_message(author, embed=em)

@bot.command(pass_context=True)
async def find(ctx, user=None):
    """Finds User"""
    return # NO, I don't want to use this for now until I make a better user finder
    await log_message("Command `find` was run")
    if user == None:
        await bot.say("Please specify user to find")
        return
    else:
        await bot.say("User is " + str(user))

    server = ctx.message.server
    if server == None:
        await bot.say("Server not found")
        return
    else:
        await bot.say("Server is %s" % (server.name))

    members = server.members
    mems = []
    if members == None:
        await bot.say("Members not found")
        return
    else:
        for member in members:
            mems.append(member.name)
        await bot.say("Members are %s" % (mems))

    #member = checks.find_user(user, members)
    member = server.get_member_named(user)

    if member == None:
        print(member)
        await bot.say("User not found")
        return
    else:
        await bot.say("User %s was found" % (member))

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

def load_servers_configs():
    os.chdir(defaultDir)
    servers = {}
    for server in os.listdir('servers'):
        with open("servers/"+server) as server_json:
            server_config = json.load(server_json)
            servers[server.replace(".json", "")] = server_config
    return servers

def createServerConfig(server):
    if server == None:
        return
    os.chdir(defaultDir)
    data = ""
    with open("servers/"+server.id+".json") as server_config_file:
        json.dump(data, server_config_file)
        return True
    return False

def main():
    for extension in Configs["Cogs"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
        else:
            print("Loaded Extensions: ", extension)

    #Setup Twitch Notifications
    #bot.loop.create_task(twitch_notification())

    #Setup Global Vars
    bot.currentLog = currentLog
    bot.currentDB = currentDB
    bot.currentDIR = defaultDir
    bot.Configs = Configs

    #Run Bot
    bot.run(currentToken)

    #handlers = log.handlers[:]
    #for hdlr in handlers:
    #    hdlr.close()
    #log.removeHandler(hdlr)

if __name__ == '__main__':
    main() # just doing this so I can run the bot easier
