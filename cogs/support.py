from discord.ext import commands
from .utils import checks
import discord, asyncio
import inspect
import urllib

class Support:
    """Support Commands, used for reporting bugs and giving suggestions"""

    def __init__(self, bot):
        self.bot = bot
        self.Config = bot.Config.get(self.__class__.__name__, {})

    @commands.command(aliases=["bug"])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def bugreport(self, ctx, *, bug):
        """Send a bugreport to the owner of the bot!"""
        msgs = [ctx.message]
        author = ctx.author
        channel = ctx.channel

        if bug == None or bug == "":
            await author.send("HOW TO MAKE A BUG REPORT")

        if self.bot.owner is None:
            msgs.append(await author.send("Sorry, bug could not be sent"))
            return

        em = discord.Embed(title="Bug Report", description=bug, colour=0xff0000)
        em.set_author(name=author.name+author.discriminator, icon_url=author.avatar_url)
        await self.bot.owner.send(embed=em)
        msgs.append(await channel.send("Bug has been reported!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

    @commands.command()
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def suggestion(self, ctx, *, suggestion):
        """Send a suggestion or feature request to the bot owner!"""
        msgs = [ctx.message]
        channel = ctx.channel
        author = ctx.author

        if suggestion == None or suggestion == "":
            await author.send("HOW TO MAKE A SUGGESTION")

        if self.bot.owner is None:
            msmgs.append(await author.send("Sorry, suggestion could not be sent"))
            return

        em = discord.Embed(title="Suggestion", description=suggestion, colour=0x00ff00)
        em.set_author(name=ctx.message.author.name+ctx.message.author.discriminator, icon_url=ctx.message.author.avatar_url)
        await self.bot.owner.send(embed=em)
        msgs.append(await channel.send("Suggestion has been added!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

    @commands.command()
    async def version(self, ctx):
        """Returns the bot's version and discord.py version"""
        channel = ctx.channel

        await channel.send("Bot: V({0}) / discord.py: V({1})".format(self.bot.Version, discord.__version__))
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Support(bot))
