#!/usr/bin/python3.6
# Copyright (c) 2017 Tagan Hoyle
# This software is released under an GPL-3.0 license.
# See LICENSE.md for full details.

"""
VectorBot
@author: TagnumElite
"""

__title__ = 'VectorBot'
__author__ = 'TagnumElite'
__license__ = 'GPL-3.0'
__copyright__ = 'Copyright 2017 TagnumElite'
__version__ = '0.6.15pre'

import asyncio
import datetime
import json
import copy
import logging
import traceback
import sys
import os
import atexit
import re
import discord.errors
import discord
from discord.ext import commands
from cogs.utils import checks, databases

Configs = {}
try:
    with open('configs.json', 'r') as file:
        Configs = json.load(file)
except FileNotFoundError:
    try:
        with open("ExampleConfig.json", 'r') as example:
            ExampleConfig = example.read()
    except FileNotFoundError:
        exit("Missing ExampleConfig.json! Please download the ExampleConfig.json to setup bot!")
    else:
        with open('configs.json', 'w') as newconfig:
            newconfig.write(re.sub("\/\/[a-zA-Z0-9 .#':/!,*-{};()]+(?=\n)", "", ExampleConfig))
        exit("Setup configs.json!!!")


defaultDir = os.getcwd()

DBC = databases.DBC(
    database=Configs["Database Name"],
    user=Configs["Database User"],
    password=Configs["Database Pass"],
    host=Configs["Database Host"],
    port=Configs["Database Port"]
)
startup_time = datetime.datetime.utcnow()

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

#try:
#    import uvloop
#except ImportError:
#    pass
#else:
#    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='logs/vectordev_{:%Y-%m-%d_%H;%M}.log'.format(
        datetime.datetime.utcnow()
    ),
    encoding='utf-8',
    mode='w'
)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
    )
)
log.addHandler(handler)

help_attrs = dict(hidden=True)

bot = commands.Bot(
    command_prefix=Configs["Prefix"],
    description=Configs["Description"],
    pm_help=Configs["PM Help"],
    help_attrs=help_attrs
)

def isHelpCommand(query):
    """Checks if the text starts with any of the prefixes"""
    for pre in Configs["Prefix"]:
        if query.lower().startswith(pre+"help"):
            return True
    return False

async def log_message(message, timeOfMessage=datetime.datetime.utcnow()):
    """This is called when a message must be logged to the logs channel.
    I want to remove this at one stage because I want to move everything to MySQL"""
    print(message)
    channel = discord.Object(id=currentLog)
    await bot.send_message(channel, message + " | " + str(timeOfMessage))

@bot.event
async def on_command_error(error, ctx):
    """This is called when an error has occured when running a command"""
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
    """This is called when the bot has logged in and can run all of its functions"""
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
    """I don't know yet."""
    await log_message("Resumed...")

