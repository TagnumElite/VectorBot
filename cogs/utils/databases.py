from discord.ext import commands
from . import checks, parser#, salt
from enum import Enum
import warnings, functools
import hashlib
import discord
import MySQLdb
import json

# to expose to the eval command
import datetime
from collections import Counter

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning) #turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning) #reset filter
        return func(*args, **kwargs)

    return new_func

class DBC():
    """This is the database connection to a MySQL databse
    This class make things run smoother and easier.

    Parameters
    ----------
    database : str
        The name of the Database/Schema that will be in use.
    user : str
        The username of client that will be logging in.
    password : Optional[str]
        Defaults to a blank string. The password of the user that will be logging in.
    host : Optional[str]
        Default to `localhost`. Only use this if the database is on a different server!
    port : Optional[int]
        Defauts to `3306`. Only use this if the database is on a different port"""
    def __init__(self, database: str, user: str, password: str="", host: str="localhost", port: int=3306):
        self.Connection = MySQLdb.connect(host=host, user=user, passwd=password, db=database, port=port)
        self.Cursor = self.Connection.cursor()

    def close(self):
        """Closes the connection."""
        self.Connection.close()

    def query(self, query):
        try:
            self.Cursor.execute(query)
            self.Connection.commit()
        except Exception as me:
            print("Query Exception: {}".format(me))
            self.Connection.rollback()
            return me
        else:
            print("Query: ", query)
            return True

    def queryOne(self, query):
        try:
            self.Cursor.execute(query)
            result = self.Cursor.fetchone()
            self.Connection.commit()
        except Exception as me:
            print("QueryOne Exception: {}".format(me))
            self.Connection.rollback()
            return me
        else:
            print("QueryOne: ", query)
            if isinstance(result, list):
                for value in result:
                    print("Result: ", result)
            return result

    def queryAll(self, query):
        try:
            self.Cursor.execute(query)
            result = self.Cursor.fetchall()
            self.Connection.commit()
        except Exception as me:
            print("QueryAll Exception: {}".format(me))
            self.Connection.rollback()
            return me
        else:
            print("QueryAll: ", query)
            if isinstance(result, list):
                for row in result:
                    for value in row:
                        print("Result: ", result)
            return result

getTable = "SELECT * FROM"
PKID = "primary key(id)"
iInto = "INSERT INTO"
cTableIfNot = "CREATE TABLE IF NOT EXISTS"
cID = "`id` INT auto_increment NOT NULL"
cName = "`name` VARCHAR(100) NOT NULL"
cServerID = "`server_id` VARCHAR(20) NOT NULL"
cMessageID = "`message_id` VARCHAR(20) NOT NULL"
cAuthorID = "`author_id` VARCHAR(20) NOT NULL"
cUserID = "`user_id` VARCHAR(20) NOT NULL"
cChannelID = "`channel_id` VARCHAR(20) NOT NULL"
cContent = "`content` JSON NOT NULL"
cCreatedAt = "`created_at` DATETIME NOT NULL"
cRemovedAt = "`removed_at` DATETIME NULL"
cEditedAt = "`edited_at` DATE NOT NULL"
cError = "`error` VARCHAR(1000) NOT NULL"
cMembers = "`members` JSON NOT NULL"
cRoles = "`roles` JSON NOT NULL"
cEmojis = "`emojis` JSON NULL"
cAfkTimeout = "`afk_timeout` INT NULL"
cRegion = "`region` ENUM('Brazil', 'Central Europe', 'Hong Kong', 'Russia', 'Singapore', 'Sydney', 'US Central', 'US East', 'US South', 'US West', 'Western Europe') NOT NULL"
cAfkChannel = "`afk_channel` VARCHAR(20)"
cChannels = "`channels` JSON NOT NULL"
cIconUrl = "`icon_url` TEXT(30) NULL"
cOwner = "`server_owner` VARCHAR(20) NOT NULL"
cOffline = "`offline` TINYINT NOT NULL DEFAULT 1"
cLarge = "`large` TINYINT NOT NULL DEFAULT 0"
cMFA = "`mfa` TINYINT NOT NULL DEFAULT 0"
cVerficationLevel = "`verfication_level` ENUM('None', 'Low', 'Medium', 'High', 'Table Flip') NOT NULL DEFAULT 'None'"
cDRole = "default_role VARCHAR(20) NOT NULL"
cDChannel = "default_channel VARCHAR(20) NOT NULL"
cSlpash = "splash VARCHAR(45) NULL"
cSize = "size REAL NOT NULL"
cConfig = "config JSON"
cMentionEveryone = "`mention_everyone` TINYINT NULL DEFAULT 0"
cMentions = "`mentions` JSON NULL"
cChannelMentions = "`channel_mentions` JSON NULL"
cRoleMentions = "`role_mentions` JSON NULL"
cAttachments = "`attachments` LONGTEXT NULL"
cPinned = "`pinned` TINYINT NULL DEFAULT 0"
cReactions = "`reactions` JSON NULL"
cUsername = "`username` VARCHAR(45) NOT NULL"
cDiscriminator = "`discriminator` VARCHAR(45) NOT NULL"
cAvatarUrl = "`avatar_url` VARCHAR(45) NULL"
cDUrl = "`default_url` VARCHAR(45) NOT NULL"
cServers = "`servers` JSON NULL"
cStatus = "`status` ENUM('online', 'idle', 'dnd', 'offline') NOT NULL DEFAULT 'offline'"
cGame = "`game` LONGTEXT NULL"

