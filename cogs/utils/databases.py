from discord.ext import commands
from . import checks
import discord
import MySQLdb

# to expose to the eval command
import datetime
from collections import Counter

dbs = MySQLdb.connect(host="localhost", user="vectorbot", passwd="", db="vector")
c = dbs.cursor()

class DBC():
    def __init__(self, user: str="vectorbot", passwd:str=None, db:str="vector", host:str="localhost"):
        self.Connection = MySQLdb.connection(host=host, user=user, passwd=passwd, db=db)
        self.cursor = self.Connection.cursor()

    def close(self):
        self.Connection.close()

    def execute(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

getTable = "SELECT * FROM"
primaryKeyID = "primary key(id)"
insertInto = "INSERT INTO"

createTableIfNot = "CREATE TABLE IF NOT EXISTS"
createID = "id INT auto_increment NOT NULL"
createServerID = "server_id VARCHAR(20) NOT NULL"
createServerName = "server_name VARCHAR(100) NOT NULL"
createMessageID = "message_id VARCHAR(20) NOT NULL"
createMessageContent = "message_content VARCHAR(1000) NOT NULL"
createAuthorID = "author_id VARCHAR(20) NOT NULL"
createChannelID = "channel_id VARCHAR(20) NOT NULL"
createCreatedAt = "created_at DATETIME NOT NULL"
createRemovedAt = "removed_at DATETIME"
createEditedAt = "edited_at DATE NOT NULL"
createError = "error VARCHAR(1000) NOT NULL"
createMembers = "server_members INT NOT NULL"
createRoles = "server_roles JSON"
createEmojis = "emojis JSON"
createAfkTimeout = "afk_timeout INT"
createRegion = "region VARCHAR(20) NOT NULL"
createAfkChannel = "afk_channel VARCHAR(20)"
createChannels = "channels JSON"
createServerIcon = "server_icon TEXT"
createServerOwner = "server_owner VARCHAR(20) NOT NULL"
createServerOnline = "server_availibity VARCHAR(10) NOT NULL"
createServerLarge = "server_large VARCHAR(10) NOT NULL"
createServerMFA = "server_mfa VARCHAR(20) NOT NULL"
createVerficationLevel = "verification_level INT NOT NULL"
createDefaultRole = "default_role VARCHAR(20)"
createDefaultChannel = "default_channel VARCHAR(20)"
createServerSlpash = "server_splash TEXT"
createServerSize = "server_size INT NOT NULL"

createErrorDBIfNot = createTableIfNot+" %s_errors ("+createID+", "+createError+", "+createCreatedAt+", "+primaryKeyID+");"

insertErrorLog = insertInto+" %s_errors(server_id, error, created_at) VALUES('%s', '%s', '%s');"

def query(query):
    try:
        c.execute(query)
        dbs.commit()
    except Exception as me:
        print ("{}".format(me))
        return False
    else:
        return True

def log_ready(bot):
    return

def log_resumed(bot):
    return

def log_error(bot, error):
    if query(createErrorDBIfNot % (bot.currentDB)) == True:
        print("Creating Table %s_errors" % (bot.currentDB))
    query(insertErrorLog % (bot.curretDB, error, datetime.datetime.utcnow()))

def log_raw_recieve(bot, msg):
    return

def log_raw_senf(bot, payload):
    return

createMessageDBIfNot = createTableIfNot+" %s_messages ("+createID+", "+createServerID+", "+createMessageID+", "+createMessageContent+", "+createAuthorID+", "+createChannelID+", "+createCreatedAt+", "+createRemovedAt+", "+primaryKeyID+");"

insertMessageLog = insertInto+" %s_messages(server_id, message_id, message_content, author_id, channel_id, created_at) VALUES('%s', '%s', '%s', '%s', '%s', '%s');"

def createMessageTable(DB):
    if query(createMessageDBIfNot % (DB)):
        print("Creating Table %s_messages" % (DB))


def createMessage(DB, message):
    msg = message.content.replace("\\","\\\\")
    query(insertMessageLog % (bot.currentDB, message.server.id, message.id, msg, message.author.id, message.channel.id, message.timestamp))
    return

def updateMessage(DB, before, after=None):
    if after != None:
        updates = checks.getServerDif(before, after)
        updateString = ""
        for k, x in updates.items():
            updateString = updateString + k + " : " + x + "\n"
        print(updateString)
    return

def messageExists(DB, serverID):
    if query("SELECT id FROM %s_servers WHERE server_id = '%s';" % (DB, serverID)) == 0:
        return False
    else:
        return True

def log_message(bot, message):
    createMessageTable(bot.currentDB)
    createMessage

def log_message_delete(bot, message):
    createMessageTable(bot.currentDB)
    if query("SELECT id FROM %s_messages WHERE message_id = '%s';" % (bot.currentDB, message.id)) == 0:
        return

def log_message_edit(bot, before, after):
    createMessageTable(bot.currentDB)

def log_reaction_add(bot, reaction, user):
    return

def log_reaction_remove(bot, reaction, user):
    return

def log_reaction_clear(bot, message, reactions):
    return

def log_channal_delete(bot, channel):
    return

def log_channal_create(bot, channel):
    return

def log_channel_update(bot, before, after):
    return

def log_member_join(bot, member):
    return

def log_member_remove(bot, member):
    return

def log_member_update(bot, before, after):
    return

createServerDBIfNot = createTableIfNot+" %s_servers ("+createID+", "+createServerID+", "+createServerName+", "+createMembers+", "+createRoles+", "+createEmojis+", "+createAfkTimeout+", "+createRegion+", "+createAfkChannel+", "+createChannels+", "+createServerIcon+", "+createServerOwner+", "+createServerOnline+", "+createServerLarge+", "+createServerMFA+", "+createVerficationLevel+", "+createDefaultRole+", "+createServerSlpash+", "+createServerSize+", "+createDefaultChannel+", "+createCreatedAt+", "+primaryKeyID+");"

ServerUpdate = " %s_server(server_id, server_name, members, roles, emojis, afk_timeout, region, afk_channel, channels, server_icon, server_owner, server_availibity, server_large, server_mfa, verfication_level, default_role, server_splash, server_size, default_channel, created_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

def createServerTable(DB):
    if query(createServerDBIfNot % (DB)) == True:
        print("Creating Table %s_servers" % (DB))

def createServer(DB, server):
    members = "NOT SETUP"#server.members
    roles = "NOT SETUP"#server.roles
    emojis = "NOT SETUP"#server.emojis
    channels = "NOT SETUP"#server.channels
    if server.afk_channel == None:
        afk_channel = None
    else:
        afk_channel = server.afk_channel.id
    query("INSERT INTO"+ServerUpdate % (DB, server.id, server.name, members, roles, emojis, server.afk_timeout, server.region, afk_channel, channels, server.icon_url, server.owner.id, not server. unavailable, server.large, server.mfa_level, checks.getVerficationLevel(server.verification_level), server.default_role.id, server.splash_url, server.member_count, server.default_channel.id, server.created_at))
    return

def updateServer(DB, before, after=None):
    if after != None:
        updates = checks.getServerDif(before, after)
        updateString = ""
        for k, x in updates.items():
            updateString = updateString + k + " : " + x + "\n"
        print(updateString)
    return

def serverExists(DB, serverID):
    if query("SELECT id FROM %s_servers WHERE server_id = '%s';" % (DB, serverID)) == 0:
        return False
    else:
        return True

def log_server_join(bot, server):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_remove(bot, server):
    createServerTable(bot.currentDB)
    server.unavailable = True
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_update(bot, before, after):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, after.id):
        updateServer(bot.currentDB, before, after)
    else:
        createServer(bot.currentDB, after)

