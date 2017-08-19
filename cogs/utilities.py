from discord.ext import commands
from .utils import checks, config
import discord
import asyncio
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
        self.Config = bot.Config.get(self.__class__.__name__, {})

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
    async def setavatar(self, ctx, url=None):
        """Sets the bots avatar! BROKEN!"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
        if url == None:
            await self.bot.say("Please give a url to change to!")
            return
        if self.bot.user.bot:
            image = urllib.urlretrieve(url, "avatar.png")
            await self.bot.edit_profile(avatar=image)
            await self.bot.say("This script may be broken, don't expect it to work!")

    @commands.command(pass_context=True, aliases=["setname"])
    @commands.cooldown(rate=2, per=3600.0)
    async def setusername(self, ctx, username=None):
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
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
    async def status(self, ctx, *, status):
        """Changes the Bots status"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
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
            title=self.Config["Rules"]["Title"].format(
                server=server.name,
                channel=channel.name,
                author=author.name
            ),
            description=self.Config["Rules"]["Description"].format(
                server=server.name,
                channel=channel.name,
                author=author.name
            ),
            color=0xff0000
        )
        em.set_image(url=self.Config["Rules"]["Image"])
        em.set_thumbnail(url=self.Config["Rules"]["Thumbnail"])
        if self.Config["Rules"]["Footer"]["Enabled"]:
            em.set_footer(
                text=self.Config["Rules"]["Footer"]["Text"].format(server=server.name),
                icon_url=self.Config["Rules"]["Footer"]["Icon Url"].format(server_icon=server.icon_url)
            )
        if self.Config["Rules"]["Author"]["Enabled"]:
            em.set_author(
                name=self.Config["Rules"]["Author"]["Name"].format(server=server.name),
                icon_url=self.Config["Rules"]["Author"]["Avatar Url"].format(server_icon=server.icon_url)
            )

        for rule in self.Config["Rules"]["Rules"]:
            em.add_field(
                name=rule["Name"],
                value=rule["Rule"],
                inline=rule["Inline"] if "Inline" in rule else False
            )
        try:
            await bot.delete_message(msg)
        except Exception as E:
            print(
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
    async def logout(self, ctx):
        """Logs Bot out of Discord"""
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
        await self.bot.say("Logging Out")
        await asyncio.sleep(2)
        await self.bot.logout()

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """Creates an invite link for the bot"""

        await self.bot.say(
            "https://discordapp.com/oauth2/authorize?client_id={CLIENTID}&scope=bot&permissions=8".format(
                CLIENTID=self.bot.user.id
            )
        )

    @commands.command(pass_context=True)
    async def avatar(self, ctx, user=None):
        """Get your avatar and if user is specified then gets the users avatar!"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        print("User %s(%s) ran command `avatar` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
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
        print("User %s(%s) ran command `icon` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
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
        print("User %s(%s) ran command `splash` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
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
        print("User %s(%s) ran command `size` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
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
        print("User %s(%s) ran command `created` in channel %s(%s) on server %s(%s)" % (author.name, author.id, channel.name, channel.id, server.name, server.id), self.bot)
        if server.created_at == None:
            await self.bot.say("Server has no creation date! WAIT WHAT!")
        else:
            await self.bot.say("%s was created on: %s" % (server.name, server.created_at))

def setup(bot):
    bot.add_cog(Utilities(bot))
