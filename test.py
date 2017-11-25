#!/usr/bin/python3.6
# TESTY TESTY!!!
# This file will change over time because I test things here. DUH

import discord
from discord.ext import commands
import configs
import datetime

status = ""

class VectorBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="V!",
            description="VectorBot",
            pm_help=True,
            help_attrs=dict(hidden=True)
        )

        self.add_command(self.hi)

    async def on_ready(self):
        print('Logged in as:')
        print('User:', self.user.name+"#"+self.user.discriminator)
        print('ID: ', self.user.id)
        print('------')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print("Started:")
        await self.change_presence(
            game=discord.Game(
                name="V!help",
                url="https://twitch.tv/tagnumelite",
                type=1
            )
        )

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting Down")
        await self.logout()

if __name__ == "__main__":
    bot = VectorBot()
    bot.run(configs.token, reconnect=True)
