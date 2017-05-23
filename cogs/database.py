from discord.ext import commands
from .utils import config, checks
from .utils.databases import DBC, MessageDB, ServerDB, MembersDB
import warnings, functools
import discord
import inspect
import urllib
import datetime
import asyncio

import datetime
from collections import Counter

#NOTE: Most will be disabled because of discord audit logs.

# Discord Audit Logs:
# Server Update
# Channel Create/Delete/Update
# Channel Perms Create/Delete/Update
# Member Kick/Prune/Ban/Unban/Update/Update Roles
# Role Create/Update/Remove
# Invite Create/Update/Remove
# Webhook Create/Update/Remove
# Emoji Create/Update/Remove
# Messages Remove

class Database:
    """Database Functionallity

    Parameters
    ----------
    bot: discord.ext.commands.Bot
        The bot

    Variables
    ---------
    MessageDB: MessageDB
    ServerDB: ServerDB
    MembersDB: MembersDB"""

    def __init__(self, bot):
        self.bot = bot
        self.MessageDB = MessageDB(bot.DBC, bot.currentDB)
        self.ServerDB = ServerDB(bot.DBC, bot.currentDB)
        self.MembersDB = MembersDB(bot.DBC, bot.currentDB)

    @commands.group(pass_context=True, aliases=['db'])
    @checks.admin_or_permissions(administrator=True)
    async def database(self, ctx):
        """Database commands!"""
        #await self.bot.say("I IS NOT READY!")
        print("Yes")

    @database.command(pass_content=True)
    async def fetch(self, user: discord.Member, date: datetime=None):
        """Fetches all the messages a user has sent or something

        .. warning::
            NOT SETUP"""
        if date is None:
            message = self.MembersDB.fetch(user)[1]
            await self.bot.say(message)

    # @database.command(pass_content=True)
    async def sexists(self, ctx, *, args):
        """Checks if server exists in the DB and not it is not!

        .. warning::
            NOT SETUP"""
        message = ctx.message
        author = message.author
        server = message.server
        channel = message.channel
        DB = self.ServerDB
        msg = [message]
        if DB.exists(server):
            msg.append(await self.bot.say("Server Does Exist!"))
        else:
            msg.append(await self.bot.say("No Server Doesn't Exist! Would you like to add it?"))
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

    async def on_ready_todo(self):
        """Called when the bot is ready

        .. note::
            TODO"""
        pass

    async def on_resumed_todo(self):
        """Called when the bot resumes

        .. note::
            TODO"""
        pass

    async def on_error_todo(self, error):
        """Called when the bot encounters an error.

        .. note::
            TODO"""
        pass

    async def on_socket_raw_recieve_todo(self, msg):
        """Called when the bot recieves data. RAW

        .. note::
            TODO"""
        pass

    async def on_socket_raw_send_todo(self, payload):
        """Called when the bot sends data. RAW

        .. note::
            TODO"""
        pass

    async def on_message(self, message):
        """Called when a message is create. This adds the message
        if it is not an ignored ID to the database."""
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.create(message)

    async def on_message_delete(self, message):
        """Called when a message is deleted. This makes it so that the
        message JSON in the database leads to null as it's last update
        if it is not an ignored ID to the database."""
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.delete(message, datetime.datetime.utcnow())

    async def on_message_edit(self, before, after):
        """Called when a message is updates. This adds the message new
        content while still keeping the old content if it is not an
        ignored ID to the database."""
        if checks.is_an_ignored([before.author.id, before.server.id, before.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.update(before, after)

    async def on_reaction_add_todo(self, reaction, user):
        """Called when a message gets an reaction.

        .. note::
            TODO"""
        self.MessageDB.addReaction(reaction, user)

    async def on_reaction_remove_todo(self, reaction, user):
        """Called when a reaction gets removed from a message.

        .. note::
            TODO"""
        self.MessageDB.deleteReaction(reaction, user)

    async def on_reaction_clear(self, message, reactions):
        """Called when the reactions on a message get cleared.

        .. note::
            TODO"""
        if checks.is_an_ignored_todo([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.clearReaction(reaction, user)

    async def on_server_join_todo(self, server: discord.Server):
        """Called when the bot joins a server.

        .. note::
            TODO"""
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.create(server)

    async def on_server_remove_todo(self, server: discord.Server):
        """Called when the bot Leaves/Kicked From/Banned From a server.

        .. note::
            TODO"""
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.delete(server)

    async def on_server_update_todo(self, before: discord.Server, after: discord.Server):
        """Called when server updates that the bot is in.

        .. note::
            TODO"""
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.update(before, after)

    async def on_server_available_todo(self, server: discord.Server):
        """Called when a server comes back online

        .. note::
            TODO"""
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.updateStatus(server, "Online")

    async def on_server_unavailable_todo(self, server):
        """Called when a server goes offline

        .. note::
            TODO"""
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.updateStatus(server, "Offline")

    # Disabled Logging Because Of Audit Logs:
    #async def on_member_ban(self, member):
    #async def on_member_unban(self, server, user):

    async def on_member_join_todo(self, member: discord.Member):
        """Called when a member joins a server the bot is in.

        .. note::
            TODO"""
        if checks.is_an_ignored(member.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.create(member)

    async def on_member_remove_todo(self, member: discord.Member):
        """Called when a member (leaves/kicked from/banned from) a server
        the bot is in.

        .. note::
            TODO"""
        if checks.is_an_ignored(member.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.delete(member)

    async def on_member_update_todo(self, before: discord.Member, after: discord.Member):
        """Called when a member calls an update the server the bot is in.

        .. note::
            TODO"""
        if checks.is_an_ignored(before.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.update(before, after)

    async def on_voice_state_update_todo(self, before, after):
        """Called when a voicestate is updated

        .. note::
            TODO"""
        if checks.is_an_ignored(before.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.updateVoiceState(before, after)

    # Disabled Logging Because Of Audit Logs:
    #async def on_server_emojis_update(self, before, after):
    #async def on_server_role_create(self, role):
    #async def on_server_role_delete(self, role):
    #async def on_server_role_update(self, before, after):
    #async def on_channel_delete(self, channel):
    #async def on_channel_create(self, channel):

    # Remind why me why we need to log this? THATS RIGHT WE DONT!
    #async def on_typing(self, channel, user, when):

    # Or This? Nope, not an conference bot
    #async def on_group_join(self, channel, user):

    # If you really need then maybe, but this isn't a conference bot!
    #async def on_group_remove(self, channel, user):

def setup(bot):
    bot.add_cog(Database(bot))
# Unless you want me to make a conference bot? But why though. WHY?
