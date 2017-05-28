"""
@author: TagnumElite
"""

from . import checks, parser
from .parser import Parser, MemberParser, MessageParser, ServerParser, ConfigParser, ChannelParser, RoleParser, EmojiParser
from _mysql_exceptions import OperationalError
import warnings, functools
import discord
import MySQLdb
from MySQLdb import MySQLError
import json

# to expose to the eval command
import datetime
from collections import Counter

# Setup Parsers
Parser = Parser()
MessageParser = MessageParser()
MemberParser = MemberParser()
ServerParser = ServerParser()
ConfigParser = ConfigParser()
ChannelParser = ChannelParser()
RoleParser = RoleParser()
EmojiParser = EmojiParser()

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
                if trie is not self.retries-1:
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
        """Reconnects to the database"""
        try:
            self._connect()
        except Exception as E:
            raise(E)

    def close(self):
        """Closes the connection."""
        self.query("SET SQL_SAFE_UPDATES = 1;")
        self.Connection.close()

    def query(self, query):
        """Make an query but doesn't return anything

        Parameters
        ----------
        query: str
            The MySQL query you want to make"""
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
        """Make an query but returns the first result

        Parameters
        ----------
        query: str
            The MySQL query you want to make"""
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
        """Make an query but returns all results

        Parameters
        ----------
        query: str
            The MySQL query you want to make"""
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
cID = "`id` BIGINT(18) NOT NULL"
cName = "`name` VARCHAR(100) NOT NULL"
cServerID = "`server_id` VARCHAR(20) NOT NULL"
cMessageID = "`message_id` VARCHAR(20) NOT NULL"
cAuthorID = "`author_id` VARCHAR(20) NOT NULL"
cUserID = "`user_id` VARCHAR(20) NOT NULL"
cChannelID = "`channel_id` VARCHAR(20) NOT NULL"
cContent = "`content` JSON NOT NULL"
cCreatedAt = "`created_at` DATETIME NOT NULL"
cRemovedAt = "`removed_at` DATETIME NULL"
cConfig = "`config` JSON NULL"
cEditedAt = "`edited_at` DATE NOT NULL"
cError = "`error` VARCHAR(1000) NOT NULL"
cMembers = "`members` JSON NOT NULL"
cRoles = "`roles` JSON NOT NULL"
cEmojis = "`emojis` JSON NULL"
cAfkTimeout = "`afk_timeout` INT NULL"
cRegion = "`region` VARCHAR(30) NOT NULL"
cAfkChannel = "`afk_channel` VARCHAR(20)"
cChannels = "`channels` JSON NOT NULL"
cIconUrl = "`icon_url` TEXT(30) NULL"
cOwner = "`owner` VARCHAR(20) NOT NULL"
cStatus = "`status` TINYINT NOT NULL DEFAULT 1"
cLarge = "`large` TINYINT NOT NULL DEFAULT 0"
cMFA = "`mfa` TINYINT NOT NULL DEFAULT 0"
cVerficationLevel = "`verfication_level` VARCHAR(30) NOT NULL DEFAULT 'None'"
cDRole = "`default_role` VARCHAR(20) NOT NULL"
cDChannel = "`default_channel` VARCHAR(20) NOT NULL"
cSlpash = "`splash` VARCHAR(45) NULL"
cSize = "`size` REAL NOT NULL"
cConfig = "config JSON"
cMentions = "`mentions` JSON NULL"
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

