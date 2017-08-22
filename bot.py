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
__version__ = '0.6.16pre'

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
from cogs.utils import parser, config

Config = {}
try:
    with open('config.json', 'r') as file:
        Config = json.load(file)
except FileNotFoundError:
    try:
        with open("ExampleConfig.json", 'r') as example:
            ExampleConfig = example.read()
    except FileNotFoundError:
        exit("Missing ExampleConfig.json! Please download the ExampleConfig.json to setup bot!")
    else:
        with open('config.json', 'w') as newconfig:
            #exampleconfigs = re.sub("\/\/[a-zA-Z0-9 .#':/!,*-{};()]+(?=\n)", "", ExampleConfig)
            #for key, value in json.loads(exampleconfigs).items():
            #    exampleconfigs[key] = input("Enter {key} ({Type}):".format(
            #        key=key,
            #        Type=type(value).__name__
            #    ))
            newconfig.write(re.sub("\/\/[a-zA-Z0-9 .#':/!,*-{};()]+(?=\n)", "", ExampleConfig))
        exit("Setup config.json!!!")

defaultDir = os.getcwd()
Mode = Config["Mode"]
Config = Config["Modes"][Mode]
mainServer = Config["Server"]
Database = Config["Database"]
Embeds = Config["Embeds"]

DBC = databases.DBC(
    database=Database["Name"],
    user=Database["User"],
    password=Database["Pass"],
    host=Database["Host"],
    port=Database["Port"]
)
startup_time = datetime.datetime.utcnow()

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='logs/vectorlog_{:%Y-%m-%d_%H;%M}.log'.format(
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
    command_prefix=Config["Prefix"],
    description=Config["Description"],
    pm_help=Config["DM Help"],
    help_attrs=help_attrs
)

def isHelpCommand(query):
    """Checks if the text starts with any of the prefixes"""
    for pre in Config["Prefix"]:
        if query.lower().startswith(pre+"help"):
            return True
    return False

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
    print('User:', bot.user.name+"#"+bot.user.discriminator)
    print('ID: ', bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    print("Started:")
    await bot.change_presence(game=discord.Game(name=Config["Status"]))
    bot.owner = None
    for server in bot.servers:
        for member in server.members:
            if member.id == Config["Owner"]:
                print("Found Owner %s/%s#%s" % (member.id, member.name, member.discriminator))
                bot.owner = member
                break
            if bot.owner is not None:
                break
        if bot.owner is not None:
            break
    if bot.owner is None:
        print("Failed to find owner")

@bot.event
async def on_resumed():
    """I don't know yet."""
    print("Resumed...")

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
    if message.author.id in Config["Ignored IDs"] or message.server.id in Config["Ignored IDs"] or message.channel.id in Config["Ignored IDs"]:
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
            print(
                """Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (
                    author, author.id,
                    server, server.id,
                    channel, channel.id
                )
            )

@bot.event
async def on_member_join(member):
    """Called when a member has joined the server. This function handles the Welcome messages"""
    continuee = False
    server_id = member.server.id
    await asyncio.sleep(10)
    server = bot.get_server(server_id)
    for members in server.members:
        if member is members:
            continuee = True
            break
    if not continuee:
        return
    print(
        "Member: %s(%s) has gone joined the server %s(%s)" % (
            member.name, member.id,
            member.server.name, member.server.id
        ),
        datetime.datetime.utcnow()
    )
    channel = discord.Object(id=currentWelcome)
    embed = Embeds["Welcome"]
    embed["Colour"] = 0x2ecc71
    em = Parser.createEmbed(
        data=embed,
        extra=Parser.make_dicts(member, member.server, Config)
    )
    await bot.send_message(channel, embed=em)

@atexit.register
def onExit():
    """Called when the programs crashes or shutsdown normally.
    Won't work if the window/screen/tmux is shut down forcefully."""
    os.chdir(defaultDir+"/buffers")
    if len(DBC.Buffer) > 0:
        with open("buffer_{:%Y-%m-%d_%H;%M}.txt".format(startup_time), 'w') as buffer:
            for query in DBC.Buffer:
                buffer.write(query)
            buffer.close()
    DBC.close()

def main():
    """This runs the magic and everything else!"""

    #Set Global Vars Before Setting Up Cogs
    bot.owner = None
    bot.mainServer = mainServer
    bot.currentDIR = defaultDir
    bot.Config = Config
    os.chdir(defaultDir+"\configs")
    bot.Configs = []
    for file in os.listdir():
        if file.endswith(".json"):
            print("Loading config", file)
            bot.Configs.append(config.Config(file.replace(".json", "")))
    os.chdir(defaultDir)
    bot.DBC = DBC
    bot.startup_time = startup_time

    #Setup Main Cogs
    for extension in Config["Cogs"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
        else:
            print("Loaded Extension: ", extension)

    #Run Bot
    bot.run(Config["Token"])

    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)

if __name__ == '__main__':
    main()
