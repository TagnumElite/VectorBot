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
    }
}

class Twitch:
    """Handles the bot's twitch system."""

    def __init__(self, bot):
        self.bot = bot
        self.Config = bot.Config.get(self.__class__.__name__, default)
        self.Parser = Parser()
        self.checked_streams = []
        self.bot.loop.create_task(self.check_for_streams())

    async def on_member_update(self, before, after):
        """Check for when members stream"""

        print("Member:", before.name)

        if check_ignore([before.id, before.server.id], self.bot.Config["Ignored IDs"]):
            print("Stream: Ignored Object")
            return True
        if before.server.id == self.bot.mainServer:
            if before.game != after.game:
                if before.game.type is 1 and after.game.type is not 1:
                    print("Finished Streaming")
                    return
                if after.game.type is 1 and before.game.type is 0:
                    print("Started Streaming")
                    return await self.check_stream(after.game.url)
                print("Stream Unknown")
            else:
                print("Same Game")
        else:
            print("Not Main Server")
        return

    async def check_streams(self):
        for server in self.bot.servers:
            config = self.bot.Config.get(server.id)
        print("Checking for streams")
        url = "https://api.twitch.tv/kraken/streams/?channel={}"
        headers = {'Client-ID': self.Config["Client ID"]}
        users = self.Config["Users"]
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
                        embed_data = self.Config["Embed"]
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
            await asyncio.sleep(self.Config["Refresh"])

    async def check_stream(self, url):
        """Check if url is twitch stream and has been checked"""

        print("Stream URL:", url)

        if url.startswith("https://www.twitch.tv"):
            username = url.replace("https://www.twitch.tv/", "")

            print("Checking the stream")
            url = "https://api.twitch.tv/kraken/streams/?channel={}"
            headers = {'Client-ID': self.Config["Client ID"]}

            print("Getting streams")
            response = requests.get(url.format(username), headers=headers)
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
                        if stream["channel"]["name"] == username:
                            print("Found stream")
                            embed_data = self.Config["Embed"]
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
        else:
            print("Non Twitch Stream")

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

def setup(bot):
    bot.add_cog(Twitch(bot))
