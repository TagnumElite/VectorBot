#!/usr/bin/python3
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
from cogs.utils import checks#, databases
from cogs.utils import parser

Parser = parser.Parser()

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
            #exampleconfigs = re.sub("\/\/[a-zA-Z0-9 .#':/!,*-{};()]+(?=\n)", "", ExampleConfig)
            #for key, value in json.loads(exampleconfigs).items():
            #    exampleconfigs[key] = input("Enter {key} ({Type}):".format(
            #        key=key,
            #        Type=type(value).__name__
            #    ))
            newconfig.write(re.sub("\/\/[a-zA-Z0-9 .#':/!,*-{};()]+(?=\n)", "", ExampleConfig))
        exit("Setup configs.json!!!")


defaultDir = os.getcwd()

currentToken = Configs["Modes"][Configs["Mode"]]["Token"]
currentLog = Configs["Modes"][Configs["Mode"]]["Log"]
currentWelcome = Configs["Modes"][Configs["Mode"]]["Welcome"]
currentDB = Configs["Modes"][Configs["Mode"]]["DB Prefix"]
currentServer = Configs["Modes"][Configs["Mode"]]["Server"]
currentAnnounce = Configs["Modes"][Configs["Mode"]]["Announce"]
currentPrefix = Configs["Modes"][Configs["Mode"]]["Prefix"]
currentDescription = Configs["Modes"][Configs["Mode"]]["Description"]
currentStatus = Configs["Modes"][Configs["Mode"]]["Status"]
DMHelp = Configs["Modes"][Configs["Mode"]]["Description"]

#DBC = databases.DBC(
#    database=Configs["Database Name"],
#    user=Configs["Database User"],
#    password=Configs["Database Pass"],
#    host=Configs["Database Host"],
#    port=Configs["Database Port"]
#)
startup_time = datetime.datetime.utcnow()

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
    command_prefix=currentPrefix,
    description=currentDescription,
    pm_help=DMHelp,
    help_attrs=help_attrs
)

def isHelpCommand(query):
    """Checks if the text starts with any of the prefixes"""
    for pre in currentPrefix:
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
    elif isinstance(error, commands.CommandOnCooldown):
        await bot.send_message(ctx.message.author, error)

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
    await bot.change_presence(game=discord.Game(name=currentStatus))
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
    embed = Configs["Welcome Embed"]
    embed["Colour"] = 0x2ecc71
    em = Parser.createEmbed(
        data=embed,
        extra=Parser.make_dicts(member, member.server, Configs)
    )
    await bot.send_message(channel, embed=em)

@atexit.register
def onExit():
    """Called when the programs crashes or shutsdown normally.
    Won't work if the window/screen/tmux is shut down forcefully."""
    #os.chdir(defaultDir+"/buffers")
    #if len(DBC.Buffer) > 0:
    #    with open("buffer_{:%Y-%m-%d_%H;%M}.txt".format(startup_time), 'w') as buffer:
    #        for query in DBC.Buffer:
    #            buffer.write(query)
    #        buffer.close()
    #DBC.close()

def main():
    """This runs the magic and everything else!"""

    #Set Global Vars Before Setting Up Cogs
    bot.currentLog = currentLog
    bot.currentDB = currentDB
    bot.currentDIR = defaultDir
    bot.currentAnnounce = currentAnnounce
    bot.Configs = Configs
    #bot.DBC = DBC
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
    if Configs["Mode"].lower() in ["dev", "development"]:
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
