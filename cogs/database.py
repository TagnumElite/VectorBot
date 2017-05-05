from discord.ext import commands
from .utils import config, checks
from .utils.databases import Databases, MessageDB, ServerDB, MembersDB, ChannelsDB, RolesDB, EmojisDB
import discord
import inspect
import urllib
import datetime
import asyncio

# to expose to the eval command
import datetime
from collections import Counter

class Database:
    """Database Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, aliases=['db'])
    @checks.admin_or_permissions(administrator=True)
    async def database(self, ctx):
        """Database commands!"""
        #await self.bot.say("I IS NOT READY!")
        print("Yes")

    @database.command(pass_content=True)
    async def fetch(self, user: discord.Member, date: datetime=None):
        DB = MessageDB(self.bot.currentDB)
        if date is None:
            message = DB.fetch(user)[1]
            await self.bot.say(message)

    @database.command(pass_content=True)
    async def sexists(self, ctx, *, args):
        """Checks if server exists in the DB"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        DB = databases.ServerDB(self.bot.currentDB)
        msg = [message]
        if DB.exists(server):
            msg.append(await self.bot.say("Server Does Exist!"))
        else:
            msg.append(await self.bot.say("No Server Doesn't Exist! Would you like to add it?")
            response = await self.bot.wait_for_message(author=author, channel=channel, timeout=60.0)
            if response is None:
                msg.append(await self.bot.say('You took too long. Goodbye.'))
                return
            elif response.lower() in ["yes", "y"]:
                msg.append(await bot.say("Adding server"))
                if DB.create(server):
                    msg.append(await self.bot.edit_message(msg, "Added Server"))
                else:
                    msg.append(await self.bot.edit_message(msg, "Failed to Create Server"))
        await self.bot.delete_messages(msg)


    #async def on_ready(self):
        #databases.log_ready(self.bot)

    #async def on_resumed(self):
        #databases.log_resumed(self.bot)

    #async def on_error(self, error):
        #databases.log_error(self.bot, error)

    #async def on_socket_raw_recieve(self, msg):
        #databases.log_raw_recieve(self.bot, msg)

    #async def on_socket_raw_send(self, payload):
        #databases.log_raw_senf(self.bot, payload)

    async def on_message(self, message):
        DB = MessageDB(self.bot.currentDB)
        DB.create(message)

    async def on_message_delete(self, message):
        DB = MessageDB(self.bot.currentDB)
        DB.delete(message, datetime.datetime.utcnow())

    async def on_message_edit(self, before, after):
        DB = MessageDB(self.bot.currentDB)
        DB.update(before, after)

    #async def on_reaction_add(self, reaction, user):
        #DB = MessageDB(self.bot.currentDB)
        #DB.addReaction(reaction, user)

    #async def on_reaction_remove(self, reaction, user):
        #DB = MessageDB(self.bot.currentDB)
        #DB.deleteReaction(reaction, user)

    #async def on_reaction_clear(self, message, reactions):
        #DB = MessageDB(self.bot.currentDB)
        #DB.clearReaction(reaction, user)

    async def on_server_join(self, server):
        DB = ServerDB(self.bot.currentDB)
        DB.create(server)

    async def on_server_remove(self, server):
        DB = ServerDB(self.bot.currentDB)
        DB.delete(server)

    async def on_server_update(self, before, after):
        DB = ServerDB(self.bot.currentDB)
        DB.update(before, after)

    async def on_server_available(self, server):
        DB = ServerDB(self.bot.currentDB)
        DB.updateStatus(server, "Online")

    async def on_server_unavailable(self, server):
        DB = ServerDB(self.bot.currentDB)
        DB.updateStatus(server, "Offline")

    async def on_member_ban(self, member):
        DB = MembersDB(self.bot.currentDB, member.server)
        DB.ban(member)

    async def on_member_unban(self, server, user):
        DB = MembersDB(self.bot.currentDB, server)
        DB.unban(user)

    async def on_member_join(self, member):
        DB = MembersDB(self.bot.currentDB, after.server)
        DB.create(before, after)

    async def on_member_remove(self, member):
        DB = MembersDB(self.bot.currentDB, after.server)
        DB.delete(before, after)

    async def on_member_update(self, before, after):
        DB = MembersDB(self.bot.currentDB, after.server)
        DB.update(before, after)

    async def on_voice_state_update(self, before, after):
        DB = MembersDB(self.bot.currentDB, after.server)
        DB.updateVoiceState(before, after)

    async def on_server_emojis_update(self, before, after):
        DB = EmojisDB(self.bot.currentDB, after.server)
        DB.update(before, after)

    async def on_server_role_create(self, role):
        DB = RolesDB(self.bot.currentDB, after.server)
        DB.create(before, after)

    async def on_server_role_delete(self, role):
        DB = RolesDB(self.bot.currentDB, after.server)
        DB.delete(before, after)

    async def on_server_role_update(self, before, after):
        DB = RolesDB(self.bot.currentDB, after.server)
        DB.update(before, after)

    async def on_channel_delete(self, channel):
        DB = ChannelsDB(self.bot.currentDB, after.server)
        DB.delete(before, after)

    async def on_channel_create(self, channel):
        DB = ChannelsDB(self.bot.currentDB, after.server)
        DB.create(before, after)

    async def on_channel_update(self, before, after):
        DB = ChannelsDB(self.bot.currentDB, after.server)
        DB.update(before, after)

    #async def on_typing(self, channel, user, when):
        #databases.log_typing(self.bot, channel, user, when)

    #async def on_group_join(self, channel, user):
        #databases.log_group_join(self.bot, channel, user)

    #async def on_group_remove(self, channel, user):
        #databases.log_group_remove(self.bot, channel, user)

def setup(bot):
    bot.add_cog(Database(bot))
