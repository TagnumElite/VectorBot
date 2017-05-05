from discord.ext import commands
from .utils import checks, config
import discord
import inspect

# to expose to the eval command
import datetime
from collections import Counter

class Misc:
    """Misc Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def avatar(self, ctx, user=None):
        """Get your avatar and if user is specified then gets the users avatar!"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `avatar` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if user == None:
            if author.avatar_url == "":
                await self.bot.say("You have no avatar!")
                return
            else:
                await self.bot.say(author.avatar_url)
                return
        else:
            members = server.members
            if members == None:
                await self.bot.say("Members not found!")
                return
            member = checks.find_user(user, members)
            if member == None:
                print(member)
                await self.bot.say("User not found!")
                return
            elif member == False:
                await self.bot.say("No user was found matching %s" % (user))
                return
            else:
                if member.avatar_url == "":
                    await self.bot.say("%s has no avatar!" % (member.name))
                else:
                    await self.bot.say("%s avatar url: %s" % (member.mention, member.avatar_url))

    @commands.command(pass_context=True)
    async def icon(self, ctx):
        """Gets the servers icon"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `icon` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if server.icon_url == "":
            await self.bot.say("%s has no icon!" % (server.name))
        else:
            await self.bot.say("%s icon is: %s" % (server.name, server.icon_url))

    @commands.command(pass_context=True)
    async def splash(self, ctx):
        """Gets the servers slpash"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `splash` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if server.splash_url == "":
            await self.bot.say("%s has no splash!" % (server.name))
        else:
            await self.bot.say("%s splash is %s" % (server.name, server.splash_url))

    @commands.command(pass_context=True)
    async def size(self, ctx):
        """Gets the servers total member count"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `size` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if server.member_count == 0:
            await self.bot.say("Server has no members! WAIT WHAT!")
        else:
            await self.bot.say("%s total member count: %s" % (server.name, server.member_count))

    @commands.command(pass_context=True)
    async def created(self, ctx):
        """Gets the servers creation time"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `created` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if server.created_at == None:
            await self.bot.say("Server has no creation date! WAIT WHAT!")
        else:
            await self.bot.say("%s was created on: %s" % (server.name, server.created_at))

def setup(bot):
    bot.add_cog(Misc(bot))