class updateTypes(Enum):
    #Global
    NAME = "name"
    ROLES = "roles"
    #Messages
    CONTENT = "content"
    #Servers
    EMOJIS = "emojis"
    REGION = "region"
    AFK_TIMEOUT = "afk_timeout"
    AFK_CHANNEL = "afk_channel"

class errorType():
    EXISTS = "EXISTS"

#createErrorDBIfNot = createTableIfNot+" %s_errors ("+createID+", "+createError+", "+createCreatedAt+", "+primaryKeyID+");"

#insertErrorLog = insertInto+" %s_errors(server_id, error, created_at) VALUES('%s', '%s', '%s');"

# Message Database
class MessageDB():
    """Message Database!"""
    createMessageDBIfNot = cTableIfNot+" %s_messages ("+cID+", "+cMessageID+", "+cServerID+", "+cChannelID+", "+cAuthorID+", "+cContent+", "+cMentionEveryone+", "+cMentions+", "+cChannelMentions+", "+cRoleMentions+", "+cAttachments+", "+cPinned+", "+cReactions+", "+PKID+");"
    print("Create MessageDB If Not: ", createMessageDBIfNot)

    insertMessageLog = iInto+" %s_messages(`message_id`, `server_id`, `channel_id`, `author_id`, `content`, `mention_everyone`, `mentions`, `channel_mentions`, `role_mentions`, `attachments`, `pinned`, `reactions`) VALUES('%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', %s, '%s');"
    print("Insert MessageLog: ", insertMessageLog)

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def mentions(self, mentions):
        ids = {"mentions": []}
        for value in mentions:
            ids["mentions"].append(value.id)
        return ids

    def mentionsNamed(self, mentions, name):
        ids = "{\"%s\":[]}"%(name)
        ids = json.loads(ids)
        for idx, value in enumerate(mentions):
            ids[name].append(value.id)
        return ids

    def createTable(self):
        print("CreateTable: ", self.createMessageDBIfNot % (self.DB))
        self.DBC.query(self.createMessageDBIfNot % (self.DB))

    def exists(self, message):
        result = self.DBC.queryOne("SELECT * FROM %s_messages WHERE message_id = '%s';" % (self.DB, message.id))
        if not result:
            return False
        else:
            return True

    def create(self, message):
        print("Creating Table vd_messages")
        self.createTable()
        print("Checking if message Exists")
        if self.exists(message):
            print("Message Exists")
            return False
        msg = "{}"
        if message.type == discord.MessageType.default:
            print("Message Type: Default")
            msg = message.content.replace("\\", "\\\\")
            msg = msg.replace('\'','\\\'')
            msg = msg.replace("\\","\\\\")
            msg = "{\"content\":[{\"content\":\""+msg+"\", \"timestamp\":\""+str(message.timestamp.utcnow())+"\"}]}"
        elif message.type == discord.MessageType.pins_add:
            print("Message Type: Pin Add")
            msg = "{\"content\":[{\"content\":\"%s pinned a message to this channel.\", \"timestamp\":\"%s\"}]}" % (message.author.name, str(message.timestamp.utcnow()))
        else:
            print("Message Type: None")
            return False
        print("Create Message : ", self.insertMessageLog % (self.DB, message.id, message.server.id, message.channel.id, message.author.id, msg, int(message.mention_everyone), str(self.mentions(message.mentions)).replace("'", "\""), str(self.mentionsNamed(message.channel_mentions, "channels")).replace("'", "\""), str(self.mentionsNamed(message.role_mentions, "roles")).replace("'", "\""), json.dumps(message.attachments[0]).replace("'", "\\\"") if len(message.attachments) >= 1 else "{}", int(message.pinned), str(parser.getReactionJSON(message.reactions)).replace("'", "\"") if len(message.reactions) >= 1 else "{}"))
        return self.DBC.query(self.insertMessageLog % (self.DB, message.id, message.server.id, message.channel.id, message.author.id, msg, int(message.mention_everyone), str(self.mentions(message.mentions)).replace("'", "\""), str(self.mentionsNamed(message.channel_mentions, "channels")).replace("'", "\""), str(self.mentionsNamed(message.role_mentions, "roles")).replace("'", "\""), json.dumps(message.attachments[0]).replace("'", "\\\"") if len(message.attachments) >= 1 else "{}", int(message.pinned), str(parser.getReactionJSON(message.reactions)).replace("'", "\"") if len(message.reactions) >= 1 else "{}"))

    def _update(self, before, after):
        updates = []
        if before.content != after.content:
            updates.append('content')
        if before.mention_everyone != after.mention_everyone:
            updates.append('mention_everyone')
        if sorted(before.mentions) != sorted(after.mentions):
            updates.append('mentions')
        if before.channel_mentions != after.channel_mentions:
            updates.append('channel_mentions')
        if before.role_mentions != after.role_mentions:
            updates.append('role_mentions')
        if before.attachments != after.attachments:
            updates.append('attachments')
        if before.pinned != after.pinned:
            updates.append('pinned')
        length = len(updates)
        search = ""
        if length == 1:
            results = self.DBC.queryOne("SELECT %s FROM %s_messages WHERE message_id = '%s'" % (updates[0], self.DB, after.id))
            search = updates[0]
            if updates[0] in ['content']:
                json_data = json.loads(results[0])
            elif updates[0] in ['pinned']:
                if self.DBC.query("UPDATE `%s_messages` SET `pinned`='%s' WHERE `message_id`='%s';" % (self.DB, int(after.pinned), after.id)):
                    return True
                else:
                    return False
            json_update = parser.messageDBUpdate(after, json_data, updates)
            if self.DBC.query("UPDATE `%s_messages` SET `%s`='%s' WHERE `message_id`='%s';" % (self.DB, search, str(json_update).replace("'", "\""), after.id)):
                return True
            else:
                return False
        else:
            for idx, value in enumerate(updates):
                if idx == length-1:
                    search += value
                else:
                    search += value+", "
            results = self.DBC.queryOne("SELECT %s FROM %s_messages WHERE message_id = '%s'" % (search, self.DB, after.id))
            string_data = parser.messageDBUpdate(after, results, updates)
            print(string_data)
            print("UPDATE `%s_messages` SET %s WHERE `message_id`='%s';" % (self.DB, string_data, after.id))
            return self.DBC.query("UPDATE `%s_messages` SET %s WHERE `message_id`='%s';" % (self.DB, string_data, after.id))

    def update(self, before, after):
        """Update a message"""
        self.createTable()
        if self.exists(after):
            return self._update(before, after)
        else:
            if not self.create(before):
                return False
            else:
                if self.exists(after):
                    return self._update(after)
                else:
                    return False

    def delete(self, message, time):
        """Adds when message was deleted!"""
        self.createTable()
        if self.exists(message):
            results = self.DBC.queryOne("SELECT content FROM %s_messages WHERE message_id = '%s'" % (self.DB, message.id))
            print(results[0][0])
            data = json.loads(results[0][0])
            print(data)
            json_react = parser.messageDBDelete(message, results, time)
            return self.DBC.query("UPDATE `%s_messages` SET `content`='%s' WHERE `message_id`='%s';" % (self.DB, json_react, message.id))
        else:
            return False

    def addReaction(self, reaction, user):
        if self.exists(reaction.message):
            results = self.DBC.queryAll("SELECT reactions FROM %s_messages WHERE message_id = '%s'" % (self.DB, reaction.message.id))
            print(results[0][0])
            data = json.loads(results[0][0])
            print(data)
            json_react = parser.reactionDB(reaction, data, user)
            print(parser.jsonToDB(json_react))
            if self.DBC.query("UPDATE `%s_messages` SET `reactions`='%s' WHERE `message_id`='%s';" % (self.DB, str(json_react), reaction.message.id)):
                return True
            else:
                return False
        else:
            return False

    def deleteReaction(self, reaction, user):
        return

    def clearReaction(self, message, reactions):
        return

    def fetch(self, user: discord.Member, date: datetime = None):
        return self.DBC.queryOne("SELECT id, content FROM %s_messages WHERE author_id = '%s' ORDER BY id DESC" % (self.DB, user.id))