class MessageDB():
    """Message Database!

    Parameters
    ----------
    DBC: DBC
        The SQL Connection
    DB: str
        The Table Prefix"""
    createMessageDBIfNot = cTableIfNot+" {PRE}_messages ("+cID+", "+cServerID+", "+cChannelID+", "+cAuthorID+", "+cContent+", "+cMentions+", "+cAttachments+", "+cPinned+", "+cReactions+", "+PKID+");"

    insertMessageLog = iInto+" {PRE}_messages(`id`, `server_id`, `channel_id`, `author_id`, `content`, `mentions`, `attachments`, `pinned`, `reactions`) VALUES({MID}, '{SID}', '{CID}', '{AID}', '{CON}', '{MENS}', '{ATTCHS}', {PIN}, '{REACTS}');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB
        self.createTable() # Create Table on startup. Only creates a table if one doesn't exist
    def createTable(self):
        """Used to create the table"""
        self.DBC.query(self.createMessageDBIfNot.format(PRE=self.DB))

    def exists(self, message: discord.Message):
        """Checks if the message exists

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        result = self.DBC.queryOne(
            "SELECT * FROM {PRE}_messages WHERE `id`={MID};".format(
                PRE=self.DB,
                MID=int(message.id)
            )
        )
        if not result:
            return False
        else:
            return True

    def create(self, message: discord.Message):
        """Create a entry to the SQL of an message

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        self.createTable()        # Make sure the Table Exists
        if self.exists(message):  # If the message already exists in the database
            #self.update(message) # Then update the message! TODO
            return False
        msg = "{}"
        if message.type == discord.MessageType.default: #Check if the message is a normal message
            msg = MessageParser.MessageDBReplace(message.content)
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
                MID=int(message.id),
                SID=message.server.id,
                CID=message.channel.id,
                AID=message.author.id,
                CON=msg,
                MENS=str(MessageParser.MessageMentions(message)).replace("'", "\""),
                ATTCHS=json.dumps(message.attachments[0]).replace("'", "\\\"") if len(message.attachments) >= 1 else "{}",
                PIN=int(message.pinned),
                REACTS=str(MessageParser.getReactionJSON(message.reactions)).replace("'", "\"") if len(message.reactions) >= 1 else "{}"
            )
        )

    def _update(self, before: discord.Message, after: discord.Message):
        updates = []
        if before.content != after.content:
            updates.append('content')
        if (before.mention_everyone is not after.mention_everyone or
            sorted(before.mentions) is not sorted(after.mentions) or
            before.channel_mentions is not after.channel_mentions or
            before.role_mentions is not after.role_mentions):
            updates.append('mentions')
        if before.attachments != after.attachments:
            updates.append('attachments')
        if before.pinned != after.pinned:
            updates.append('pinned')
        length = len(updates)
        search = ""
        if length == 1:
            json_data = {}
            results = self.DBC.queryOne(
                "SELECT {UP} FROM {PRE}_messages WHERE `id`={MID}".format(
                    UP=updates[0],
                    PRE=self.DB,
                    MID=int(after.id)
                )
            )
            search = updates[0]
            if search is 'content':
                json_data = json.loads(results[0])
            elif search is 'pinned':
                return self.DBC.query(
                    "UPDATE `{PRE}_messages` SET `pinned`='{PIN}' WHERE `id`={MID};".format(
                        PRE=self.DB,
                        PIN=int(after.pinned),
                        MID=int(after.id)
                    )
                )
            json_update = MessageParser.MessageUpdate(after, json_data, updates)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `{KEY}`='{VAL}' WHERE `id`={MID};".format(
                    PRE=self.DB,
                    KEY=search,
                    VAL=MessageParser.MessageDBReplace(str(json_update).replace("'", '"')),
                    MID=int(after.id)
                )
            )
        else:
            for idx, value in enumerate(updates):
                if idx == length-1:
                    search += value
                else:
                    search += value+", "
            results = self.DBC.queryOne(
                "SELECT {KEY} FROM {PRE}_messages WHERE `id`={MID}".format(
                    KEY=search,
                    PRE=self.DB,
                    MID=int(after.id)
                )
            )
            string_data = MessageParser.MessageUpdate(after, results, updates)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET {DATA} WHERE `id`={MID};".format(
                    PRE=self.DB,
                    DATA=string_data,
                    MID=int(after.id)
                )
            )

    def update(self, before: discord.Message, after: discord.Message):
        """Update a message

        Parameters
        ----------
        before: discord.Message
        after: discord.Message"""
        self.createTable()
        if self.exists(after):
            return self._update(before, after)
        else:
            if not self.create(before):
                return False  # I will raise an error here later but for now it is fine
            else:
                if self.exists(after):
                    return self._update(before, after) #Why do I double check? because I must
                else:
                    return False  # I will raise an error here later but for now it is fine

    def delete(self, message: discord.Message, time):
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
                "SELECT content FROM {PRE}_messages WHERE `id`={MID}".format(
                    PRE=self.DB,
                    MID=int(message.id)
                )
            )
            data = json.loads(results[0])
            json_react = MessageParser.MessageDelete(data, time)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `content`='{VAL}' WHERE `id`={MID};".format(
                    PRE=self.DB,
                    VAL=str(json_react).replace("'", '"').replace("None", "null"),
                    MID=int(message.id)
                )
            )
        else:
            return False # I will raise an error here later but for now it is fine

    def addReaction(self, reaction: discord.Reaction, user):
        """Called when a reaction is added

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""
        if self.exists(reaction.message):
            results = self.DBC.queryAll(
                "SELECT reactions FROM {PRE}_messages WHERE `id`='{MID}'".format(
                    PRE=self.DB,
                    MID=int(reaction.message.id)
                )
            )
            print(results[0][0])
            data = json.loads(results[0][0])
            print(data)
            json_react = MessageParser.ReactionDB(reaction, data, user)
            print(Parser.jsonToDB(json_react))
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `reactions`='{VAL}' WHERE `id`={MID};".format(
                    PRE=self.DB,
                    VAL=str(json_react),
                    MID=int(reaction.message.id)
                )
            )
        else:
            return False

    def deleteReaction(self, reaction: discord.Reaction, user):
        """Called when a reaction is deleted

        .. note::
            TODO

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""
        return

    def clearReaction(self, message: discord.Message, reactions):
        """Called when all reaction on a message is deleted

        .. note::
            TODO

        Parameters
        ----------
        message: discord.Message
            The reaction
        reactions: list[discord.Reaction]
            The User"""
        return

    def fetch(self, *, Query):
        """Fetches data from DB.

        .. note::
            TODO

        Parameters
        ----------
        Query: str
            Honestly I don't know"""
        pass

