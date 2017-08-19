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

    @commands.command(pass_context=True, aliases=["bug"])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def bugreport(self, ctx, *, bug):
        """Send a bugreport to the owner of the bot!"""
        msgs = [ctx.message]

        if bug == None or bug == "":
            await self.bot.send_message(ctx.message.author, "HOW TO MAKE A BUG REPORT")

        if self.bot.owner is None:
            msgs.append(await self.bot.send_message(ctx.message.author, "Sorry, bug could not be sent"))
            return

        em = discord.Embed(title="Bug Report", description=bug, colour=0xff0000)
        em.set_author(name=ctx.message.author.name+ctx.message.author.discriminator, icon_url=ctx.message.author.avatar_url)
        await self.bot.send_message(self.bot.owner, embed=em)
        msgs.append(await self.bot.say("Bug has been reported!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def suggestion(self, ctx, *, suggestion):
        """Send a suggestion or feature request to the bot owner!"""
        msgs = [ctx.message]

        if suggestion == None or suggestion == "":
            await self.bot.send_message(ctx.message.author, "HOW TO MAKE A SUGGESTION")

        if self.bot.owner is None:
            msmgs.append(await self.bot.send_message(ctx.message.author, "Sorry, suggestion could not be sent"))
            return

        em = discord.Embed(title="Suggestion", description=suggestion, colour=0x00ff00)
        em.set_author(name=ctx.message.author.name+ctx.message.author.discriminator, icon_url=ctx.message.author.avatar_url)
        await self.bot.send_message(self.bot.owner, embed=em)
        msgs.append(await self.bot.say("Suggestion has been added!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

def setup(bot):
    bot.add_cog(Support(bot))
