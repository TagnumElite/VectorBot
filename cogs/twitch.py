from discord.ext import commands
from .utils.checks import check_ignore
from .utils.parser import Parser
import discord
import asyncio
import requests
import json
import re

class Twitch:
    """Handles the bot's twitch system."""

    def __init__(self, bot):
        self.bot = bot
        self.Parser = Parser()
        self.checked_streams = []
        self.bot.loop.create_task(self.check_for_streams())

    async def check_streams(self):
        for server in self.bot.servers:
            config = self.bot.Config.get(server.id)
        print("Checking for streams")
        url = "https://api.twitch.tv/kraken/streams/?channel={}"
        headers = {'Client-ID': self.bot.Configs["Twitch Client ID"]}
        users = self.bot.Configs["Twitch Users"]
        channels = ", ".join(users)

        print("Getting streams")
        response = requests.get(url.format(channels), headers=headers)
        print("Response: ", response)
        data = self.Parser.jsonLoads(response.content)
        print("Data: ", data)
        if data["_total"] is not 0:
            print("Streams: ", data["_total"])
            for stream in data["streams"]:
                print("Stream ID: ", stream["_id"])
                if stream["_id"] in self.checked_streams:
                    print("Stream has been checked")
                else:
                    print("Stream has not been checked")
                    if stream["channel"]["name"] in users:
                        print("Found stream")
                        embed_data = self.bot.Configs["Twitch Embed"]
                        embed_data["Colour"] = 0x6441A4
                        print("Getting Embed")
                        em = self.Parser.createEmbed(
                            data=embed_data,
                            extra=stream
                        )
                        print("Embed: ", em.to_dict())
                        print("Appedning Stream")
                        self.checked_streams.append(stream["_id"])
                        print("Getting announcement")
                        announcement = discord.Object(
                            id=self.bot.currentAnnounce
                        )
                        print("Sending Embed")
                        await self.bot.send_message(
                            announcement,
                            embed=em
                        )
                        print("Sent Embed")
                    else:
                        print("User is not ours")
        else:
            print("Streams: None")

    async def check_for_streams(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            await self.check_streams()
            await asyncio.sleep(self.bot.Configs["Twitch Refresh"])

    async def check_stream(self, url):
        """Check if url is twitch stream and has been checked"""

        if url.startswith("")

    @commands.group(pass_context=True)
    async def twitch(self, ctx):
        """Twitch commands"""

        pass

    @twitch.command(pass_context=True)
    async def add(self, ctx, user):
        """Add a user to the announcement list"""

        pass

    @twitch.command(pass_context=True)
    async def remove(self, ctx, user):
        """Remove a user to the announcement list"""

        pass

    @twitch.command(pass_context=True)
    async def list(self, ctx):
        """List current users"""

        pass

    @twitch.command(pass_context=True)
    @commands.cooldown(rate=1, per=60.0)
    async def check(self, ctx, streamer: str=None):
        """Check if someone is livestreaming, if you put in
        a streamers name you will get an DM if that streamer
        is online"""

        await self.check_streams()

    async def on_member_update(self, before, after):
        """Check for when members stream"""

        if check_ignore([before.id, before.server.id], self.bot.Config["Ignored IDs"]):
            return True
        if member.server.id is self.bot.mainServer:
            if before.game is not after.game:
                if before.game.type is 1:
                    return
                if after.game.type is 1 and before.game.type is 0:
                    await self.check_stream(after.game.url)
        return

def setup(bot):
    bot.add_cog(Twitch(bot))
