from discord.ext import commands
from .utils import checks
import discord
import inspect

# to expose to the eval command
import datetime
from collections import Counter

class Admin:
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def load(self, *, module : str):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def unload(self, *, module : str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def _reload(self, *, module : str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await self.bot.say('\N{PISTOL}')
            await self.bot.say('{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def debug(self, ctx, *, code : str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.say(python.format(result))

    ''' Disabling all ban commands as discord has released audit logs!
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def ban(self, ctx, user=None, reason=None, msgs=0):
        """BAN HAMMER"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `ban` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), bot=self.bot)
        if user == None:
            await self.bot.say("Please specify user to ban")
            return
        if reason == None:
            await self.bot.say("Please give an reason!")
            return
        if server == None:
            await self.bot.say("Server not found")
            return
        members = server.members
        if members == None:
            await self.bot.say("Members not found")
            return
        member = checks.find_user(user, members)
        if member == None:
            print(member)
            await self.bot.say("User not found")
            return
        elif member == False:
            await self.bot.say("No user was found matching %s" % (user))
            return
        else:
            try:
                await self.bot.ban(member, delete_message_days=msgs)
                await self.bot.say("User %s was banned by " % (member))
            except Exception as e:
                await self.log_message("Banning failed: {0}".format(e))

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def unban(self, ctx, user=None, reason=None, msgs=0):
        """CUPCAKE"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `unban` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), bot=self.bot)
        if user == None:
            await self.bot.say("Please specify user to unban")
            return
        if reason == None:
            await self.bot.say("Please give an reason!")
            return
        if server == None:
            await self.bot.say("Server not found")
            return
        try:
            members = await self.bot.get_bans(server)
        except Exception as e:
            await self.log_message("Failed to get bans: {}".format(e), bot=self.bot)
        if members == None:
            await self.bot.say("Members not found")
            return
        member = checks.find_user(user, members)
        if member == None:
            print(member)
            await self.bot.say("User not found")
            return
        elif member == False:
            await self.bot.say("No user was found matching %s" % (user))
            return
        else:
            try:
                await self.bot.unban(member)
                await self.bot.say("User %s was unbanned by " % (member))
            except Exception as e:
                await checks.log_message("Unbanning failed: {0}".format(e), bot=self.bot)

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def banned(self, ctx, user=None):
        """Gets banned users unless a user is passed then gives data about banned user."""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await checks.log_message("User %s(%s) ran command `banned` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), bot=self.bot)
        try:
            members = await self.bot.get_bans(server)
        except Exception as e:
            await self.log_message("Failed to get bans: {}".format(e), bot=self.bot)
        if members == None:
            await self.bot.say("Members not found")
            return
        if user != None:
            member = checks.find_user(user, members)

        else:
            membersNames = []
            members
            await self.bot.say("")
    '''

def setup(bot):
    bot.add_cog(Admin(bot))
