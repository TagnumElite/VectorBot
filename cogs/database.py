from discord.ext import commands
from .utils import config, checks
from .utils.databases import DBC, MessageDB, ServerDB, MembersDB, ChannelsDB, RolesDB, EmojisDB
import warnings, functools
import discord
import inspect
import urllib
import datetime
import asyncio

import datetime
from collections import Counter

#NOTE: Most will be disabled because of discord audit logs but this does not mean the functions don't work. Uncomment the functions to make them work!
#NOTE: THESE THINGS WILL CHANGE BECAUSE I CHANGED THE WAY THE BOT WILL BE LOGGING INTO THE DB

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
    """Database Functionallity"""

    def __init__(self, bot):
        self.bot = bot
        self.MessageDB = MessageDB(bot.DBC, bot.currentDB)
        self.ServerDB = ServerDB(bot.DBC, bot.currentDB)
        self.MembersDB = MembersDB(bot.DBC, bot.currentDB)
        self.ChannelsDB = ChannelsDB(bot.DBC, bot.currentDB)
        self.RolesDB = RolesDB(bot.DBC, bot.currentDB)
        self.EmojisDB = EmojisDB(bot.DBC, bot.currentDB)

    @commands.group(pass_context=True, aliases=['db'])
    @checks.admin_or_permissions(administrator=True)
    async def database(self, ctx):
        """Database commands!"""
        #await self.bot.say("I IS NOT READY!")
        print("Yes")

    @database.command(pass_content=True)
    async def fetch(self, user: discord.Member, date: datetime=None):
        if date is None:
            message = self.MembersDB.fetch(user)[1]
            await self.bot.say(message)

    # @database.command(pass_content=True)
    async def sexists(self, ctx, *, args):
        """Checks if server exists in the DB and not it is not!"""
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
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.create(message)

    async def on_message_delete(self, message):
        if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.delete(message, datetime.datetime.utcnow())

    async def on_message_edit(self, before, after):
        if checks.is_an_ignored([before.author.id, before.server.id, before.channel.id], self.bot.Configs["Ignored IDs"]):
            return
        self.MessageDB.update(before, after)

    #async def on_reaction_add(self, reaction, user):
        #self.MessageDB.addReaction(reaction, user)

    #async def on_reaction_remove(self, reaction, user):
        #self.MessageDB.deleteReaction(reaction, user)

    #async def on_reaction_clear(self, message, reactions):
        #if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
        #    return
        #self.MessageDB.clearReaction(reaction, user)

    #@Todo
    async def on_server_join_todo(self, server):
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.create(server)

    #@Todo
    async def on_server_remove_todo(self, server):
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.delete(server)

    #async def on_server_update(self, before, after):
        #if checks.is_an_ignored([message.author.id, message.server.id, message.channel.id], self.bot.Configs["Ignored IDs"]):
        #    return
        #self.ServerDB.update(before, after)

    #@Todo
    async def on_server_available(self, server):
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.updateStatus(server, "Online")

    #@Todo
    async def on_server_unavailable(self, server):
        if checks.is_an_ignored(server.id, self.bot.Configs["Ignored IDs"]):
            return
        self.ServerDB.updateStatus(server, "Offline")

    # DUSCIRD ABIT LOGS (Discord Audit Logs)
    #async def on_member_ban(self, member):
    #    self.MembersDB.ban(member)

    #async def on_member_unban(self, server, user):
    #    self.MembersDB.unban(server, user)

    #@Todo
    async def on_member_join(self, member):
        if checks.is_an_ignored(member.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.create(before, after)

    #@Todo
    async def on_member_remove(self, member):
        if checks.is_an_ignored(member.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.delete(before, after)

    #@Todo
    async def on_member_update(self, before, after):
        if checks.is_an_ignored(before.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.update(before, after)

    #@Todo
    async def on_voice_state_update(self, before, after):
        if checks.is_an_ignored(before.id, self.bot.Configs["Ignored IDs"]):
            return
        self.MembersDB.updateVoiceState(before, after)

    # Discord Audit Logs
    #async def on_server_emojis_update(self, before, after):
    #    self.EmojisDB.update(before, after)

    #async def on_server_role_create(self, role):
    #    DB = RolesDB(self.bot.currentDB, after.server)
    #    DB.create(before, after)

    #async def on_server_role_delete(self, role):
    #    DB = RolesDB(self.bot.currentDB, after.server)
    #    DB.delete(before, after)

    #async def on_server_role_update(self, before, after):
    #    DB = RolesDB(self.bot.currentDB, after.server)
    #    DB.update(before, after)

    #async def on_channel_delete(self, channel):
    #    DB = ChannelsDB(self.bot.currentDB, after.server)
    #    DB.delete(before, after)

    #async def on_channel_create(self, channel):
    #    DB = ChannelsDB(self.bot.currentDB, after.server)
    #    DB.create(before, after)

    #async def on_channel_update(self, before, after):
    #    DB = ChannelsDB(self.bot.currentDB, after.server)
    #    DB.update(before, after)

    #Remind why me why we need to log this?
    #async def on_typing(self, channel, user, when):
        #databases.log_typing(self.bot, channel, user, when)

    #Or This?
    #async def on_group_join(self, channel, user):
        #databases.log_group_join(self.bot, channel, user)

    #Until someone tells me, I won't add support for it!
    #async def on_group_remove(self, channel, user):
        #databases.log_group_remove(self.bot, channel, user)

def setup(bot):
    bot.add_cog(Database(bot))
