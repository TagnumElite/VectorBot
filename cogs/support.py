from discord.ext import commands
from .utils import checks
import discord, asyncio
import inspect
import urllib

class Support:
    """Support Commands, used for reporting bugs and giving suggestions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=["bug"])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def bugreport(self, ctx, *, bug):
        msgs = []
        members = self.bot.get_all_members()
        owner = None
        for member in members:
            if member.id is self.bot.Configs["Owner"]:
                owner = member
                break

        if owner is None:
            await self.bot.send_message(ctx.message.author, "Sorry, bug could not be sent")
            return

        em = discord.Embed(title="Bug Report", description=bug, colour=0xff0000)
        em.set_author(name=ctx.message.author.name+ctx.message.author.discriminator, icon_url=ctx.message.author.avatar_url)
        await self.bot.send_message(owner, embed=em)
        msgs.append(await self.bot.say("Bug has been reported!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def suggestion(self, ctx, *, suggestion):
        msgs = []
        members = self.bot.get_all_members()
        owner = None
        for member in members:
            if member.id is self.bot.Configs["Owner"]:
                owner = member
                break

        if owner is None:
            await self.bot.send_message(ctx.message.author, "Sorry, suggestion could not be sent")
            return

        em = discord.Embed(title="Suggestion", description=suggestion, colour=0x00ff00)
        em.set_author(name=ctx.message.author.name+ctx.message.author.discriminator, icon_url=ctx.message.author.avatar_url)
        await self.bot.send_message(owner, embed=em)
        msgs.append(await self.bot.say("Suggestion has been added!"))
        await asyncio.sleep(5)
        await self.bot.delete_messages(msgs)
        return

def setup(bot):
    bot.add_cog(Support(bot))