class UserDB():
    """User Database

    Parameters
    ----------
    DB : str
        prefix of the database"""

    createUserDBIfNot = cTableIfNot+" %s_users ("+cID+", "+cUserID+", "+cUsername+", "+cDiscriminator+", "+cAvatarUrl+", "+cDUrl+", "+cServers+", "+cStatus+", "+cGame+", "+PKID+");"

    userUpdate = " %s_server(`user_id`, `username`, `discriminator`, `avatar_url`, `default_url`, `servers`, `status`, `game`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def createTable(self):
        """Creates the table"""
        return self.DBC.query(self.createUserDBIfNot % (self.DB))

    def exists(self, user):
        """Checks if user exists in the table

        Parameters
        ----------
        user : discord.Member / discord.User
            The user to be looked up."""
        self.createTable()
        if self.DBC.queryOne("SELECT * FROM %s_users WHERE user_id = '%s';" % (self.DB, user.id)) == 0:
            return False
        else:
            return True

    def hasServer(self, user, server: discord.Server):
        """Checks if the user has the server in it!
        Returns a bool

        Parameters
        ----------
        user : discord.User can be discord.Member
            Is the Member/User that is going to be checked!
        server : discord.Server
            The discord server that is being searched for"""
        results = self.DBC.queryOne("SELECT servers FROM %s_users WHERE user_id = '%s';" % (self.DB, user.id))
        for key, value in json.loads(results[0]).items():
            if key == "servers":
                for idx, val in enumerate(value):
                    if val == server.id:
                        return True
        return False

    def create(self, user):
        self.createTable()
        if self.exists(user):
            return True
        return self.DBC.query("INSERT INTO"+self.userUpdate % (DB, user.id, user.name, user.discriminator, user.avatar_url, user.default_url, "{'servers':[]}", str(user.status), user.game.name))

    def _update(self, before, after):
        return False

    def update(self, before, after):
        """Update a user

        Parameters
        ----------
        before : discord.User
            The Discord User before the update.
        after : discord.User
            The Discord User after the update."""
        self.createTable()
        if self.exists(after):
            return self._update(before, after)
        else:
            if not self.create(before):
                return False
            else:
                if self.exists(after):
                    return self._update(after)
                else:
                    return False

    def addServer(self, member: discord.Member):
        self.createTable()
        if not self.exists():
            self.create(member)
        server = member.server
        #TODO
        return False