class ServerDB():
    """Server Databases, contains details for all the channels and config

    Parameters
    ----------
    DBC: DBC
        This is the DBC(DataBase Connection) that the bot uses
    DB: str
        This is the table prefix to denote whether we are running in dev mode or not!"""

    createServerDBIfNot = cTableIfNot+" {PRE}_servers ("+cID+", "+cName+", "+cMembers+", "+cConfig+", "+cRoles+", "+cEmojis+", "+cAfkTimeout+", "+cRegion+", "+cAfkChannel+", "+cChannels+", "+cIconUrl+", "+cOwner+", "+cStatus+", "+cLarge+", "+cMFA+", "+cVerficationLevel+", "+cDRole+", "+cSlpash+", "+cSize+", "+cDChannel+", "+cCreatedAt+", "+PKID+");"

    createServer = "INSERT INTO {PRE}_servers(`id`, `name`, `members`, `config`, `roles`, `emojis`, `afk_timeout`, `region`, `afk_channel`, `channels`, `icon_url`, `owner`, `status`, `large`, `mfa`, `verfication_level`, `default_role`, `splash`, `size`, `default_channel`, `created_at`) VALUES({SID}, '{NAM}', '{MEM}', '{CON}', '{ROL}', '{EMO}', '{AFT}', '{REG}', '{AFC}', '{CHA}', '{ICO}', '{OWN}', '{STS}', '{LAR}', '{MFA}', '{VLV}', '{DRL}', '{SPL}', '{SIZ}', '{DCH}', '{CAT}');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def createTable(self):
        """Creates the ``prefix_servers`` table"""
        return self.DBC.query(
            self.createServerDBIfNot.format(
                PRE=self.DB
            )
        )

    def exists(self, server: discord.Server):
        """Check if a server exists in the databaes

        Parameters
        ----------
        server: discord.Server
            The Server"""
        return self.DBC.queryOne("SELECT * FROM {PRE}_servers WHERE `id`={SID};".format(
            PRE=self.DB,
            SID=server.id
        )) == 0

    def existsRole(self, role: discord.Role):
        """Checks if the role exists in the server

        Parameters
        ----------
        role: discord.Role
            The Role to be added"""
        return self.DBC.queryOne("SELECT roles FROM {PRE}_servers WHERE `id`={SID};".format(
            PRE=self.DB,
            SID=server.id
        )) == 0
    def existsChannel(self, channel: discord.Channel):
        """Checks if the channel exists in the server

        Parameters
        ----------
        channel: discord.Channel"""
        return self.DBC.queryOne("SELECT * FROM {PRE}_servers WHERE `id`={SID};".format(
            PRE=self.DB,
            SID=server.id
        )) == 0
    def create(self, server: discord.Server):
        """Adds a server to the table

        Parameters
        ----------
        server: discord.Server
            The Server to be created"""
        self.createTable()
        if self.exists(server):
            return False
        members = json.dumps(MemberParser.ServerMembers(server.members)).replace("'", '"')
        roles = json.dumps(RoleParser.ServerRoles(server.roles)).replace("'", '"')
        emojis = json.dumps(EmojiParser.ServerEmojis(server.emojis)).replace("'", '"')
        channels = json.dumps(ChannelParser.ServerChannels(server.channels)).replace("'", '"')
        config = {

        }
        return self.DBC.query(
            self.createServer.format(
                PRE = self.DB,
                SID = int(server.id),
                NAM = server.name,
                MEM = members,
                CON = config,
                ROL = roles,
                EMO = emojis,
                AFT = server.afk_timeout,
                REG = ServerParser.getRegion(server.region),
                AFC = server.afk_channel.id if server.afk_channel is not None else "",
                CHA = channels,
                ICO = server.icon_url if server.icon_url is not None else "",
                OWN = server.owner.id,
                STS = int(not server.unavailable),
                LAR = int(server.large),
                MFA = server.mfa_level,
                VLV = ServerParser.getVLV(server.verification_level),
                DRL = server.default_role.id,
                SPL = server.splash,
                SIZ = server.member_count,
                DCH = server.default_channel.id,
                CAT = server.created_at
            ).replace("None", "null").replace("True", "true").replace("False", "false")
        )

    def createRole(self, role: discord.Role):
        """Add a role

        Parameters
        ----------
        role: discord.Role
            The Role"""
        pass
    def createChannel(self, channel: discord.Channel):
        """Add a channel

        Parameters
        ----------
        channel: discord.Channel
            The channel to be added"""
        pass
    def createEmoji(self, emoji: discord.Emoji):
        """Add a emoji

        Parameters
        ----------
        emoji: discord.Emoji
            The New Emoji"""
        pass

    def createMember(self, member: discord.Member):
        """Called when a server is joined

        Parameters
        ----------
        member: discord.Member
            The Member that was added"""
        server = member.server
        if not self.exists(server):
            return self.create(server)
        pass
    def _update(self, before: discord.Server, after: discord.Server):
        if not self.exists(before):
            self.create(before)
        else:
            pass

    def update(self, before: discord.Server, after: discord.Server):
        """Update a server

        Parameters
        ----------
        before: discord.Server
            The Old Server
        after: discord.Server
            The New Server"""
        self.createTable()
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

    def updateRole(self, role: discord.Role):
        """Update a role

        Parameters
        ----------
        role: discord.Role
            The New Role"""
        pass

    def updateChannel(self, channel: discord.Channel):
        """Update a channel

        Parameters
        ----------
        channel: discord.Channel
            The New Channel"""
        pass

    def updateEmoji(self, emoji: discord.Emoji):
        """Update a emoji

        Parameters
        ----------
        emoji: discord.Emoji
            The New Emoji"""
        pass

    def delete(self, server: discord.Server):
        """Called when a server is deleted or the
        bot is kicked!

        Parameters
        ----------
        server: discord.Server
            The Server That was removed"""
        self.createTable(server)
        return self.DBC.query("DELETE FROM %s_servers WHERE `id`=%s"%(self.DB, int(server.id)))

    def deleteRole(self, role: discord.Role):
        """Removes a role

        Parameters
        ----------
        role: discord.Role
            The Old Role"""
        pass
    def deleteChannel(self, channel: discord.Role):
        """Removes a channel

        Parameters
        ----------
        channel: discord.Channel"""
        pass

    def deleteEmoji(self, emoji: discord.Emoji):
        """Removes an emoji

        Parameters
        ----------
        emoji: discord.Emoji"""
        pass

    def deleteMember(self, member: discord.Member):
        """Called when a member has been removed

        Parameters
        ----------
        member: discord.Member
            The Member that was removed"""
        server = member.server
        if not self.exists(server):
            return self.create(server)
        pass

    def updateStatus(self, server: discord.Server, status):
        """Updates the servers availibility

        Parameters
        ----------
        server: discord.Server
            The Server
        status: int or bool
            Online or Offline/True or False/1 or 0"""
        if isinstance(status, str):
            if status.lower() is "online":
                status = 1
            else:
                status = 0
        self.createTable()
        if not self.exists(server):
            return self.create(server)
        return self.DBC.query(
            "UPDATE `{PRE}_servers` SET `status`='{VAL}' WHERE `id`={SID};".format(
                PRE=self.DB,
                VAL=int(status),
                SID=int(server.id)
            )
        )

