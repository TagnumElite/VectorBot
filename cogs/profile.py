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
        self.Splash = draw.Splash(WebsitePath=bot.Configs["Splash Path"], BotPath=bot.currentDIR)

    @commands.command(pass_context=True, aliases=["sub"])
    async def subscribe(self, ctx, Mth: str=None, *, Role: str=None):
        """Subscribe to a role to get updates from the role!
        NOTE: That you need to write the exact name of the role!

        Example: V!sub (c)reate/(a)dd/(r)emove/(d)elete CSGO to have the CSGO role created/addded/removed/deleted (to/from your profile)/(to/from the server)"""

        msgs = []
        MTHL = Mth.lower()
        if MTHL in ["create", "c"]:
            if checks.admin_or_permissions(manage_roles=True):
                msgs.append(await self.bot.say("Create Role not setup"))
            else:
                msgs.append(await self.bot.say("You do not have permission to do this!"))
        elif MTHL in ["add", "a"]:
            msgs.append(await self.bot.say("Add Role Not Setup Yet"))
        elif MTHL in ["remove", "r"]:
            msgs.append(await self.bot.say("Remove Role Not Setup Yet"))
        elif MTHL in ["delete", "d"]:
            if checks.admin_or_permissions(manage_roles=True):
                msgs.append(await self.bot.say("Delete Role not setup"))
            else:
                msgs.append(await self.bot.say("You do not have permission to do this!"))
        else:
            msgs.append(await self.bot.say("Please specifiy whether you want to create/add/remove a role!"))
        await asyncio.sleep(7)
        await self.bot.delete_messages(msgs)

    @commands.command(pass_context=True)
    async def banner(self, ctx):
        """Gets your own banner! Main Server Only!"""
        message = ctx.message
        author = message.author
        server = message.server
        await self.bot.delete_message(message)
        if server.id == self.bot.Configs["Bot Server"] or self.bot.Configs["Dev Server"]:
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
            await self.bot.send_message(author, "Here is your custom splash! {}/members/{}".format(self.bot.Configs["Splash Site"], self.Splash.Update(author.id, author.name, author.avatar_url, game, getS(author.status), (r,g,b))))
        else:
            msg = await self.bot.say("That is not permitted here!")
            await asyncio.sleep(4)
            await self.bot.delete_message(msg)

    async def on_member_join(self, member):
        if member.server.id == self.bot.Configs["Bot Server"] or self.bot.Configs["Dev Server"]:
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
            await self.bot.send_message(author, "Here is your custom splash! {}/members/{}".format(self.bot.Configs["Splash Site"], self.Splash.Update(author.id, author.name, author.avatar_url, game, getS(author.status), (r,g,b))))

    async def on_member_remove(self, member):
        if member.server.id == self.bot.Configs["Bot Server"] or self.bot.Configs["Dev Server"]:
            self.Splash.remove(member.id)

    async def on_member_update(self, before, after):
        if after.server.id == self.bot.Configs["Bot Server"] or self.bot.Configs["Dev Server"]:
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
            self.Splash.Update(author.id, author.name, author.avatar_url, game, getS(author.status), (r,g,b))

    async def on_member_ban(self, member):
        if member.server.id == self.bot.Configs["Bot Server"] or self.bot.Configs["Dev Server"]:
            self.Splash.remove(member.id)

def setup(bot):
    bot.add_cog(Profile(bot))
