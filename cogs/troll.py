from discord.ext import commands
from .utils import checks
import discord, asyncio

class Troll:
    """Troll Commands, used for annoying all"""

    def __init__(self, bot):
        self.bot = bot
        self.Config = bot.Config.get(self.__class__.__name__, {})

    async def on_message(self, message):
        if len(message.attachments) > 0:
            print("Message Attach:", message.attachments)
        else:
            return

def setup(bot):
    bot.add_cog(Troll(bot))
