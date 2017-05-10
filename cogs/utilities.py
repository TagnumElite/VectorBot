from discord.ext import commands
from .utils import checks, config
import discord
import inspect
import urllib

# to expose to the eval command
import datetime
from collections import Counter

def is_member(m, u):
    return m.author == u

class Utilities:
    """Utilities Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def prune(self, ctx, number: int, user=None):
        """Deletes messages from the chat!
        Example:
        V!prune 5 to delete 5 messages!
        V!prune 5 @Example to delete 5 messages by the user @Example"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `prune` in channel %s(%s) on server %s(%s)" % (author, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        await self.bot.say("NOT SETUP YET")
        return
        if number == 0:
            await self.bot.say("Please specify a number higher than 0")
            return
        try:
            deleted = await self.bot.purge_from(channel, limit=number, check=is_member)
            await self.bot.say('Deleted {} message(s)'.format(len(deleted)))
        except Exception as e:
            await self.bot.say("{}".format(e))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=2, per=3600.0)
    @checks.admin_or_permissions(manage_server=True)
    async def setavatar(self, ctx, url=None):
        """Sets the bots avatar! BROKEN!"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `setavatar` in channel %s(%s) on server %s(%s)" % (author, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if url == None:
            await self.bot.say("Please give a url to change to!")
            return
        if self.bot.user.bot:
            image = urllib.urlretrieve(url, "avatar.png")
            await self.bot.edit_profile(avatar=image)
            await self.bot.say("This script may be broken, don't expect it to work!")

    @commands.command(pass_context=True)
    @commands.cooldown(rate=2, per=3600.0)
    @checks.admin_or_permissions(manage_server=True)
    async def setusername(self, ctx, username=None):
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `setusername` in channel %s(%s) on server %s(%s)" % (author, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if username == None:
            await self.bot.say("Please specify a username to give!")
            return
        if self.bot.user.bot:
            try:
                await self.bot.edit_profile(username=username)
            except Exception as e:
                await self.bot.say("Exception! :{}:".format(e))
            else:
                await self.bot.say("Username was changed to {}".format(username))

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Ping Command"""
        msg = ctx.message
        author = msg.author
        server = msg.server
        channel = msg.channel
        created = msg.timestamp
        now = datetime.datetime.utcnow()
        ping = now - created
        await self.bot.say("PING!: %s"+"ms") % (str(ping.microseconds))
        await checkslog_message("User %s(%s) ran command `test` on server %s(%s) in channel %s(%s)" % (author, author.id, server.name, server.id, channel.name, channel.id), self.bot)

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def status(self, ctx, *, status):
        """Changes the Bots status"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `status` in channel %s(%s) on server %s(%s) String: \"%s\"" % (author, author.id, channel.name, channel.id, server.name, server.id, status), self.bot)
        await self.bot.change_presence(game=discord.Game(name=status))

def setup(bot):
    bot.add_cog(Utilities(bot))