@bot.event
async def on_message(message):
    """Called when the bot recieves a message. Either through t a private/group/guild/server message"""
    msg = message.content
    author = message.author
    server = message.server
    channel = message.channel
    if message.author.bot or message.author.id == bot.user.id:
        bot.messages.remove(message)
        print("BOT")
        return
    if message.author.id in Configs["Ignored IDs"] or message.server.id in Configs["Ignored IDs"] or message.channel.id in Configs["Ignored IDs"]:
        bot.messages.remove(message)
        print("Ignored")
        return
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
            await log_message(
                """Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (
                    author, author.id,
                    server, server.id,
                    channel, channel.id
                )
            )
    print("MESSAGE: %s"%(message.content))

@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def do(ctx, times: int, *, command):
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
    await asyncio.sleep(4)
    await bot.logout()

@bot.event
async def on_member_join(member):
    """Called when a member has joined the server. This function handles the Welcome messages"""
    await log_message(
        "Member: %s(%s) has gone joined the server %s(%s)" % (
            member.name, member.id,
            member.server.name, member.server.id
        ),
        datetime.datetime.utcnow()
    )
    channel = discord.Object(id=currentWelcome)
    em = discord.Embed(
        title='Welcome to %s!' % (member.server.name),
        description="""Use these commands %s!
- V!help to get a PM about my commands!
- V!rules to see the rules!""" % (member.mention),
        color=0x2ecc71
    )
    em.set_author(
        name=member.name,
        icon_url=member.avatar_url
    )
    em.set_thumbnail(url=member.avatar_url)
    await bot.send_message(channel, embed=em)

@bot.command(pass_context=True)
async def rules(ctx):
    """Get the rules of the current server! BROKEN"""
    msg = ctx.message
    server = msg.server
    author = msg.author
    channel = msg.channel
    #TODO: Remember to make an if statement to check if the server has overridden rules!
    em = discord.Embed(
        title=Configs["Rules"]["Title"].format(
            server=server.name,
            channel=channel.name,
            author=author.name
        ),
        description=Configs["Rules"]["Description"].format(
            server=server.name,
            channel=channel.name,
            author=author.name
        ),
        color=0xff0000
    )
    em.set_image(url=Configs["Rules"]["Image"])
    em.set_thumbnail(url=Configs["Rules"]["Thumbnail"])
    if Configs["Rules"]["Footer"]["Enabled"]:
        em.set_footer(
            text=Configs["Rules"]["Footer"]["Text"].format(server=server.name),
            icon_url=Configs["Rules"]["Footer"]["Icon Url"].format(server_icon=server.icon_url)
        )
    if Configs["Rules"]["Author"]["Enabled"]:
        em.set_author(
            name=Configs["Rules"]["Author"]["Name"].format(server=server.name),
            icon_url=Configs["Rules"]["Author"]["Avatar Url"].format(server_icon=server.icon_url)
        )

    for rule in Configs["Rules"]["Rules"]:
        em.add_field(
            name=rule["Name"],
            value=rule["Rule"],
            inline=rule["Inline"] if "Inline" in rule else False
        )
    try:
        await bot.delete_message(msg)
    except Exception as E:
        await log_message(
            """Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(E) % (
                author, author.id,
                server, server.id,
                channel, channel.id
            ),
            datetime.datetime.utcnow()
        )
    await bot.send_message(author, embed=em)

#@bot.command(pass_context=True)
#async def find(ctx, user=None):
#    """Finds User a user with the name provided. Really badly setup"""
#    return # NO, I don't want to use this for now until I make a better user finder
#    await log_message("Command `find` was run")
#    if user == None:
#        await bot.say("Please specify user to find")
#        return
#    else:
#        await bot.say("User is " + str(user))
#
#    server = ctx.message.server
#    if server == None:
#        await bot.say("Server not found")
#        return
#    else:
#        await bot.say("Server is %s" % (server.name))
#
#    members = server.members
#    mems = []
#    if members == None:
#        await bot.say("Members not found")
#        return
#    else:
#        for member in members:
#            mems.append(member.name)
#        await bot.say("Members are %s" % (mems))
#
#    #member = checks.find_user(user, members)
#    member = server.get_member_named(user)
#
#    if member == None:
#        print(member)
#        await bot.say("User not found")
#        return
#    else:
#        await bot.say("User %s was found" % (member))

@atexit.register
def onExit():
    """Called when the programs crashes or shutsdown normally.
    Won't work if the window/screen/tmux is shut down forcefully."""
    os.chdir(defaultDir)
    if len(DBC.Buffer) > 0:
        with open("buffer_{:%Y-%m-%d_%H;%M}.txt".format(startup_time), 'w') as buffer:
            for query in DBC.Buffer:
                buffer.write(query)
            buffer.close()
    DBC.close()

def main():
    """This runs the magic and everything else!"""
    #Set Global Vars Before Setting Up Cogs
    bot.currentLog = currentLog
    bot.currentDB = currentDB
    bot.currentDIR = defaultDir
    bot.Configs = Configs
    bot.DBC = DBC
    bot.startup_time = startup_time

    #Setup Main Cogs
    for extension in Configs["Cogs"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
        else:
            print("Loaded Extension: ", extension)

    #Setup Dev Cogs
    if Configs["Dev Mode"]:
        for dextension in Configs["Dev Cogs"]:
            try:
                bot.load_extension(dextension)
            except Exception as e:
                print('Failed to load development extension {}\n{}: {}'.format(dextension, type(e).__name__, e))
            else:
                print("Loaded Development Extension: ", dextension)

    #Run Bot
    bot.run(currentToken)

    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)

if __name__ == '__main__':
    main() # Needed this to stop the autodoc!
