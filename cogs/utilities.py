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
    async def setavatar(self, ctx, url=None):
        """Sets the bots avatar! Semi-Working!"""

        msgs = [ctx.message]
        author = msgs[0].author
        guild = msgs[0].guild
        channel = msgs[0].channel
        if msgs[0].author.id is not self.bot.Config["Owner"]:
            msgs.append(self.bot.send("You do not have the required permission"))
        else:
            if url == None:
                if len(msgs[0].attachments) >= 1:
                    url = msgs[0].attachments[0]["url"]
                else:
                    msgs.append(await self.bot.send("Please give a url to change to or upload an image to update to!"))
            if url != None:
                image = urllib.urlretrieve(url, "avatar.png")
                try:
                    await self.bot.edit_profile(avatar=image)
                except discord.InvalidArgument:
                    msgs.append(await self.bot.send("Please upload the appropriate image format"))
                except Exception as E:
                    msgs.append(await self.bot.send("Exception! :{}:".format(E)))
                except discord.HTTPException as HE:
                    msgs.append(await self.bot.send("Failed to edit avatar: {}".format(HE)))
                except discord.ClientException:
                    msgs.append(await self.bot.send("Non-Bot Account"))
                else:
                    msgs.append(await self.bot.send("This script may be broken, don't expect it to work!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)

    @commands.command(pass_context=True, aliases=["setname"])
    @commands.cooldown(rate=2, per=3600.0)
    async def setusername(self, ctx, username=None):
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
        if username == None:
            await self.bot.send("Please specify a username to give!")
            return
        if self.bot.user.bot:
            try:
                await self.bot.edit_profile(username=username)
            except Exception as E:
                await self.bot.send("Exception! :{}:".format(E))
            else:
                await self.bot.send("Username was changed to {}".format(username))

    @commands.command()
    async def ping(self, ctx):
        """Ping Command"""
        msg = ctx.message
        author = msg.author
        guild = msg.guild
        channel = msg.channel
        created = msg.timestamp
        now = datetime.datetime.utcnow()
        ping = now - created
        await self.bot.send("PING!: %s"+"ms") % (str(ping.microseconds))

    @commands.command(pass_context=True, hidden=True)
    async def status(self, ctx, *, status):
        """Changes the Bots status"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
        await self.bot.change_presence(game=discord.Game(name=status))

    @commands.command()
    async def rules(self, ctx):
        """Get the rules of the current guild!"""
        msg = ctx.message
        guild = msg.guild
        author = msg.author
        channel = msg.channel
        #TODO: Remember to make an if statement to check if the guild has overridden rules!
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
        await self.bot.send(author, embed=em)

    @commands.command(pass_context=True, hidden=True)
    async def logout(self, ctx):
        """Logs Bot out of Discord"""
        if ctx.message.author.id is not self.bot.Config["Owner"]:
            return
        await self.bot.send("Logging Out")
        await asyncio.sleep(2)
        await self.bot.logout()

    @commands.command()
    async def invite(self, ctx):
        """Creates an invite link for the bot"""

        await self.bot.send(
            discord.utils.ouath_url(
                client_id=self.bot.user.id,
                permissions=discord.Permission(8)
            )
        )

    @commands.command()
    async def avatar(self, ctx, user=None):
        """Get your avatar and if user is specified then gets the users avatar!"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        print("User %s(%s) ran command `avatar` in channel %s(%s) on guild %s(%s)" % (author.name, author.id, channel.name, channel.id, guild.name, guild.id), self.bot)
        if user == None:
            if author.avatar_url == "":
                await self.bot.send("You have no avatar!")
                return
            else:
                await self.bot.send(author.avatar_url)
                return
        else:
            members = guild.members
            if members == None:
                await self.bot.send("Members not found!")
                return
            member = checks.find_user(user, members)
            if member == None:
                print(member)
                await self.bot.send("User not found!")
                return
            elif member == False:
                await self.bot.send("No user was found matching %s" % (user))
                return
            else:
                if member.avatar_url == "":
                    await self.bot.send("%s has no avatar!" % (member.name))
                else:
                    await self.bot.send("%s avatar url: %s" % (member.mention, member.avatar_url))

    @commands.command()
    async def icon(self, ctx):
        """Gets the guilds icon"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        print("User %s(%s) ran command `icon` in channel %s(%s) on guild %s(%s)" % (author.name, author.id, channel.name, channel.id, guild.name, guild.id), self.bot)
        if guild.icon_url == "":
            await self.bot.send("%s has no icon!" % (guild.name))
        else:
            await self.bot.send("%s icon is: %s" % (guild.name, guild.icon_url))

    @commands.command()
    async def splash(self, ctx):
        """Gets the guilds slpash"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        print("User %s(%s) ran command `splash` in channel %s(%s) on guild %s(%s)" % (author.name, author.id, channel.name, channel.id, guild.name, guild.id), self.bot)
        if guild.splash_url == "":
            await self.bot.send("%s has no splash!" % (guild.name))
        else:
            await self.bot.send("%s splash is %s" % (guild.name, guild.splash_url))

    @commands.command()
    async def size(self, ctx):
        """Gets the guilds total member count"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        print("User %s(%s) ran command `size` in channel %s(%s) on guild %s(%s)" % (author.name, author.id, channel.name, channel.id, guild.name, guild.id), self.bot)
        if guild.member_count == 0:
            await self.bot.send("Guild has no members! WAIT WHAT!")
        else:
            await self.bot.send("%s total member count: %s" % (guild.name, guild.member_count))

    @commands.command()
    async def created(self, ctx):
        """Gets the guilds creation time"""
        message = ctx.message
        author = message.author
        guild = message.guild
        channel = message.channel
        print("User %s(%s) ran command `created` in channel %s(%s) on guild %s(%s)" % (author.name, author.id, channel.name, channel.id, guild.name, guild.id), self.bot)
        if guild.created_at == None:
            await self.bot.send("Guild has no creation date! WAIT WHAT!")
        else:
            await self.bot.send("%s was created on: %s" % (guild.name, guild.created_at))

def setup(bot):
    bot.add_cog(Utilities(bot))
