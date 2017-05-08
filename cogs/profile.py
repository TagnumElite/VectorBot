from discord.ext import commands
import discord
from .utils import checks, draw
import inspect
import urllib
import asyncio

# to expose to the eval command
import datetime
from collections import Counter

def getS(status):
    if status == discord.Status.online:
        return "Online"
    elif status == discord.Status.offline:
        return "Offline"
    elif status == discord.Status.idle:
        return "IDLE"
    elif status == discord.Status.do_not_disturb:
        return "DnD"
    elif status == discord.Status.invisible:
        return "Invisible"
    else:
        return "None"

class Profile:
    """Profile Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def banner(self, ctx):
        """Gets your own banner! Main/Dev Server Only!"""
        message = ctx.message
        author = message.author
        server = message.server
        if server.id == "Main Server" or "Dev Server":
            if author.game == None:
                game = "Not Playing"
            else:
                game = author.game.name
            if author.top_role == server.default_role:
                r = 255
                g = 255
                b = 255
            else:
                r = author.top_role.colour.r
                g = author.top_role.colour.g
                b = author.top_role.colour.b
            await self.bot.send_message(author, "Here is your custom splash! http://splash.example.com/members/{}".format(draw.splash(author.id, author.name, author.avatar_url, game, getS(author.status), (r,g,b))))
        else:
            await self.bot.say("That is not permitted here!")
        await asyncio.sleep(3)
        await self.bot.delete_message(message)

    async def on_member_join(self, member):
        if member.server.id == "Main Server" or "Dev Server":
            if member.game == None:
                game = "Not Playing"
            else:
                game = member.game.name
            if member.top_role == member.server.default_role:
                r = 255
                g = 255
                b = 255
            else:
                r = member.top_role.colour.r
                g = member.top_role.colour.g
                b = member.top_role.colour.b
            await self.bot.send_message(member, "Here is your custom splash! http://splash.example.com/members/{}".format(draw.splash(member.id, member.name, member.avatar_url, game, getS(member.status), (r,g,b))))

    async def on_member_remove(self, member):
        if member.server.id == "Main Server" or "Dev Server":
            draw.remove(member.id)

    async def on_member_update(self, before, after):
        if after.server.id == "Main Server" or "Dev Server":
            print("UPDATING SPLASH")
            if after.game == None:
                game = "Not Playing"
            else:
                game = after.game.name
            if after.top_role == after.server.default_role:
                r = 255
                g = 255
                b = 255
            else:
                r = after.top_role.colour.r
                g = after.top_role.colour.g
                b = after.top_role.colour.b
            draw.splash(after.id, after.name, after.avatar_url, game, getS(after.status), (r,g,b))

    async def on_member_ban(self, member):
        if member.server.id == "Main Server" or "Dev Server":
            draw.remove(member.id)

    async def on_member_unban(self, server, user):
        return

def setup(bot):
    bot.add_cog(Profile(bot))
