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
        self.config = bot.config.get(self.__class__.__name__, {})

    @commands.command(hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def load(self, ctx, *, module : str):
        """Loads a module."""
        channel = ctx.channel
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await channel.send('\N{PISTOL}')
            await channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await channel.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def unload(self, ctx, *, module : str):
        """Unloads a module."""
        channel = ctx.channel
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await channel.send('\N{PISTOL}')
            await channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await channel.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def _reload(self, ctx, *, module : str):
        """Reloads a module."""
        channel = ctx.channel
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await channel.send('\N{PISTOL}')
            await channel.send('{}: {}'.format(type(e).__name__, e))
        else:
            await channel.send('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, hidden=True)
    @checks.admin_or_permissions(administrator=True)
    async def debug(self, ctx, *, code : str):
        channel = ctx.channel
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await channel.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await channel.send(python.format(result))

def setup(bot):
    bot.add_cog(Admin(bot))
