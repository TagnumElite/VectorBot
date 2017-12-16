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
__copyright__ = 'Copyright 2017, TagnumElite'
__version__ = '1.0.0a'

import os
import sys
import json
import asyncio
import logging
import datetime
import traceback
import subprocess

sys.path.insert(0, "lib")

try:
    import discord
    from discord.ext import commands
except ImportError:
    print("Please install discord.py")
    sys.exit(1)

default_cogs = [
    "cogs.admin",
    "cogs.database",
    "cogs.gallery",
    "cogs.utilities"
]

class VectorBot(commands.AutoShardedBot):
    
    def __init__(self, config, logger, **kwargs):
        self.version = __version__
        self.logger = logger
        self.uptime = datetime.datetime.utcnow()
        self.config = config
        
        super().__init__(**kwargs)
        
        self.remove_command("help")
        self.add_command(self.cmd_commands)
        self.add_command(self.cmd_help)
        
        self.config['Cogs'] = self.config.get('Cogs', default_cogs)
        
        for cog in self.config["Cogs"]:
            try:
                self.load_extension(cog)
            except Exception as E:
                print('Could not load extension {0} due to {1.__class__.__name__}'.format(cog, E))
                self.logger.debug("Failed to load {0} due to {1}".format(cog, E))
            else:
                print('Loaded Exention {0}'.format(cog))
    
    async def on_ready(self):
        """"""
        underline = '-'*(len(self.user.name)+26)
        print(underline)
        print('{0.user.name}#{0.user.discriminator} ({0.user.id})'.format(self))
        print(underline)
        print("\nStats:")
        print("{0} servers \n{1} channels \n{2} users\n".format(
            len(self.guilds), len([c for c in self.get_all_channels()]),
            len(set(self.get_all_members()))
        ))
        print(underline)
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        status = self.config.get('Status', "vectorbot.elitekast.com")
        await self.change_presence(game=discord.Game(name=status))
    
    async def on_message(self, message):
        """"""
        msg = message.content
        author = message.author
        channel = message.channel
        guild = message.guild
        if author.bot:
            return
        if len(msg.split()) > 1: # This is to make so that commands aren't case sensitive
            msg = msg.split(maxsplit=1)
            msg[0] = msg[0].lower()
            content = " ".join(msg)
            message.content = content
        else:
            msg = msg.lower()
            message.content = msg
        await self.process_commands(message)
        await self.delete_help(message)
    
    async def delete_help(self, message):
        prefixes = await self.get_prefix(message)
        if isinstance(prefixes, str):
            if message.content.startswith(prefixes+'help'):
                await message.delete()
        else:
            await self.delete_help_prefix(message, prefixes)
    
    async def delete_help_prefix(self, message, prefix):
        if isinstance(prefix, str):
            if message.content.startswith(prefix+'help'):
                await message.delete()
                return True
            else:
                return False
        else:
            for pre in prefix:
                if await self.delete_help_prefix(message, pre):
                    return True
            return False
    
    async def on_resumed(self):
        """"""
        print("Resumed")
    
    @commands.command(name="help")
    async def cmd_help(self, ctx, *commands):
        """Shows this message."""
        # No body wants the channel to be stuffed with embeds
        destination = ctx.author
        
        def repl(obj):
            return _mentions_transforms.get(obj.group(0), '')

        # help by itself just lists our own commands.
        if len(commands) == 0:
            pages = await self.formatter.format_help_for(ctx, self)
        elif len(commands) == 1:
            # try to see if it is a cog name
            name = _mention_pattern.sub(repl, commands[0])
            command = None
            if name in self.cogs:
                command = self.cogs[name]
            else:
                command = self.all_commands.get(name)
                if command is None:
                    await destination.send(self.command_not_found.format(name))
                    return

            pages = await self.formatter.format_help_for(ctx, command)
        else:
            name = _mention_pattern.sub(repl, commands[0])
            command = self.all_commands.get(name)
            if command is None:
                await destination.send(self.command_not_found.format(name))
                return

            for key in commands[1:]:
                try:
                    key = _mention_pattern.sub(repl, key)
                    command = command.all_commands.get(key)
                    if command is None:
                        await destination.send(self.command_not_found.format(key))
                        return
                except AttributeError:
                    await destination.send(self.command_has_no_subcommands.format(command, key))
                    return

            pages = await self.formatter.format_help_for(ctx, command)

        if bot.pm_help is None:
            characters = sum(map(lambda l: len(l), pages))
            # modify destination based on length of pages.
            if characters > 1000:
                destination = ctx.message.author

        for page in pages:
            await destination.send(page)
    
    @commands.command(name="commands")
    async def cmd_commands(self, ctx, *commands):
        for command in self.commands:
            print(command.name, command.module)

def setup_loggers(config_mode):
    import logging.handlers
    logger = logging.getLogger("vectorbot")
    
    log_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: %(message)s',
        datefmt="[%d/%m/%Y %H:%M]"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    
    if config_mode.lower().startswith("debug"):
        stdout_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        stdout_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    
    log_handler = logging.handlers.RotatingFileHandler(
        filename="logs/vectorbot_{:%Y-%m-%d_%H;%M}.log".format(datetime.datetime.now()), encoding='utf-8', mode='a', maxBytes=10**7, backupCount=5
    )
    log_handler.setFormatter(log_format)
    
    logger.addHandler(log_handler)
    logger.addHandler(stdout_handler)
    
    discord_logger = logging.getLogger('discord')
    if config_mode.lower().startswith('debug'):
        discord_logger.setLevel(logging.DEBUG)
    else:
        discord_logger.setLevel(logging.INFO)
    discord_handler = logging.FileHandler(
        filename='logs/discord_{:%Y-%m-%d_%H;%M}.log'.format(datetime.datetime.utcnow()),
        encoding='utf-8', mode='a'
    )
    discord_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: %(message)s',
            datefmt="[%d/%m/%Y %H:%M]"
        )
    )
    discord_logger.addHandler(discord_handler)
    
    return logger

def create_config():
    print("The config was not found, please input the following values! \n")
    config = {}
    config["Token"] = input("Please input bots token. \n>")
    config["Prefix"] = [input("Please input prefix. \n>")]
    default = {"Mode": "Default", "Modes": {"Default": config}}
    with open('config.json', 'w') as file:
        json.dump(default, file)
    return ("Default", config)

def setup_configs():
    config = {}
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        return create_config()
    else:
        return (config["Mode"], config["Modes"][config["Mode"]])

if __name__ == '__main__':
    mode, config = setup_configs()
    token = config.pop("Token")
    logger = setup_loggers(mode)
    loop = asyncio.get_event_loop()
    description = config.get("Description")
    prefix = commands.when_mentioned_or(config.get('Prefix', ['v!']))
    bot = VectorBot(
        config=config, logger=logger, loop=loop,
        description=description, command_prefix=prefix
    )
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        bot.logger.error(traceback.format_exc())