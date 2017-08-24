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
import re
import discord.errors
import discord
from discord.ext import commands
from cogs.utils import checks, databases
from cogs.utils import parser, config

def setup_loggers():
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
Mode = Config["Mode"]
Config = Config["Modes"][Mode]


class VectorBot(commands.Bot):
    """This is the VectorBot's main class and what runs the whole bot.

    Parameters
    ----------
    config: dict
        The Main config the bot will run off of"""

    def __init__(self, config, **kwargs):
        self.Version = __version__

        self.Config = config
        self.defaultDir = os.getcwd()
        self.main_guild = self.Config["Guild"]
        self.Database = self.Config["Database"]
        self.Embeds = self.Config["Embeds"]

        self.Config["Prefix"] = kwargs.get("command_prefix", self.Config["Prefix"])
        kwargs["description"] = kwargs.get("description", self.Config["Description"])
        kwargs["pm_help"] = kwargs.get("kwargs", self.Config["DM Help"])
        kwargs["help_attrs"] = dict(hidden=True)

        super().__init__(command_prefix=commands.when_mentioned_or(self.Config["Prefix"]), **kwargs)

        self.Status = []

        self.DBC = databases.DBC(
            database=self.Database["Name"],
            user=self.Database["User"],
            password=self.Database["Pass"],
            host=self.Database["Host"],
            port=self.Database["Port"]
        )
        self.startup_time = datetime.datetime.utcnow()

        for cog in self.Config["Cogs"]:
            try:
                self.load_extension(cog)
            except Exception as E:
                print('Could not load extension {{0}} due to {{1.__class__.__name__}}'.format(cog, E))
            else:
                print('Loaded Exention {0}'.format(cog))
    def isHelpCommand(self, query):
        """Checks if the text starts with any of the prefixes"""
        for pre in self.Config["Prefix"]:
            if query.lower().startswith(pre+"help"):
                return True
        return False

    async def on_ready(self):
        """This is called when the bot has logged in and can run all of its functions"""

        print('Logged in as:')
        print('User:', self.user.name+"#"+self.user.discriminator)
        print('ID: ', self.user.id)
        print('------')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print("Started:")
        await self.change_presence(game=discord.Game(name=self.Config["Status"]))
        self.owner = None
        for guild in self.guilds:
            for member in guild.members:
                if member.id == self.Config["Owner"]:
                    print("Found Owner %s/%s#%s" % (member.id, member.name, member.discriminator))
                    self.owner = member
                    break
                if self.owner is not None:
                    break
            if self.owner is not None:
                break
        if self.owner is None:
            print("Failed to find owner")

        await self.setup_loops()

    async def on_command_error(self, error, ctx):
        """This is called when an error has occured when running a command"""
        if isinstance(error, commands.NoPrivateMessage):
            await self.send(ctx.message.author, 'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await self.send(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        elif isinstance(error, commands.CommandOnCooldown):
            await self.send(ctx.message.author, error)

    async def on_resumed(self):
        """I don't know yet."""
        print("Resumed...")
    async def on_message(self, message):
        """Called when the bot recieves a message. Either through t a private/group/guild message"""
        msg = message.content
        author = message.author
        guild = message.guild
        channel = message.channel
        if message.author.id in self.Config["Ignored IDs"] or message.guild.id in self.Config["Ignored IDs"] or message.channel.id in self.Config["Ignored IDs"]:
            print("Ignored")
            return
        if len(msg.split()) > 1: # This is to make so that commands aren't case sensitive
            msg = msg.split(maxsplit=1)
            msg[0] = msg[0].lower()
            content = " ".join(msg)
            message.content = content
            await self.process_commands(message)
        else:
            await self.process_commands(message)
        if self.isHelpCommand(message.content):
            try:
                await self.delete_message(message)
            except discord.errors.Forbidden():
                await databases.log_message(message)
            except:
                print(
                    """Error deleteing command `help` run by %s(%s) on guild %s(%s) in channel %s(%s)
    Error: {0}""".format(Forbidden) % (
                        author, author.id,
                        guild, guild.id,
                        channel, channel.id
                    )
                )

    async def on_member_join(self, member):
        """Called when a member has joined the guild. This function handles the Welcome messages"""
        continuee = False
        guild_id = member.guild.id
        await asyncio.sleep(10)
        guild = self.get_guild(guild_id)
        for members in guild.members:
            if member is members:
                continuee = True
                break
        if not continuee:
            return
        print(
            "Member: %s(%s) has gone joined the guild %s(%s)" % (
                member.name, member.id,
                member.guild.name, member.guild.id
            ),
            datetime.datetime.utcnow()
        )
        channel = discord.Object(id=currentWelcome)
        embed = self.Embeds["Welcome"]
        embed["Colour"] = 0x2ecc71
        em = Parser.createEmbed(
            data=embed,
            extra=Parser.make_dicts(member, member.guild, self.Config)
        )
        await self.send(channel, embed=em)

    async def setup_loops(self):
        """Setup the loops"""

        self.loop.create_task(self.change_status())

    async def add_status(self, status, priority="LOW", time=60):
        """Add a status the bot

        Parameters
        ----------
        status: discord.Game
            The status to change to
        priority: str
            Defaults to "LOW". Don't know yet
        time: int
            Don't know yet"""

        self.Status.append((status, priority, time))

    async def change_status(self):
        await self.wait_until_ready()
        self.Status.append()
        while not self.is_closed():
            pass

def main():
    """Redundent"""
    for file in os.listdir():
        if file.endswith(".json"):
            print("Loading config", file)
            bot.Configs.append(config.Config(file.replace(".json", "")))

if __name__ == '__main__':
    setup_loggers()

    Bot = VectorBot(config=Config)
    Bot.run(Config["Token"])

    if len(Bot.DBC.Buffer) > 0:
        with open("buffers/buffer_{:%Y-%m-%d_%H;%M}.txt".format(startup_time), 'w') as buffer:
            for query in Bot.DBC.Buffer:
                buffer.write(query)
            buffer.close()
    Bot.DBC.close()

    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)
