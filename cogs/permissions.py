from discord.ext import commands
from .utils import config, checks

class Permissions:
    """Handles the bot's permission system."""

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Permissions(bot))
