from discord.ext import commands
from .utils import checks, config
import discord
import inspect
import feedparser

# to expose to the eval command
import datetime
from collections import Counter

class Feeds:
    """Feed Commands"""

    def __init__(self, bot):
        self.bot = bot

    async def checks_for_feeds(self):
        await self.bot.wait_until_ready()

    @commands.command(pass_context=True)
    async def feeds(self, ctx):
        return

def setup(bot):
    bot.add_cog(Feeds(bot))
