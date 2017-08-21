from discord.ext import commands
from .utils import checks, parser
import discord, asyncio

class Debug:
    """Debug Utilities.

    .. warning::
        ONLY ACTIVATE THIS IF YOU WANT TO DEBUG OR SPAMMED LOG"""

    def __init__(self, bot):
        self.bot = bot
        self.Config = bot.Config.get(self.__class__.__name__, None)

    def Print(self, msg):
        print("Debug:", msg)

    async def on_ready(self):
        self.Print("Ready")

    async def on_resumed(self):
        self.Print("Resumed")

    async def on_error(self, event, *args, **kwargs):
        self.Print("Error {}/{}/{}".format(event, args, kwargs))

    async def on_message(self, message):
        self.Print("Message: {}".format(message.__dict__))

    async def on_socket_raw_receive(self, msg):
        self.Print("Socket Raw Receive: {}".format(msg))

    async def on_socket_raw_send(self, payload):
        self.Print("Socket Raw Send: {}".format(payload))

    async def on_message_delete(self, message):
        self.Print("Message Deleted: {}".format(message.__dict__))

    async def on_message_edit(self, before, after):
        self.Print("Message: Before: {} / After {}".format(before.__dict__, after.__dict__))

def setup(bot):
    bot.add_cog(Debug(bot))