class ServerDB():
    """Server Databases, contains details for all the channels and config"""

    createServerDBIfNot = cTableIfNot+" %s_servers ("+cID+", "+cServerID+", "+cName+", "+cMembers+", "+cRoles+", "+cEmojis+", "+cAfkTimeout+", "+cRegion+", "+cAfkChannel+", "+cChannels+", "+cIconUrl+", "+cOwner+", "+cOffline+", "+cLarge+", "+cMFA+", "+cVerficationLevel+", "+cDRole+", "+cSlpash+", "+cSize+", "+cDChannel+", "+cCreatedAt+", "+PKID+");"

    ServerUpdate = " %s_server(`server_id`, `server_name`, `members`, `roles`, `emojis`, `afk_timeout`, `region`, `afk_channel`, `channels`, `server_icon`, `server_owner`, `server_availibity`, `server_large`, `server_mfa`, `verfication_level`, `default_role`, `server_splash`, `server_size`, `default_channel`, `created_at`) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def createTable(self):
        return self.DBC.query(self.createServerDBIfNot % (self.DB))

    def exists(self, server):
        if self.DBC.queryOne("SELECT * FROM %s_servers WHERE server_id = '%s';" % (self.DB, server.id)) == 0:
            return False
        else:
            return True

    def create(self, server):
        if self.exists(server):
            return True
        members = "NOT SETUP"#server.members
        roles = "NOT SETUP"#server.roles
        emojis = "NOT SETUP"#server.emojis
        channels = "NOT SETUP"#server.channels
        if server.afk_channel == None:
            afk_channel = None
        else:
            afk_channel = server.afk_channel.id
        #if query("INSERT INTO"+self.ServerUpdate % (DB, server.id, server.name, members, roles, emojis, server.afk_timeout, server.region, afk_channel, channels, server.icon_url, server.owner.id, server.unavailable, server.large, server.mfa_level, checks.getVerficationLevel(server.verification_level), server.default_role.id, server.splash_url, server.member_count, server.default_channel.id, server.created_at)):
        #    return True
        #else:
        #    return False
        return False

    def _update(self, before, after):
        if not self.exists(before):
            self.create(before)
        return False

    def update(self, before, after):
        """Update a server"""
        if self.exists(after):
            if self._update(before, after):
                return True
            else:
                return False
        else:
            if not self.create(before):
                return False
            else:
                if self.exists(after):
                    if self._update(after):
                        return True
                    else:
                        return False

    def delete(self, server):
        """Adds when message was deleted!"""
        self.createTable(server)
        if self.exists(server):
            return self.DBC.query("DELETE FROM %s_servers WHERE server_id=%s"%(self.DB, server.id))
        else:
            return False

    def updateStatus(bot, server, status):
        print("Update Status!")

    def addMember(self, member: discord.Member):
        userDB.addServer(member)

    def fetch(self, server, item):
        return False

