#!/usr/bin/python3.6
# Copyright (c) 2017 Tagan Hoyle
# This software is released under an GPL-3.0 license.
# See LICENSE.md for full details.

__title__ = 'VectorBot'
__author__ = 'TagnumElite'
__license__ = 'GPL-3.0'
__copyright__ = 'Copyright 2017 TagnumElite'
__version__ = '0.6.1'

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

Configs = {}
try:
    with open('configs.json', 'r') as file:
        Configs = json.load(file)
except FileNotFoundError:
    try:
        with open("ExampleConfigs.json", 'r') as example:
            ExampleConfig = example.read()
    except FileNotFoundError:
        exit("Missing ExampleConfig.json! Please download the ExampleConfig.json to setup bot!")
    else:
        with open('configs.json', 'w+') as newconfig:
            file.write(ExampleConfig)
        exit("Setup configs.json!!!")


defaultDir = os.getcwd()

DB = databases.DBC(database=Configs["Database Name"], user=Configs["Database User"], password=Configs["Database Pass"], host=Configs["Database Host"], port=Configs["Database Port"])

if Configs["Dev Mode"]:
    currentToken = Configs["Dev Token"]
    currentLog = Configs["Dev Log"]
    currentWelcome = Configs["Dev Welcome"]
    currentDB = Configs["Dev Database Prefix"]
    #currentNotification = devNotification
else:
    currentToken = Configs["Bot Token"]
    currentLog = Configs["Bot Log"]
    currentWelcome = Configs["Bot Welcome"]
    currentDB = Configs["Bot Database Prefix"]
    #currentNotification = botNotification

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

#I will fix this at some point
#discord_logger = logging.getLogger('discord')
#discord_logger.setLevel(logging.CRITICAL)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='vectordev %s.log' % (datetime.datetime.utcnow()), encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#log.addHandler(handler)

help_attrs = dict(hidden=True)

bot = commands.Bot(command_prefix=Configs["Prefix"], description=Configs["Description"], pm_help=Configs["PM Help"], help_attrs=help_attrs)

def isHelpCommand(query):
    for pre in Configs["Prefix"]:
        if query.lower().startswith(pre+"help"):
            return True
    return False

async def log_message(message, timeOfMessage=datetime.datetime.utcnow()):
    print(message)
    channel = discord.Object(id=currentLog)
    await bot.send_message(channel, message + " | " + str(timeOfMessage))

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
    await bot.change_presence(game=discord.Game(name=Configs["Status"]))
    bot.currentLog = currentLog
    bot.currentWelcome = currentWelcome
    #bot.currentNotification = currentNotification

@bot.event
async def on_resumed():
    await log_message("Resumed...")

@bot.event
async def on_message(message):
    msg = message.content
    author = message.author
    server = message.server
    channel = message.channel
    if message.author.bot or message.author.id == bot.user.id:
        bot.messages.remove(message)
        print("BOT")
        return
    #if author.id or server.id or channel.id in Configs["Ignored IDs"]:
    #    bot.messages.remove(message)
    #    print("Ignored")
    #    return
    if len(msg.split()) > 1: # This is to make so that commands aren't case sensitive
        msg = msg.split(maxsplit=1)
        msg[0] = msg[0].lower()
        content = " ".join(msg)
        message.content = content
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)
    if isHelpCommand(message.content):
        try:
            await bot.delete_message(message)
        except discord.errors.Forbidden():
            await databases.log_message(message)
        except:
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id))
    print("MESSAGE: %s"%(message.content))

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
    #TODO: Remember to make an if statement to check if the server has overridden rules!
    em = discord.Embed(title=Configs["Rules"]["Title"].format(server=server.name, channel=channel.name, author=author.name), description=Configs["Rules"]["Description"].format(server=server.name, channel=channel.name, author=author.name), color=0xff0000, url=Configs["Rules"]["Url"])
    em.set_footer(text=Configs["Rules"]["Footer"]["Text"].format(server=server.name), icon_url=discord.Embed.Empty if Configs["Rules"]["Footer"]["Icon Url"] is "" else Configs["Rules"]["Footer"]["Icon Url"])
    em.set_author(name=Configs["Rules"]["Author"]["Name"].format(server=server.name), icon_url=discord.Embed.Empty if Configs["Rules"]["Author"]["Avatar Url"].format(server_icon=server.icon_url) is "" else Configs["Rules"]["Author"]["Avatar Url"])
    for rule in Configs["Rules"]["Rules"]:
        em.add_field(name=rule["Name"], value=rule["Rule"], inline=rule["Inline"] if "Inline" in rule else False)
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

def main():
    for extension in Configs["Cogs"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
        else:
            print("Loaded Extension: ", extension)

    if Configs["Dev Mode"]:
        for dextension in Configs["Dev Cogs"]:
            try:
                bot.load_extension(dextension)
            except Exception as e:
                print('Failed to load development extension {}\n{}: {}'.format(dextension, type(e).__name__, e))
            else:
                print("Loaded Development Extension: ", dextension)

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
    #    log.removeHandler(hdlr)

if __name__ == '__main__':
    main() # just doing this so I can run the bot easier
