from discord.ext import commands
from .utils import databases, config #checks,
import discord
import inspect
import urllib

# to expose to the eval command
import datetime
from collections import Counter

class Database:
    """Database Commands"""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            databases.log_message(self.bot, message)

    async def on_ready(self):
        databases.log_ready(self.bot)

    async def on_resumed(self):
        databases.log_resumed(self.bot)

    async def on_error(self, error):
        databases.log_error(self.bot, error)

    async def on_socket_raw_recieve(self, msg):
        databases.log_raw_recieve(self.bot, msg)

    async def on_socket_raw_send(self, payload):
        databases.log_raw_senf(self.bot, payload)

    async def on_message_delete(self, message):
        databases.log_message_delete(self.bot, message)

    async def on_message_edit(self, before, after):
        databases.log_message_edit(self.bot, before, after)

    async def on_reaction_add(self, reaction, user):
        databases.log_reaction_add(self.bot, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        databases.log_reaction_remove(self.bot, reaction, user)

    async def on_reaction_clear(self, message, reactions):
        databases.log_reaction_clear(self.bot, message, reactions)

    async def on_channel_delete(self, channel):
        databases.log_channal_delete(self.bot, channel)
        if config.exists(channel.server.id, self.bot) == True:
            data = config.getConfig(channel.server.id, self.bot)
        elif config.exists(channel.server.id, self.bot) == None:
            data = config.getConfig(channel.server.id, self.bot, No=True)
        else:
            config.createServerConfig(server, self.bot.currentDir)

        if data["channels"].has_key(channel.id):
            del data["channels"][channel.id]
            config.saveServerConfig(server.id, data, self.bot):

    async def on_channel_create(self, channel):
        databases.log_channal_create(self.bot, channel)
        if config.exists(channel.server.id, self.bot) == True:
            data = config.getConfig(channel.server.id, self.bot)
        elif config.exists(channel.server.id, self.bot) == None:
            data = config.getConfig(channel.server.id, self.bot, No=True)
        else:
            config.createServerConfig(server, self.bot.currentDir)

        if data["channels"].has_key(channel.id):
            del data["channels"][channel.id]
            config.saveServerConfig(server.id, data, self.bot):

    async def on_channel_update(self, before, after):
        databases.log_channel_update(self.bot, before, after)

    async def on_member_join(self, member):
        databases.log_member_join(self.bot, member)

    async def on_member_remove(self, member):
        databases.log_member_remove(self.bot, member)

    async def on_member_update(self, before, after):
        databases.log_member_update(self.bot, before, after)

    async def on_server_join(self, server):
        databases.log_server_join(self.bot, server)

    async def on_server_remove(self, server):
        databases.log_server_remove(self.bot, server)

    async def on_server_update(self, before, after):
        databases.log_server_update(self.bot, before, after)

    async def on_server_role_create(self, role):
        databases.log_server_role_create(self.bot, role)

    async def on_server_role_delete(self, role):
        databases.log_server_role_delete(self.bot, role)

    async def on_server_role_update(self, before, after):
        databases.log_server_role_update(self.bot, before, after)

    async def on_server_emojis_update(self, before, after):
        databases.log_server_emojis_update(self.bot, before, after)

    async def on_server_available(self, server):
        databases.log_server_available(self.bot, server)

    async def on_server_unavailable(self, server):
        databases.log_server_unavailable(self.bot, server)

    async def on_voice_state_update(self, before, after):
        databases.log_voice_state_update(self.bot, before, after)

    async def on_member_ban(self, member):
        databases.log_member_ban(self.bot, member)

    async def on_member_unban(self, server, user):
        databases.log_member_unban(self.bot, server, user)

    async def on_typing(self, channel, user, when):
        databases.log_typing(self.bot, channel, user, when)

    async def on_group_join(self, channel, user):
        databases.log_group_join(self.bot, channel, user)

    async def on_group_remove(self, channel, user):
        databases.log_group_remove(self.bot, channel, user)

def setup(bot):
    bot.add_cog(Database(bot))
