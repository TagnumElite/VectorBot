"""Social system is only an experiment of mine."""

from discord.ext import commands
from ..utils import checks, config
import discord
import asyncio

class Social:
    """Handles the bot's Social system."""

    def __init__(self, bot):
        self.bot = bot
        self.Config = bot.Config.get(self.__class__.__name__, {})
        self.bot.loop.create_task(self.check_feeds())
        self.checked_feeds = {}

    async def check_feeds(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            await asyncio.sleep(60)

def setup(bot):
    bot.add_cog(Social(bot))
