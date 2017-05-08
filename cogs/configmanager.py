from discord.ext import commands
import discord
from .utils import checks, config
import inspect
import asyncio

# to expose to the eval command
import datetime
from collections import Counter

class ConfigManager:
    """Config Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def serverC(self, ctx):
        print("say serverC")
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        if config.exists(server.id, self.bot) == "Yes":
            print("say true")
            await self.bot.say(config.getServerConfig(server.id, self.bot))
        elif cofig.exists(server.id, self.bot) == "Not Yet":

        else:
            await self.bot.say("Server config doesn't exist! Creating...")
            print("say false")
            config.createServerConfig(server, self.bot.currentDIR)
            await self.bot.say("Created Server Config File")

    @commands.command(pass_context=True)
    async def emailT(self, ctx):
        return

    @commands.command(pass_context=True)
    async def sendE(self, ctx, reciever: str, *, content):
        eServer = email.Email("")

    async def on_message(self, message):
        if checks.offensive(message.content):
            await self.bot.delete_message(message)
        return

def setup(bot):
    bot.add_cog(ConfigManager(bot))
