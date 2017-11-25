from discord.ext import commands
from .utils import checks, config

import random
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

    def __unload(self):
        """Clean Up Scripts"""
        pass

    async def __local_check(self, ctx):
        """Checks that apply to every command in here"""
        pass

    async def __global_check(self, ctx):
        """Checks that apply to every command in the bot"""
        pass

    async def __global_check_once(self, ctx):
        """check that apply to every command but is guaranteed to be called only once"""
        return True

    async def __error(self, ctx, error):
        """error handling to every command in here"""
        pass

    async def __before_invoke(self, ctx):
        """called before a command is called here"""
        pass

    async def __after_invoke(self, ctx):
        """called after a command is called here"""
        pass

    @commands.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def prune(self, ctx, number: int, user=None):
        """Deletes messages from the chat!
        Example:
        V!prune 5 to delete 5 messages!
        V!prune 5 @Example to delete 5 messages by the user @Example"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        await self.bot.send("NOT SETUP YET")
        return
        if number == 0:
            await self.bot.send("Please specify a number higher than 0")
            return
        try:
            deleted = await self.bot.purge_from(channel, limit=number, check=is_member)
            await self.bot.send('Deleted {} message(s)'.format(len(deleted)))
        except Exception as e:
            await self.bot.send("{}".format(e))

    @commands.command()
    @commands.cooldown(rate=2, per=3600.0)
    @commands.is_owner()
    async def setavatar(self, ctx, url=None):
        """Sets the bots avatar! Semi-Working!"""

        msgs = [ctx.message]
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        if url == None:
            if len(msgs[0].attachments) >= 1:
                url = msgs[0].attachments[0]["url"]
            else:
                msgs.append(await channel.send("Please give a url to change to or upload an image to update to!"))
        if url != None:
            image = urllib.urlretrieve(url, "avatar.png")
            try:
                await self.bot.edit_profile(avatar=image)
            except discord.InvalidArgument:
                msgs.append(await channel.send("Please upload the appropriate image format"))
            except Exception as E:
                msgs.append(await channel.send("Exception! :{}:".format(E)))
            except discord.HTTPException as HE:
                msgs.append(await channel.send("Failed to edit avatar: {}".format(HE)))
            except discord.ClientException:
                msgs.append(await channel.send("Non-Bot Account"))
            else:
                msgs.append(await channel.send("This script may be broken, don't expect it to work!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)

    @commands.command(pass_context=True, aliases=["setname"])
    @commands.cooldown(rate=2, per=3600.0)
    @commands.is_owner()
    async def setusername(self, ctx, username=None):
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        if username == None:
            await channel.send("Please specify a username to give!")
            return
        if self.bot.user.bot:
            try:
                await self.bot.edit_profile(username=username)
            except Exception as E:
                await channel.send("Exception! :{}:".format(E))
            else:
                await channel.send("Username was changed to {}".format(username))

    @commands.command()
    async def ping(self, ctx):
        """Ping Command"""
        msg = ctx.message
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        created = msg.timestamp
        now = datetime.datetime.utcnow()
        ping = now - created
        await channel.send("PING!: %s" % (ping.microseconds)+"ms")

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, status):
        """Changes the Bots status"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        await self.bot.change_presence(game=discord.Game(name=status))

    @commands.command()
    async def rules(self, ctx):
        """Get the rules of the current guild!"""
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        channel = ctx.channel
        em = discord.Embed(
            title=self.bot.Config["Rules"]["Title"].format(
                guild=guild.name,
                channel=channel.name,
                author=author.name
            ),
            description=self.bot.Config["Rules"]["Description"].format(
                guild=guild.name,
                channel=channel.name,
                author=author.name
            ),
            color=0xff0000
        )
        em.set_image(url=self.bot.Config["Rules"]["Image"])
        em.set_thumbnail(url=self.bot.Config["Rules"]["Thumbnail"])
        if self.bot.Config["Rules"]["Footer"]["Enabled"]:
            em.set_footer(
                text=self.bot.Config["Rules"]["Footer"]["Text"].format(guild=guild.name),
                icon_url=self.bot.Config["Rules"]["Footer"]["Icon Url"].format(guild_icon=guild.icon_url)
            )
        if self.bot.Config["Rules"]["Author"]["Enabled"]:
            em.set_author(
                name=self.bot.Config["Rules"]["Author"]["Name"].format(guild=guild.name),
                icon_url=self.bot.Config["Rules"]["Author"]["Avatar Url"].format(guild_icon=guild.icon_url)
            )

        for rule in self.bot.Config["Rules"]["Inline"]:
            em.add_field(
                name=rule["Name"],
                value=rule["Rule"],
                inline=rule["Inline"] if "Inline" in rule else False
            )
        try:
            await bot.delete_message(msg)
        except Exception as E:
            print(
                """Error deleteing command `rules` run by %s(%s) on guild %s(%s) in channel %s(%s)
    Error: {0}""".format(E) % (
                    author, author.id,
                    guild, guild.id,
                    channel, channel.id
                ),
                datetime.datetime.utcnow()
            )
        await author.send(embed=em)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        """Logs Bot out of Discord"""
        await ctx.channel.send("Logging Out")
        await asyncio.sleep(2)
        await self.bot.logout()

    @commands.command()
    async def invite(self, ctx):
        """Creates an invite link for the bot"""

        await ctx.channel.send(
            discord.utils.ouath_url(
                client_id=self.bot.user.id,
                permissions=discord.Permission(8)
            )
        )

    @commands.command()
    async def avatar(self, ctx, user=None):
        """Get your avatar and if user is specified then gets the users avatar!"""
        message = ctx.message
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        if user == None:
            if author.avatar_url == "":
                await channel.send("You have no avatar!")
                return
            else:
                await channel.send(author.avatar_url)
                return
        else:
            members = guild.members
            if members == None:
                await channel.send("Members not found!")
                return
            member = checks.find_user(user, members)
            if member == None:
                print(member)
                await channel.send("User not found!")
                return
            elif member == False:
                await channel.send("No user was found matching %s" % (user))
                return
            else:
                if member.avatar_url == "":
                    await channel.send("%s has no avatar!" % (member.name))
                else:
                    await channel.send("%s avatar url: %s" % (member.mention, member.avatar_url))

    @commands.command()
    async def icon(self, ctx):
        """Gets the guilds icon"""
        message = ctx.message
        guild = ctx.guild
        channel = ctx.channel
        if guild.icon_url == "":
            await channel.send("%s has no icon!" % (guild.name))
        else:
            await channel.send("%s icon is: %s" % (guild.name, guild.icon_url))

    @commands.command()
    async def splash(self, ctx):
        """Gets the guilds slpash"""
        message = ctx.message
        guild = ctx.guild
        channel = ctx.channel
        if guild.splash_url == "":
            await channel.send("%s has no splash!" % (guild.name))
        else:
            await channel.send("%s splash is %s" % (guild.name, guild.splash_url))

    @commands.command()
    async def size(self, ctx):
        """Gets the guilds total member count"""
        message = ctx.message
        guild = ctx.guild
        channel = ctx.channel
        if guild.member_count == 0:
            await channel.send("Guild has no members! WAIT WHAT!")
        else:
            await channel.send("%s total member count: %s" % (guild.name, guild.member_count))

    @commands.command()
    async def created(self, ctx):
        """Gets the guilds creation time"""
        message = ctx.message
        guild = ctx.guild
        channel = ctx.channel
        if guild.created_at == None:
            await channelsend("Guild has no creation date! WAIT WHAT!")
        else:
            await channel.send("%s was created on: %s" % (guild.name, guild.created_at))

    @commands.command()
    async def choose(self, ctx, *choices : str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

def setup(bot):
    bot.add_cog(Utilities(bot))