class MembersDB():
    """Members Database Class

    Parameters
    ----------
    DBC: DBC
        This is the DBC(DataBase Connection) that the bot uses
    DB: str
        This is the table prefix to denote whether we are running in dev mode or not!"""

    createMemberDBIfNot = cTableIfNot+" {PRE}_users ("+cID+", "+cUserID+", "+cUsername+", "+cDiscriminator+", "+cAvatarUrl+", "+cDUrl+", "+cServers+", "+cStatus+", "+cGame+", "+PKID+");"

    userUpdate = " {PRE}_server(`user_id`, `username`, `discriminator`, `avatar_url`, `default_url`, `servers`, `status`, `game`) VALUES('{UID}', '{USN}', '{DIS}', '{AURL}', '{DURL}', '{SERV}', '{STA}', '{GME}');"

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def createTable(self):
        """Creates the table"""
        return self.DBC.query(
            self.createMemberDBIfNot.format(
                PRE=self.DB
            )
        )

    def exists(self, member: discord.Member):
        """Checks if user exists in the table

        Parameters
        ----------
        user : discord.Member
            The user to be looked up."""
        self.createTable()
        return not self.DBC.queryOne(
            "SELECT * FROM %s_users WHERE user_id = '%s';" % (
                self.DB,
                member.id
            )
        ) == 0

    def create(self, member: discord.Member):
        """Adds a member to the database

        Parameters
        ----------
        member: discord.Member
            The Member"""
        self.createTable()
        if self.exists(member):
            return True
        self.addMember(member)
        pass

    def _update(self, after: discord.Member):
        pass

    def update(self, before: discord.Member, after: discord.Member):
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

    def delete(self, member: discord.Member):
        return

    def ban(self, member: discord.Member):
        return

    def unban(self, server: discord.Server, user: discord.User):
        return

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

    def ban(self, member: discord.Member):
        """Ban a user from a server

        Parameters
        ----------
        member: discord.Member
            Thbe Member that was banned"""
        pass

    def unban(self, server: discord.Server, user: discord.User):
        """Ban a user from a server

        Parameters
        ----------
        server: discord.Server
            The server from which the user was unbanned
        user: discord.User
            The user that was unbanned"""
        pass