@deprecated
class EmojisDB(ServerDB):
    """Emojis!"""

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def create(self, emoji):
        return False

    def delete(self, emoji):
        return False

    def _update(self, before, after):
        createServerTable(bot.currentDB)
        if serverExists(bot.currentDB, server.id):
            updateServer(bot.currentDB, server)
        else:
            createServer(bot.currentDB, server)
        return False

    def update(self, before, after):
        if before is None:
            return self.create(after)
        elif after is None:
            return self.delete(before)
        else:
            return self._update(before, after)

@deprecated
class RolesDB(ServerDB):
    """Roles!"""

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def create(self, role):
        createServerTable(bot.currentDB)
        if serverExists(bot.currentDB, server.id):
            updateServer(bot.currentDB, server)
        else:
            createServer(bot.currentDB, server)

    def delete(self, role):
        createServerTable(bot.currentDB)
        if serverExists(bot.currentDB, server.id):
            updateServer(bot.currentDB, server)
        else:
            createServer(bot.currentDB, server)

    def update(self, before, after):
        createServerTable(bot.currentDB)
        if serverExists(bot.currentDB, server.id):
            updateServer(bot.currentDB, server)
        else:
            createServer(bot.currentDB, server)

class MembersDB(ServerDB):
    """Members Database Class"""

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def create(self, member):
        self.addMember(member)
        pass

    def delete(self, member):
        return

    def update(self, before, after):
        return

    def ban(self, member):
        return

    def unban(self, server, user):
        return

    def updateVoiceState(self, before, after):
        return

class ChannelsDB(ServerDB):
    """Channels Database Class"""

    def __init__(self, DB, server):
        self.DB = DB
        self.Server = server

    def create(self, channel):
        return

    def update(self, before, after):
        return

    def delete(self, channel):
        return

class ConfigDB():
    """Config Database Class"""
    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

def log_ready(bot):
    return

def log_resumed(bot):
    return

def log_error(bot, error):
    #if query(createErrorDBIfNot % (bot.currentDB)) == True:
        #print("Creating Table %s_errors" % (bot.currentDB))
    #query(insertErrorLog % (bot.curretDB, error, datetime.datetime.utcnow()))
    return

def log_raw_recieve(bot, msg):
    return

def log_raw_send(bot, payload):
    return

def log_typing(bot, channel, user, when):
    return False

def log_group_join(bot, channel, user):
    return False

def log_group_remove(bot, channel, user):
    return False
#SOMEONE SEND HELP, IM STUCK IN AN LOOP BETWEEN A MAINFRAME AND A POTATO
