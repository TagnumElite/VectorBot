from discord.ext import commands
from .utils.checks import check_ignore
from .utils.parser import Parser
import discord
import asyncio
import requests
import json
import re

default = {
    "Client ID": "uo6dggojyb8d6soh92zknwmi5ej1q2",
    "Refresh": 30,
    "Users": [],
    "Main": "",
    "Embed": {
        "Title": "{name} is live!",
        "Description": "",
        "Colour": "",
        "Footer": {
            "Enabled": False,
            "Text": "",
            "Icon Url": ""
        },
        "Url": "",
        "Thumbnail": "",
        "Image": "{preview[large]}",
        "Author": {
            "Enabled": False,
            "Name": "",
            "Avatar Url": ""
        },
        "Inline": [
            {"Name": "Viewers", "Value": "{viewers}", "Inline": True},
            {"Name": "Created At", "Value": "{created_at}", "Inline": True}
        ]
    }}

class Twitch:
    """Handles the bot's twitch system."""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get(self.__class__.__name__, default)
        self.Parser = Parser()
        self.checked_streams = []
        self.bot.loop.create_task(self.check_for_streams())

    async def on_member_update(self, before, after):
        """Check for when members stream"""

        if check_ignore([before.id, before.guild.id], self.bot.Config["Ignored IDs"]):
            return True
        try:
            if before.guild.id == self.bot.main_guild:
                if before.game != after.game:
                    if before.game.type is 1 or after.game.type is not 1:
                        return
                    if before.game.type is 0 and after.game.type is 1:
                        return await self.check_streams(after.game.url)
        except Exception as E:
            return

    async def check_streams(self, url=None):
        channel = ""
        if url is None:
            if len(self.Config["Users"]) <= 0:
                return
            else:
                channel = ", ".join(users)
        else:
            if url.startswith("https://www.twitch.tv"):
                channel = url.replace("https://www.twitch.tv/", "")
            else:
                return

        for guild in self.bot.guilds:
            config = self.bot.Config.get(guild.id)
        url = "https://api.twitch.tv/kraken/streams/?channel={}"
        headers = {'Client-ID': self.Config["Client ID"]}
        users = self.Config["Users"]

        response = requests.get(url.format(channel), headers=headers)
        data = self.Parser.jsonLoads(response.content)
        if data["_total"] is not 0:
            for stream in data["streams"]:
                if stream["_id"] in self.checked_streams:
                    continue
                else:
                    if stream["channel"]["name"] in users:
                        embed_data = self.Config["Embed"]
                        embed_data["Colour"] = 0x6441A4
                        em = self.Parser.createEmbed(
                            data=embed_data,
                            extra=stream
                        )
                        self.checked_streams.append(stream["_id"])
                        announcement = discord.Object(
                            id=self.bot.currentAnnounce
                        )
                        await announcement.send(embed=em)

    async def check_for_streams(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            await self.check_streams()
            await asyncio.sleep(self.Config["Refresh"])

    @commands.group()
    async def twitch(self, ctx):
        """Twitch commands"""

        pass

    @twitch.command()
    async def add(self, ctx, user):
        """Add a user to the announcement list"""

        pass

    @twitch.command()
    async def remove(self, ctx, user):
        """Remove a user to the announcement list"""

        pass

    @twitch.command()
    async def list(self, ctx):
        """List current users"""

        pass

    @twitch.command()
    @commands.cooldown(rate=1, per=60.0)
    async def check(self, ctx, streamer: str=None):
        """Check if someone is livestreaming, if you put in
        a streamers name you will get an DM if that streamer
        is online"""

        await self.check_streams()

def setup(bot):
    bot.add_cog(Twitch(bot))