class ConfigsDB():
    """Configs Database Class

    Parameters
    ----------
    DBC: DBC
        This is the DBC(DataBase Connection) that the bot uses
    DB: str
        This is the table prefix to denote whether we are running in dev mode or not!"""

    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB

    def getServerConfig(self, server: discord.Server, setting: str):
        """Get Server Config

        Parameters
        ----------
        server: discord.Server

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setServerConfig(self, server: discord.Server, setting: str, value):
        """Set Server Config

        Parameters
        ----------
        server: discord.Server

        setting: str

        value
            """
        pass

    def getServerPermission(self, server: discord.Server, permission: str):
        """Get Server Permission

        Parameters
        ----------
        server: discord.Server

        permission: str
            """
        pass

    def setServerPermission(self, server: discord.Server, permission: str, value):
        """Set Server Permission

        Parameters
        ----------
        server: discord.Server

        permission: str

        value
            """
        pass

    def getChannelConfig(self, server: discord.Channel, setting: str):
        """Get Channel Config

        Parameters
        ----------
        server: discord.Channel

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setChannelConfig(self, server: discord.Channel, setting: str, value):
        """Set Channel Config

        Parameters
        ----------
        server: discord.Channel

        setting: str

        value
            """
        pass

    def getChannelPermission(self, server: discord.Channel, permission: str):
        """Get Channel Permission

        Parameters
        ----------
        server: discord.Channel

        permission: str
            """
        pass

    def setChannelPermission(self, server: discord.Channel, permission: str, value):
        """Set Channel Permission

        Parameters
        ----------
        server: discord.Channel

        permission: str

        value
            """
        pass

    def getMemberConfig(self, server: discord.Member, setting: str):
        """Get Member Config

        Parameters
        ----------
        server: discord.Member

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setMemberConfig(self, server: discord.Member, setting: str, value):
        """Set Member Config

        Parameters
        ----------
        server: discord.Member

        setting: str

        value
            """
        pass

    def getMemberPermission(self, server: discord.Member, permission: str):
        """Get Member Permission

        Parameters
        ----------
        server: discord.Member

        permission: str
            """
        pass

    def setMemberPermission(self, server: discord.Member, permission: str, value):
        """Set Member Permission

        Parameters
        ----------
        server: discord.Member

        permission: str

        value
            """
        pass

def log_ready(bot):
    pass

def log_resumed(bot):
    pass

def log_error(bot, error):
    #if query(createErrorDBIfNot % (bot.currentDB)) == True:
        #print("Creating Table %s_errors" % (bot.currentDB))
    #query(insertErrorLog % (bot.curretDB, error, datetime.datetime.utcnow()))
    pass

#SOMEONE SEND HELP, IM STUCK IN AN LOOP BETWEEN A MAINFRAME AND A POTATO
