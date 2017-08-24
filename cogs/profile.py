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
        self.Config = bot.Config.get(self.__class__.__name__, {})
        self.Splash = draw.Splash(
            WebsitePath=self.bot.Config["Splash Path"],
            BotPath=bot.currentDIR
        )

    @commands.command(pass_context=True, aliases=["sub"])
    async def subscribe(self, ctx, Mth: str=None, *, Role: str=None):
        """Subscribe to a role to get updates from the role!
        NOTE: That you need to write the exact name of the role!

        Example: V!sub (c)reate/(a)dd/(r)emove/(d)elete CSGO to have the CSGO role created/addded/removed/deleted (to/from your profile)/(to/from the guild)"""

        pass

        msgs = []
        MTHL = Mth.lower()
        if MTHL in ["create", "c"]:
            if checks.admin_or_permissions(manage_roles=True):
                msgs.append(await self.bot.send("Create Role not setup"))
            else:
                msgs.append(await self.bot.send("You do not have permission to do this!"))
        elif MTHL in ["add", "a"]:
            msgs.append(await self.bot.send("Add Role Not Setup Yet"))
        elif MTHL in ["remove", "r"]:
            msgs.append(await self.bot.send("Remove Role Not Setup Yet"))
        elif MTHL in ["delete", "d"]:
            if checks.admin_or_permissions(manage_roles=True):
                msgs.append(await self.bot.send("Delete Role not setup"))
            else:
                msgs.append(await self.bot.send("You do not have permission to do this!"))
        else:
            msgs.append(await self.bot.send("Please specifiy whether you want to create/add/remove a role!"))
        await asyncio.sleep(7)
        await self.bot.delete_messages(msgs)

    @commands.command()
    async def banner(self, ctx, *, args):
        """Get your own banner! Main Guild Only!"""
        message = ctx.message
        author = message.author
        guild = message.guild
        await self.bot.delete_message(message)
        if guild.id is self.bot.Config["Guild"]:
            await self.bot.send(
                author,
                "Here is your custom splash! {}/members/{}".format(
                    self.bot.Config["Splash Site"],
                    self.Splash.Check(member) # I won't do Update because in large guilds that can cause the bot to crash
                )
            )
        else:
            msg = await self.bot.send("That is not permitted here!")
            await asyncio.sleep(4)
            await self.bot.delete_message(msg)

    async def on_member_join(self, member):
        if member.guild.id is self.bot.Config["Guild"] and not member.bot:
            await self.bot.send(
                author,
                "Here is your custom splash! {}/members/{}".format(
                    self.bot.Config["Modes"][self.bot.Config["Mode"]]["Splash Site"],
                    self.Splash.Update(member)
                )
            )

    async def on_member_update(self, before, after):
        if after.guild.id == self.bot.Config["Guild"] and not after.bot:
            if before.name is not after.name:
                self.Splash.Update(after)
            elif before.game is not after.game:
                self.Splash.Update(after)
            elif before.roles is not after.roles:
                self.Splash.Update(after)
            elif before.avatar_url is not after.avatar_url:
                self.Splash.Update(after)
            elif before.status is not after.status:
                self.Splash.Update(after)

    async def on_member_ban(self, member):
        if member.guild.id == self.bot.Config["Guild"]:
            self.Splash.Remove(member.id)

    async def on_member_remove(self, member):
        if member.guild.id == self.bot.Config["Guild"]:
            self.Splash.Remove(member.id)

def setup(bot):
    bot.add_cog(Profile(bot))
