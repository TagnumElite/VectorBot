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
        self.Configs = bot.Configs

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
        if url == None:
            await self.bot.say("Please give a url to change to!")
            return
        if self.bot.user.bot:
            image = urllib.urlretrieve(url, "avatar.png")
            await self.bot.edit_profile(avatar=image)
            await self.bot.say("This script may be broken, don't expect it to work!")

    @commands.command(pass_context=True, aliases=["setname"])
    @commands.cooldown(rate=2, per=3600.0)
    @checks.admin_or_permissions(manage_server=True)
    async def setusername(self, ctx, username=None):
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
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

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def status(self, ctx, *, status):
        """Changes the Bots status"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        await self.bot.change_presence(game=discord.Game(name=status))

    @commands.command(pass_context=True)
    async def rules(self, ctx):
        """Get the rules of the current server!"""
        msg = ctx.message
        server = msg.server
        author = msg.author
        channel = msg.channel
        #TODO: Remember to make an if statement to check if the server has overridden rules!
        em = discord.Embed(
            title=self.Configs["Rules"]["Title"].format(
                server=server.name,
                channel=channel.name,
                author=author.name
            ),
            description=self.Configs["Rules"]["Description"].format(
                server=server.name,
                channel=channel.name,
                author=author.name
            ),
            color=0xff0000
        )
        em.set_image(url=self.Configs["Rules"]["Image"])
        em.set_thumbnail(url=self.Configs["Rules"]["Thumbnail"])
        if self.Configs["Rules"]["Footer"]["Enabled"]:
            em.set_footer(
                text=self.Configs["Rules"]["Footer"]["Text"].format(server=server.name),
                icon_url=self.Configs["Rules"]["Footer"]["Icon Url"].format(server_icon=server.icon_url)
            )
        if self.Configs["Rules"]["Author"]["Enabled"]:
            em.set_author(
                name=self.Configs["Rules"]["Author"]["Name"].format(server=server.name),
                icon_url=self.Configs["Rules"]["Author"]["Avatar Url"].format(server_icon=server.icon_url)
            )

        for rule in self.Configs["Rules"]["Rules"]:
            em.add_field(
                name=rule["Name"],
                value=rule["Rule"],
                inline=rule["Inline"] if "Inline" in rule else False
            )
        try:
            await bot.delete_message(msg)
        except Exception as E:
            await log_message(
                """Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
    Error: {0}""".format(E) % (
                    author, author.id,
                    server, server.id,
                    channel, channel.id
                ),
                datetime.datetime.utcnow()
            )
        await self.bot.send_message(author, embed=em)

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def logout(self, ctx):
        """Logs Bot out of Discord"""
        await self.bot.say("Logging Out")
        await asyncio.sleep(2)
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Utilities(bot))
