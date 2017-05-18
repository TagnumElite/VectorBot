from discord.ext import commands
from . import checks, parser#, salt
from _mysql_exceptions import OperationalError
#from _mysql.Connector import errorcode
from enum import Enum
import warnings, functools
import hashlib
import discord
import MySQLdb
from MySQLdb import MySQLError
import json

# to expose to the eval command
import datetime
from collections import Counter

# Decorator to defined deprecated functions
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
        Defauts to `3306`. Only use this if the database is on a different port
    retries: Optional[int]
        Defaults to `20`. This is the amount of times it will try to reconnect to the Database"""
    Buffer = []

    def __init__(self, database: str, user: str, password: str="", host: str="localhost", port: int=3306, retries: int=20):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.retries = retries
        self.Connecting = False
        self._connect()

    def _connect(self):
        if self.Connecting:
            return
        else:
            self.Connecting = False
            for trie in range(self.retries):
                if trie is not self.retires-1:
                    try:
                        self.Connection = MySQLdb.connect(
                            host=self.host,
                            user=self.user,
                            passwd=self.password,
                            db=self.database,
                            port=self.port
                        )
                    except Exception as E:
                        errno = E.args[0]
                        if errno is 2003:
                            return
                        else:
                            self.Conntection = False
                            raise(E)
                else: #Last Try
                    try:
                        self.Connection = MySQLdb.connect(
                            host=self.host,
                            user=self.user,
                            passwd=self.password,
                            db=self.database,
                            port=self.port
                        )
                    except Exception as E:
                        errno = E.args[0]
                        if errno is 2003:
                            exit("Couldn't Connect to the MySQL Server")
                        else:
                            self.Conntection = False
                            raise(E)
        self.Cursor = self.Connection.cursor()
        self.query("SET SQL_SAFE_UPDATES = 0;")

    def reconnect(self):
        try:
            self._connect()
        except Exception as E:
            raise(E)

    def close(self):
        """Closes the connection."""
        self.query("SET SQL_SAFE_UPDATES = 1;")
        self.Connection.close()

    def query(self, query):
        try:
            print("Query: ", query)
            self.Cursor.execute(query)
            self.Connection.commit()
        except MySQLError as me:
            print("Exception Args", me.args)
            if me.args[0] in [2006, 2013]:
                try:
                    self.reconnect()
                except Exception as E:
                    raise(E)
                else:
                    return self.query(query)
            else:
                print("Query Exception: {}".format(me))
                self.Buffer.append(query)
                self.Connection.rollback()
                raise me
        else:
            return True

    def queryOne(self, query):
        try:
            print("QueryOne: ", query)
            self.Cursor.execute(query)
            result = self.Cursor.fetchone()
            self.Connection.commit()
        except MySQLError as me:
            print("Exception Args", me.args)
            if me.args[0] in [2006, 2013]:
                self.reconnect()
                return self.query(query) # I know infinite loop.
            else:
                print("Query Exception: {}".format(me))
                self.Buffer.append(query)
                self.Connection.rollback()
                raise me
        else:
            if isinstance(result, list):
                for value in result:
                    print("Result: ", result)
            return result

    def queryAll(self, query):
        try:
            print("QueryAll: ", query)
            self.Cursor.execute(query)
            result = self.Cursor.fetchall()
            self.Connection.commit()
        except MySQLError as me:
            print("Exception Args", me.args)
            if me.args[0] in [2006, 2013]:
                self.reconnect()
                return self.query(query) # I know infinite loop.
            else:
                print("Query Exception: {}".format(me))
                self.Buffer.append(query)
                self.Connection.rollback()
                raise me
        else:
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
    """Message Database!

    Parameters
    ----------
    DBC: DBC
        The SQL Connection
    DB: str
        The Table Prefix"""
    createMessageDBIfNot = cTableIfNot+" {PRE}_messages ("+cID+", "+cMessageID+", "+cServerID+", "+cChannelID+", "+cAuthorID+", "+cContent+", "+cMentionEveryone+", "+cMentions+", "+cChannelMentions+", "+cRoleMentions+", "+cAttachments+", "+cPinned+", "+cReactions+", "+PKID+");"

    insertMessageLog = iInto+" {PRE}_messages(`message_id`, `server_id`, `channel_id`, `author_id`, `content`, `mention_everyone`, `mentions`, `channel_mentions`, `role_mentions`, `attachments`, `pinned`, `reactions`) VALUES('{MID}', '{SID}', '{CID}', '{AID}', '{CON}', {MENE}, '{MENS}', '{CMENS}', '{RMENS}', '{ATTCHS}', {PIN}, '{REACTS}');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB
        self.createTable() # Create Table on startup. Only creates a table if one doesn't exist

    def mentions(self, mentions):
        """Converts a list of Menstions to a list of ids of the users mentioned

        Parameters
        ----------
        mensions: list[discord.Mensions]
            The list of mensions from the message"""
        ids = {"mentions": []}
        for value in mentions:
            ids["mentions"].append(value.id)
        return ids

    def mentionsNamed(self, mentions, name):
        """Have I ever used this?

        .. warning::
            deprecated

        Parameters
        ----------
        mensions: list[discord.Mensions]
            The list of mensions from the message
        name: str
            The name of the mension list"""
        ids = '{"%s":[]}'%(name)
        ids = json.loads(ids)
        for idx, value in enumerate(mentions):
            ids[name].append(value.id)
        return ids

    def createTable(self):
        """Used to create the table"""
        self.DBC.query(self.createMessageDBIfNot.format(PRE=self.DB))

    def exists(self, message):
        """Checks if the message exists

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        result = self.DBC.queryOne(
            "SELECT * FROM {PRE}_messages WHERE message_id = '{MID}';".format(
                PRE=self.DB,
                MID=message.id
            )
        )
        if not result:
            return False
        else:
            return True

    def create(self, message):
        """Create a entry to the SQL of an message

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        self.createTable() # we need to make sure the table exists
        if self.exists(message): # This should never happen
            return False
        msg = "{}"
        if message.type == discord.MessageType.default: #Check if the message is a normal message
            msg = parser.MessageDBReplace(message.content)
            msg = '{"content":[{"content":"'+msg+'", "timestamp":"'+str(message.timestamp.utcnow())+'"}]}'
        elif message.type == discord.MessageType.pins_add:
            msg = '{"content":[{"content":"{author} pinned a message to this channel.", "timestamp":"{timestamp}"}]}'.format(
                author=message.author.name,
                timestamp=str(message.timestamp.utcnow())
            )
        else:
            return False
        return self.DBC.query(
            self.insertMessageLog.format(
                PRE=self.DB,
                MID=message.id,
                SID=message.server.id,
                CID=message.channel.id,
                AID=message.author.id,
                CON=msg,
                MENE=int(message.mention_everyone),
                MENS=str(self.mentions(message.mentions)).replace("'", "\""),
                CMENS=str(self.mentionsNamed(message.channel_mentions, "channels")).replace("'", "\""),
                RMENS=str(self.mentionsNamed(message.role_mentions, "roles")).replace("'", "\""),
                ATTCHS=json.dumps(message.attachments[0]).replace("'", "\\\"") if len(message.attachments) >= 1 else "{}",
                PIN=int(message.pinned),
                REACTS=str(parser.getReactionJSON(message.reactions)).replace("'", "\"") if len(message.reactions) >= 1 else "{}"
            )
        )

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
            json_data = {}
            results = self.DBC.queryOne(
                "SELECT {UP} FROM {PRE}_messages WHERE message_id = '{MID}'".format(
                    UP=updates[0],
                    PRE=self.DB,
                    MID=after.id
                )
            )
            search = updates[0]
            if search is 'content':
                json_data = json.loads(results[0])
            elif search is 'pinned':
                return self.DBC.query(
                    "UPDATE `{PRE}_messages` SET `pinned`='{PIN}' WHERE `message_id`='{MID}';".format(
                        PRE=self.DB,
                        PIN=int(after.pinned),
                        MID=after.id
                    )
                )
            json_update = parser.messageDBUpdate(after, json_data, updates)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `{KEY}`='{VAL}' WHERE `message_id`='{MID}';".format(
                    PRE=self.DB,
                    KEY=search,
                    VAL=parser.MessageDBReplace(str(json_update).replace("'", '"')),
                    MID=after.id
                )
            )
        else:
            for idx, value in enumerate(updates):
                if idx == length-1:
                    search += value
                else:
                    search += value+", "
            results = self.DBC.queryOne(
                "SELECT {KEY} FROM {PRE}_messages WHERE message_id = '{MID}'".format(
                    KEY=search,
                    PRE=self.DB,
                    MID=after.id
                )
            )
            string_data = parser.messageDBUpdate(after, results, updates)
            return self.DBC.query(
                "UPDATE `%s_messages` SET %s WHERE `message_id`='%s';" % (
                    self.DB,
                    string_data,
                    after.id
                )
            )

    def update(self, before, after):
        """Update a message"""
        self.createTable()
        if self.exists(after):
            return self._update(before, after)
        else:
            if not self.create(before):
                return False  # I will raise an error here later but for now it is fine
            else:
                if self.exists(after):
                    return self._update(after) #Why do I double check? because I must
                else:
                    return False  # I will raise an error here later but for now it is fine

    def delete(self, message, time):
        """Called when a message is deleted.

        Parameters
        ----------
        message: discord.Message
            The discord message that was deleted
        time: datetime.datetime.utcnow()
            UTC Time when message was deleted"""
        self.createTable()
        if self.exists(message):
            results = self.DBC.queryOne(
                "SELECT content FROM {PRE}_messages WHERE message_id = '{MID}'".format(
                    PRE=self.DB,
                    MID=message.id
                )
            )
            data = json.loads(results[0])
            json_react = parser.messageDBDelete(data, time)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `content`='{VAL}' WHERE `message_id`='{MID}';".format(
                    PRE=self.DB,
                    VAL=str(json_react).replace("'", '"').replace("None", "null"),
                    MID=message.id
                )
            )
        else:
            return False # I will raise an error here later but for now it is fine

    def addReaction(self, reaction, user):
        """Called when a reaction is added

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""
        if self.exists(reaction.message):
            results = self.DBC.queryAll(
                "SELECT reactions FROM {PRE}_messages WHERE message_id = '{MID}'".format(
                    PRE=self.DB,
                    MID=reaction.message.id
                )
            )
            print(results[0][0])
            data = json.loads(results[0][0])
            print(data)
            json_react = parser.reactionDB(reaction, data, user)
            print(parser.jsonToDB(json_react))
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `reactions`='{VAL}' WHERE `message_id`='{MID}';".format(
                    PRE=self.DB,
                    VAL=str(json_react),
                    MID=reaction.message.id
                )
            )
        else:
            return False

    def deleteReaction(self, reaction, user):
        """Called when a reaction is deleted

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""
        return

    def clearReaction(self, message, reactions):
        """Called when all reaction on a message is deleted

        Parameters
        ----------
        message: discord.Message
            The reaction
        reactions: list[discord.Reaction]
            The User"""
        return

    def fetch(self, *, Query):
        """Fetches data from DB. NOT SETUP"""
        pass
        #return self.DBC.queryOne(
        #    "SELECT id, content FROM {PRE}_messages WHERE author_id = '{AID}' ORDER BY id DESC".format(
        #        PRE=self.DB,
        #        AID=user.id
        #    )
        #)

class UserDB():
    """User Database

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

    createUserDBIfNot = cTableIfNot+" {PRE}_users ("+cID+", "+cUserID+", "+cUsername+", "+cDiscriminator+", "+cAvatarUrl+", "+cDUrl+", "+cServers+", "+cStatus+", "+cGame+", "+PKID+");"

    userUpdate = " {PRE}_server(`user_id`, `username`, `discriminator`, `avatar_url`, `default_url`, `servers`, `status`, `game`) VALUES('{UID}', '{USN}', '{DIS}', '{AURL}', '{DURL}', '{SERV}', '{STA}', '{GME}');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def createTable(self):
        """Creates the table"""
        return self.DBC.query(self.createUserDBIfNot.format(PRE=self.DB))

    def exists(self, user):
        """Checks if user exists in the table

        Parameters
        ----------
        user : discord.Member / discord.User
            The user to be looked up."""
        self.createTable()
        return not self.DBC.queryOne(
            "SELECT * FROM %s_users WHERE user_id = '%s';" % (
                self.DB,
                user.id
            )
        ) == 0

    def hasServer(self, user, server: discord.Server):
        """Checks if the user has the server in it!
        Returns a bool

        Parameters
        ----------
        user : discord.User / discord.Member
            Is the Member/User that is going to be checked!
        server : discord.Server
            The discord server that is being searched for"""
        results = self.DBC.queryOne(
            "SELECT servers FROM %s_users WHERE user_id = '%s';" % (
                self.DB,
                user.id
            )
        )
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
        return self.DBC.query(
            "INSERT INTO"+self.userUpdate % (
                DB,
                user.id,
                user.name,
                user.discriminator,
                user.avatar_url,
                user.default_url,
                "{'servers':[]}",
                str(user.status),
                user.game.name
            )
        )

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

    def addMember(self, server: discord.Server):
        """Called when a server is joined
        WAIT STOP RIGHT HERE.
        I NEED TO PLAN OUT ServerDB/UserDB/MemberDB Cross compatibility and stuff!
        Parameters
        ----------
        server:"""
        return False

class ServerDB():
    """Server Databases, contains details for all the channels and config

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

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
    """Emojis!

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

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
    """Roles!

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

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
    """Members Database Class

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

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
    """Channels Database Class

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""

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
    """Config Database Class

    Parameters
    ----------
    DBC: DBC
        I am lazy
    DB: str
        Prefix"""
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

#SOMEONE SEND HELP, IM STUCK IN AN LOOP BETWEEN A MAINFRAME AND A POTATO
