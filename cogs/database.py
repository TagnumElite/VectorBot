from discord.ext import commands
from .utils import config, checks
from .utils.databases import DBC, MessageDB, ServerDB, MembersDB, ConfigDB
import warnings, functools
import discord
import inspect
import urllib
import datetime
import asyncio

# I thought I would have to disable many things because of the
# Audit Logs but nope, still have to do everything.

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
    bot: discord.Client
        The bot

    Attributes
    ---------
    MessageDB: MessageDB
    ServerDB: ServerDB
    MembersDB: MembersDB"""

    def __init__(self, bot):
        self.bot = bot
        self.MessageDB = MessageDB(bot.DBC, bot.currentDB)
        self.ServerDB = ServerDB(bot.DBC, bot.currentDB)
        self.MembersDB = MembersDB(bot.DBC, bot.currentDB)
        self.ConfigDB = ConfigDB(bot.DBC, bot.currentDB)

    @commands.group(pass_context=True)
    async def database(self, ctx):
        """Database commands! NONE FUNCTIONAL"""
        #await self.bot.say("I IS NOT READY!")
        print("Yes")

    @database.command(pass_context=True)
    async def fetch(self, ctx, user: discord.Member, date: str=None):
        """Fetches all the messages a user has sent or something

        .. warning::
            NOT SETUP"""
        if date is None:
            message = self.MembersDB.fetch(user)[1]
            await self.bot.say(message)

    @database.command(pass_context=True)
    async def check(self, ctx, key, value):
        """Checks up on values

        .. warning::
            NOT SETUP"""

        pass

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

    async def on_message(self, message: discord.Message):
        """Called when a message is create. This adds the message
        if it is not an ignored ID to the database."""
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.create(message)

    async def on_message_delete(self, message: discord.Message):
        """Called when a message is deleted. This makes it so that the
        message JSON in the database leads to null as it's last update
        if it is not an ignored ID to the database."""
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.delete(message, datetime.datetime.utcnow())

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Called when a message is updates. This adds the message new
        content while still keeping the old content if it is not an
        ignored ID to the database."""
        if checks.is_an_ignored([before.author.id, before.server.id, before.channel.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.update(before, after)

    async def on_reaction_add(self, reaction: discord.Reaction, user):
        """Called when a message gets an reaction.

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction to be added
        user: discord.User
            The user that added the reaction"""
        if checks.is_an_ignored(user.id, self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.addReaction(reaction, user)

    async def on_reaction_remove(self, reaction: discord.Reaction, user):
        """Called when a reaction gets removed from a message.

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction to be added
        user: discord.User
            The user that added the reaction"""
        if checks.is_an_ignored(user.id, self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.deleteReaction(reaction, user)

    async def on_reaction_clear(self, message: discord.Message, reactions):
        """Called when the reactions on a message get cleared.

        Parameters
        ----------
        message: discord.Message
            The message that had the reactions cleared
        reactions: list[discord.Reaction]
            List of reactions cleared"""

        if checks.is_an_ignored_todo([message.author.id, message.server.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MessageDB.clearReactions(message)

    async def on_server_join(self, server: discord.Server):
        """Called when the bot joins a server.

        Parameters
        ----------
        server: discord.Server"""
        if checks.is_an_ignored(server.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.create(server)

    async def on_server_remove(self, server: discord.Server):
        """Called when the bot Leaves/Kicked From/Banned From a server.

        Parameters
        ----------
        server: discord.Server"""
        if checks.is_an_ignored(server.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.delete(server)

    async def on_server_update(self, before: discord.Server, after: discord.Server):
        """Called when server updates that the bot is in.

        Parameters
        ----------
        before: discord.Server
            Before Update
        after:  discord.Server
            After Update"""
        if checks.is_an_ignored(before.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.update(before, after)

    async def on_server_available(self, server: discord.Server):
        """Called when a server comes back online

        Parameters
        ----------
        server: discord.Server"""
        if checks.is_an_ignored(server.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.updateStatus(server, 1)

    async def on_server_unavailable(self, server: discord.Server):
        """Called when a server goes offline

        Parameters
        ----------
        server: discord.Server"""
        if checks.is_an_ignored(server.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.updateStatus(server, 0)

    async def on_server_emojis_update_todo(self, before, after):
        """Called when an emojis is updated/create/deleted

        Parameters
        ----------
        before: list[discord.Emojis]
            A list of the emojis before the update
        after: list[discord.Emojis]
            A list of emojis after the update"""
        if checks.is_an_ignored([before.id, before.server.id], self.bot.Config["Ignored IDs"]):
            return
        beforeS = sorted(before, key=lambda x: x.id)
        afterS = sorted(after, key=lambda x: x.id)
        if len(before) < len(after):
            for idx, emoji in enumerate(beforeS):
                #if
                NOTE = "I have to check between the two lists what's new"
            return self.ServerDB.createEmoji(None)
        elif len(before) > len(after):
            return self.ServerDB.deleteEmoji(None)
        elif len(before) is len(after):
            return self.ServerDB.updateEmoji(before, after)
        else:
            return "That doesn't make sense."
        return

    async def on_server_role_create(self, role: discord.Role):
        """Called when a role is created

        Parameters
        ----------
        role: discord.Role
            The New Role"""
        if checks.is_an_ignored(role.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.createRole(role)

    async def on_server_role_delete(self, role: discord.Role):
        """Called when a role is deleted

        Parameters
        ----------
        before: discord.Role
            The Delted Role"""
        if checks.is_an_ignored(role.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.deleteRole(role)

    async def on_server_role_update(self, before: discord.Role, after: discord.Role):
        """Called when a role is updated

        Parameters
        ----------
        before: discord.Role
            Old Role
        after: discord.Role
            New Role"""
        if checks.is_an_ignored(before.id, self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.updateRole(after)

    async def on_channel_delete(self, channel: discord.Channel):
        """Called when a channel is deleted

        Parameters
        ----------
        channel: discord.Channel
            The Delted Channel"""
        if checks.is_an_ignored([channel.id, channel.server.id], self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.deleteChannel(channel)

    async def on_channel_create(self, channel: discord.Channel):
        """Called when a channel is created!

        Parameters
        ----------
        channel: discord.Channel
            The new Channel"""
        if checks.is_an_ignored([channel.id, channel.server.id], self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.createChannel(self, channel)

    async def on_channel_update(Self, before: discord.Channel, after: discord.Channel):
        """Called when a channel is updated

        Parameters
        ----------
        before: discord.Channel
            The Old Channel
        after: discord.Channel
            The New Channel"""
        if checks.is_an_ignored([channel.id, channel.server.id], self.bot.Config["Ignored IDs"]):
            return
        return self.ServerDB.updateChannel(after)

    async def on_member_bant(self, member: discord.Member):
        """Called when a member is banned

        Parameters
        ----------
        member: discord.Member
            The banned Member"""
        if checks.is_an_ignored([member.id, member.server.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MembersDB.ban(member)

    async def on_member_unbant(self, server: discord.Server, user: discord.User):
        """Called when a user is unbanned

        Parameters
        ----------
        server: discord.Server
            The server from which the user was unbanned from
        user: discord.User
            The User"""
        if checks.is_an_ignored([server.id, user.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MembersDB.unban(server, user)

    async def on_member_joint(self, member: discord.Member):
        """Called when a member joins a server the bot is in.

        Parameters
        ----------
        memer: discord.Member
            The Server Member that was added"""
        if checks.is_an_ignored([member.id, member.server.id], self.bot.Config["Ignored IDs"]):
            return
        self.ServerDB.createMember(member)
        return self.MembersDB.create(member)

    async def on_member_removet(self, member: discord.Member):
        """Called when a member (leaves/kicked from/banned from) a server
        the bot is in.

        Parameters
        ----------
        memer: discord.Member
            The Server Member that was removed"""
        if checks.is_an_ignored([member.id, member.server.id], self.bot.Config["Ignored IDs"]):
            return
        self.ServerDB.deleteMember(member)
        return self.MembersDB.delete(member)

    async def on_member_updatet(self, before: discord.Member, after: discord.Member):
        """Called when a member calls an update the server the bot is in.

        Parameters
        ----------
        before: discord.Member
            The Old Member
        after: discord.Member
            The New Member"""
        if checks.is_an_ignored([before.id, before.server.id], self.bot.Config["Ignored IDs"]):
            return
        return self.MembersDB.update(before, after)

    #async def on_voice_state_update_todo(self, before, after):

    # Remind why me why we need to log this? THATS RIGHT WE DONT!
    #async def on_typing(self, channel, user, when):

    # Or This? Nope, not an conference bot
    #async def on_group_join(self, channel, user):

    # If you really need then maybe, but this isn't a conference bot!
    #async def on_group_remove(self, channel, user):

def setup(bot):
    bot.add_cog(Database(bot))
