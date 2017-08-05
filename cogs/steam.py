from discord.ext import commands
from .utils import checks, steammanager
import discord
import inspect
import urllib

# to expose to the eval command
import datetime
from collections import Counter

class Steam:
    """Steam Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, aliases=['rtfd'], invoke_without_command=True)
    async def steam(self, ctx, *, obj : str = None):
        """Steam Functionality!"""

    @steam.command(pass_context=True)
    async def fetch(self, ctx, user: str, *args):
        """Fetches Users Data From SteamRep"""
        SteamY = steammanager.SteamY("LOL NO")
        data = SteamY.getBans(user)
        profile = SteamY.getProfile(user)
        color = 0xffffff
        thumbnail = ""
        if data['CommunityBanned'] or data['VACBanned']:
            color = 0xff0000
        elif data['NumberOfVACBans'] > 0 or data['NumberOfGameBans'] > 0:
            color = 0x980000
        elif data['EconomyBan']:
            color = 0xdb7e00
        else:
            color = 0x00ff31
        em = discord.Embed(title='%s Bans!'%(profile['personaname']), description='Description', colour=color)
        em.set_author(name=profile['personaname'],url=profile['profileurl'],icon_url=profile['avatar'])
        for key, value in data.items():
            em.add_field(name=key, value=value)


        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def stats(self, ctx, user: str, *args):
        """Outputs a embed with users steam stats"""
        print("start!")
        SteamY = steammanager.SteamY("LOL NO")
        data = SteamY.getBans(user)
        profile = SteamY.getProfile(user)
        color = 0xffffff
        thumbnail = ""
        if data['CommunityBanned'] or data['VACBanned']:
            color = 0xff0000
        elif data['NumberOfVACBans'] > 0 or data['NumberOfGameBans'] > 0:
            color = 0x980000
        elif data['EconomyBan']:
            color = 0xdb7e00
        else:
            color = 0x00ff31
        em = discord.Embed(title='%s Bans!'%(profile['personaname']), description='Description', colour=color)
        em.set_thumbnail(url=profile['profileurl'])
        em.set_author(name=profile['personaname'],url=profile['profileurl'],icon_url=profile['avatar'])
        for key, value in data.items():
            em.add_field(name=key, value=value)
        print("Adding Banned Friends")
        #em.add_field(name="Banned Friends!", value=len(SteamY.bannedFriends(user)))


        await self.bot.say(embed=em)

def setup(bot):
    bot.add_cog(Steam(bot))
