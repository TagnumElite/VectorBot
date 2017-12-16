from discord.ext import commands
from .utils import config, checks
import warnings, functools
import discord
import inspect
import urllib
import datetime
import asyncio

# I thought I would have to disable many things because of the
# Audit Logs but nope, still have to do everything.

# Discord Audit Logs:
# Guild Update
# GuildChannel Create/Delete/Update
# GuildChannel Perms Create/Delete/Update
# Member Kick/Prune/Ban/Unban/Update/Update Roles
# Role Create/Update/Remove
# Invite Create/Update/Remove
# Webhook Create/Update/Remove
# Emoji Create/Update/Remove
# Messages Remove

def check_database(Database):
    if Database == None:
        return False

class Database:
    """Database Functionallity

    .. warning::
        EVERYTHING IS BROKEN!!!

    Parameters
    ----------
    bot: discord.Client
        The bot

    Attributes
    ---------
    MDB: MessageDB
    GDB: GuildDB
    UDB: UserDB"""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get(
            self.__class__.__name__,
            {"Host": "localhost",
             "Port": 3306,
             "Name": "vectorbot",
             "User": "Vector",
             "Pass": "",
             "Type": "MySQL",
             "Prefix": "vb"}
        )

    @commands.group()
    async def database(self, ctx):
        """Database commands! NONE FUNCTIONAL"""
        pass

    @database.command()
    async def fetch(self, ctx, user: discord.Member, date: str=None):
        """Fetches all the messages a user has sent or something

        .. warning::
            NOT SETUP"""
        if date is None:
            message = self.UDB.fetch(user)[1]
            await ctx.send(message)
        return

    @database.command()
    async def check(self, ctx, key, value):
        """Checks up on values

        .. warning::
            NOT SETUP"""
        pass

    async def on_ready(self):
        """Setup the databases on bot ready!"""
        print("Database: On Ready")
        try:
            from .utils.databases import MessageDB
        except:
            print("Message Database Offline")
            self.MDB = None
        else:
            self.MDB = MessageDB(self.bot.DBC, self.Config["Prefix"])
        try:
            from .utils.databases import GuildDB
        except:
            print("Guild Database Offline")
            self.GDB = None
        else:
            self.GDB = GuildDB(self.bot.DBC, self.Config["Prefix"])
        try:
            from .utils.databases import UserDB
        except:
            print("Member Database Offline")
            self.UDB = None
        else:
            self.UDB = UserDB(self.bot.DBC, self.Config["Prefix"])
        try:
            from .utils.databases import ConfigDB
        except:
            print("Config Database Offline")
            self.CDB = None
        else:
            self.CDB = ConfigDB(self.bot.DBC, self.Config["Prefix"])

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
        await self.bot.wait_until_ready()
        if checks.check_ignore([message.author.id, message.guild.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        try:
            result = self.MDB.create(message)
        except:
            return False
        else:
            return result

    async def on_message_delete(self, message: discord.Message):
        """Called when a message is deleted. This makes it so that the
        message JSON in the database leads to null as it's last update
        if it is not an ignored ID to the database."""
        await self.bot.wait_until_ready()
        if checks.check_ignore([message.author.id, message.guild.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        return self.MDB.delete(message, datetime.datetime.utcnow())

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Called when a message is updates. This adds the message new
        content while still keeping the old content if it is not an
        ignored ID to the database."""
        await self.bot.wait_until_ready()
        if checks.check_ignore([before.author.id, before.guild.id, before.channel.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        return self.MDB.update(before, after)

    async def on_reaction_add(self, reaction: discord.Reaction, user):
        """Called when a message gets an reaction.

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction to be added
        user: discord.User
            The user that added the reaction"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(user.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        return self.MDB.addReaction(reaction, user)

    async def on_reaction_remove(self, reaction: discord.Reaction, user):
        """Called when a reaction gets removed from a message.

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction to be added
        user: discord.User
            The user that added the reaction"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(user.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        return self.MDB.deleteReaction(reaction, user)

    async def on_reaction_clear(self, message: discord.Message, reactions):
        """Called when the reactions on a message get cleared.

        Parameters
        ----------
        message: discord.Message
            The message that had the reactions cleared
        reactions: list[discord.Reaction]
            List of reactions cleared"""

        await self.bot.wait_until_ready()
        if checks.check_ignore_todo([message.author.id, message.guild.id, message.channel.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.MDB):
            return False
        return self.MDB.clearReactions(message)

    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a guild.

        Parameters
        ----------
        guild: discord.Guild"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(guild.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.create(guild)

    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot Leaves/Kicked From/Banned From a guild.

        Parameters
        ----------
        guild: discord.Guild"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(guild.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.delete(guild)

    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Called when guild updates that the bot is in.

        Parameters
        ----------
        before: discord.Guild
            Before Update
        after:  discord.Guild
            After Update"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(before.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.update(before, after)

    async def on_guild_available(self, guild: discord.Guild):
        """Called when a guild comes back online

        Parameters
        ----------
        guild: discord.Guild"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(guild.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.updateStatus(guild, 1)

    async def on_guild_unavailable(self, guild: discord.Guild):
        """Called when a guild goes offline

        Parameters
        ----------
        guild: discord.Guild"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(guild.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.updateStatus(guild, 0)

    async def on_guild_emojis_update(self, guild: discord.Guild, before, after):
        """Called when an emojis is updated/create/deleted

        Parameters
        ----------
        before: list[discord.Emojis]
            A list of the emojis before the update
        after: list[discord.Emojis]
            A list of emojis after the update"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([before.id, before.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        beforeS = sorted(before, key=lambda x: x.id)
        afterS = sorted(after, key=lambda x: x.id)
        if len(before) < len(after):
            for idx, emoji in enumerate(beforeS):
                #if
                NOTE = "I have to check between the two lists what's new"
            print("Create Emoji")
            #return self.GDB.create(None)
        elif len(before) > len(after):
            print("Delete Emoji")
            #return self.GDB.delete(None)
        elif len(before) is len(after):
            return self.GDB.update(before, after)
        else:
            return "That doesn't make sense."
        return

    async def on_guild_role_create(self, role: discord.Role):
        """Called when a role is created

        Parameters
        ----------
        role: discord.Role
            The New Role"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(role.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.createRole(role)

    async def on_guild_role_delete(self, role: discord.Role):
        """Called when a role is deleted

        Parameters
        ----------
        before: discord.Role
            The Delted Role"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(role.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.deleteRole(role)

    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Called when a role is updated

        Parameters
        ----------
        before: discord.Role
            Old Role
        after: discord.Role
            New Role"""
        await self.bot.wait_until_ready()
        if checks.check_ignore(before.id, self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.updateRole(after)

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Called when a channel is deleted

        Parameters
        ----------
        channel: discord.abc.GuildChannel
            The Delted GuildChannel"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([channel.id, channel.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.deleteGuildChannel(channel)

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Called when a channel is created!

        Parameters
        ----------
        channel: discord.abc.GuildChannel
            The new GuildChannel"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([channel.id, channel.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.createGuildChannel(self, channel)

    async def on_guild_channel_update(Self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        """Called when a channel is updated

        Parameters
        ----------
        before: discord.abc.GuildChannel
            The Old GuildChannel
        after: discord.abc.GuildChannel
            The New GuildChannel"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([channel.id, channel.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.GDB.updateGuildChannel(after)

    async def on_member_ban_todo(self, guild: discord.Guild, user: discord.User):
        """Called when a member is banned

        Parameters
        ----------
        member: discord.Member
            The banned Member"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([member.id, member.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.UDB.ban(member)

    async def on_member_unban_todo(self, guild: discord.Guild, user: discord.User):
        """Called when a user is unbanned

        Parameters
        ----------
        guild: discord.Guild
            The guild from which the user was unbanned from
        user: discord.User
            The User"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([guild.id, user.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        return self.UDB.unban(guild, user)

    async def on_member_join_todo(self, member: discord.Member):
        """Called when a member joins a guild the bot is in.

        Parameters
        ----------
        memer: discord.Member
            The Guild Member that was added"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([member.id, member.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        if not check_database(self.UDB):
            return False
        self.GDB.createMember(member)
        return self.UDB.create(member)

    async def on_member_remove_todo(self, member: discord.Member):
        """Called when a member (leaves/kicked from/banned from) a guild
        the bot is in.

        Parameters
        ----------
        memer: discord.Member
            The Guild Member that was removed"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([member.id, member.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.GDB):
            return False
        if not check_database(self.UDB):
            return False
        self.GDB.deleteMember(member)
        return self.UDB.delete(member)

    async def on_member_update_todo(self, before: discord.Member, after: discord.Member):
        """Called when a member calls an update the guild the bot is in.

        Parameters
        ----------
        before: discord.Member
            The Old Member
        after: discord.Member
            The New Member"""
        await self.bot.wait_until_ready()
        if checks.check_ignore([before.id, before.guild.id], self.bot.Config["Ignored IDs"]):
            return
        if not check_database(self.UDB):
            return False
        return self.UDB.update(before, after)

def setup(bot):
    bot.add_cog(Database(bot))