def log_server_role_create(bot, role):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_role_delete(bot, role):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_role_update(bot, before, after):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_emojis_update(bot, before, after):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_available(bot, server):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_server_unavailable(bot, server):
    createServerTable(bot.currentDB)
    if serverExists(bot.currentDB, server.id):
        updateServer(bot.currentDB, server)
    else:
        createServer(bot.currentDB, server)

def log_voice_state_update(bot, before, after):
    return

def log_member_ban(bot, member):
    return

def log_member_unban(bot, server, user):
    return

def log_typing(bot, channel, user, when):
    return

def log_group_join(bot, channel, user):
    return

def log_group_remove(bot, channel, user):
    return

def get_message(bot, message):
    return

def get_ready(bot):
    return

def get_resumed(bot):
    return

def get_error(bot, error):
    return

def get_raw_recieve(bot, msg):
    return

def get_raw_senf(bot, payload):
    return

def get_message_delete(bot, message):
    return

def get_message_edit(bot, before, after):
    return

def get_reaction_add(bot, reaction, user):
    return

def get_reaction_remove(bot, reaction, user):
    return

def get_reaction_clear(bot, message, reactions):
    return

def get_channal_delete(bot, channel):
    return

def get_channal_create(bot, channel):
    return

def get_channel_update(bot, before, after):
    return

def get_member_join(bot, member):
    return

def get_member_remove(bot, member):
    return

def get_member_update(bot, before, after):
    return

def get_server_join(bot, server):
    return

def get_server_remove(bot, server):
    return

def get_server_update(bot, before, after):
    return

def get_server_role_create(bot, role):
    return

def get_server_role_delete(bot, role):
    return

def get_server_role_update(bot, before, after):
    return

def get_server_emojis_update(bot, before, after):
    return

def get_server_available(bot, server):
    return

def get_server_unavailable(bot, server):
    return

def get_voice_state_update(bot, before, after):
    return

def get_member_ban(bot, member):
    return

def get_member_unban(bot, server, user):
    return

def get_typing(bot, channel, user, when):
    return

def get_group_join(bot, channel, user):
    return

def get_group_remove(bot, channel, user):
    return
