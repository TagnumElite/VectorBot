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

    @commands.command()
    async def banner(self, ctx, *, args):
        """Get your own banner! Main Guild Only!"""
        message = ctx.message
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        await self.bot.delete_message(message)
        if guild.id is self.bot.Config["Guild"]:
            await author.send(
                "Here is your custom splash! {}/members/{}".format(
                    self.bot.Config["Splash Site"],
                    self.Splash.Check(member) # I won't do Update because in large guilds that can cause the bot to crash
                )
            )
        else:
            msg = await channel.send("That is not permitted here!")
            await asyncio.sleep(4)
            await msg.delete()

    async def on_member_join(self, member):
        if member.guild.id is self.bot.Config["Guild"] and not member.bot:
            await member.send(
                "Here is your custom splash! {}/members/{}".format(
                    self.bot.Config["Splash Site"],
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
            else:
                return

    async def on_member_ban(self, member):
        if member.guild.id == self.bot.Config["Guild"]:
            self.Splash.Remove(member.id)

    async def on_member_remove(self, member):
        if member.guild.id == self.bot.Config["Guild"]:
            self.Splash.Remove(member.id)

def setup(bot):
    bot.add_cog(Profile(bot))
