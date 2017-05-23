from discord.ext import commands
from .utils import checks, config
from PIL import Image
import discord
import inspect

class Image:
    """Image Manipulation

    .. warning::
        NOT SETUP"""

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Image(bot))
