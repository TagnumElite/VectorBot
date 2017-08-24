"""
Databases
@author: TagnumElite
"""

from . import checks, parser
from .parser import Parser, MemberParser, MessageParser, GuildParser, ConfigParser, ChannelParser, RoleParser, EmojiParser
from _mysql_exceptions import OperationalError
import warnings, functools
import discord
import MySQLdb
from MySQLdb import MySQLError
import json
import asyncio # I plan to make all the functions async for expanded functionallity later
import datetime

getTable = "SELECT * FROM"
PKID = "primary key(id)"
iInto = "INSERT INTO"
cTableIfNot = "CREATE TABLE IF NOT EXISTS"
cID = "`id` INT NOT NULL AUTO_INCREMENT"
cGuildID = "`guild_id` VARCHAR(100) NOT NULL"
cMessageID = "`message_id` VARCHAR(100) NOT NULL"
cAuthorID = "`author_id` VARCHAR(100) NOT NULL"
cUserID = "`user_id` VARCHAR(100) NOT NULL"
cGuildChannelID = "`channel_id` VARCHAR(100) NOT NULL"
cOwnerID = "`owner_id` VARCHAR(100) NOT NULL"
cCreatedAt = "`created_at` DATETIME NOT NULL"
cError = "`error` VARCHAR(3000) NOT NULL"
cDiscriminator = "`discriminator` INT NOT NULL"
cKey = "`key` VARCHAR(100) NOT NULL"
cValue = '`value` VARCHAR(10000) NOT NULL'

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
        Default to `localhost`. Only use this if the database is on a different guild!
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
        self.buffer = []
        self._connect()

    def _connect(self):
        if self.Connecting:
            print("_connect connecting: ", self.Connecting)
            return
        else:
            self.Connecting = True
            print("_connect connect: ", self.Connecting)
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
                            print("_connect failed: ", self.Connecting)
                            self.Connecting = False
                            raise(E)
                    else:
                        self.Connecting = False
                        print("_connect success: ", self.Connecting)
                        break
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
                            print("_connect failed: ", self.Connecting)
                            self.Conntection = False
                            raise(E)

        self.Cursor = self.Connection.cursor()
        self.queryOne("SET SQL_SAFE_UPDATES = 0;")

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

    def _query(self, query, results=None):
        print("_query start: ", self.Connecting)
        while self.Connecting:
            pass

        self.Connecting = True
        print("_query connect: ", self.Connecting)

        if len(query) == 1:
            query = query[0]
        else:
            query = " ".join(query)

        try:
            print("Query: ", query)
            self.Cursor.execute(query)
            if results is 1:
                result = self.Cursor.fetchone()
            elif results is True:
                result = self.Cursor.fetchall()
            self.Connection.commit()
        except MySQLError as me:
            print("Exception Args", me.args)
            if me.args[0] in [2006, 2013]:
                print("_query could not connect: ", self.Connecting)
                self.Connecting = False
                try:
                    self.reconnect()
                except Exception as E:
                    raise(E)
                else:
                    if results is 1:
                        return self.queryOne(query)
                    elif results is True:
                        return self.queryAll(query)
                    else:
                        return self.query(query)
            else:
                print("Query Exception: {}".format(me))
                self.Buffer.append(query)
                self.Connection.rollback()
                self.Connecting = False
                print("Connecting:", self.Connecting)
                raise me
        except Exception as E:
            print("Query Exception: {}".format(E))
            self.Buffer.append(query)
            self.Connection.rollback()
            self.Connecting = False
            raise E
        else:
            self.Connecting = False
            print("_query finish: ", not self.Connecting)
            if results is not None:
                return result
            else:
                return True

    def query(self, *query):
        """Make an query but doesn't return anything

        Parameters
        ----------
        query: str
            The MySQL query you want to make, a list for multiple queries"""

        return self._query(query, results=1)

    def queryOne(self, *query):
        """Make an query and returns the first result

        Parameters
        ----------
        query: str
            The MySQL query you want to make, a list for multiple queries"""

        return self._query(query, results=1)

    def queryAll(self, *query):
        """Make an query and returns all results

        Parameters
        ----------
        query: str/list
            The MySQL query you want to make, a list for multiple queries"""

        return self._query(query, results=True)


class DB():
    """Base DB Class

    Parameters
    ----------
    DBC: DBC
        The Database Connection
    DB: str
        The table prefix"""

    #: Override, tables main name
    table = "main"
    #: Override, The main table to be created!
    createDataTable = cTableIfNot
    #: Override, The meta table to be created!
    createMetaTable = cTableIfNot
    #: Override
    insertData = iInto
    #: Override
    insertMeta = iInto
    #: Override
    insertMetaV = iInto
    #: Override
    insertMetaW = iInto
    #: Override
    selectValue = "SELECT value FROM {PRE}_{TABLE}s_meta WHERE `{TAB}_id`='{MID}' AND `key`='{KEY}';"


    def __init__(self, DBC, DB):
        self.DBC = DBC
        self.DB = DB.lower()
        self.createTables()
        # Setup Parsers
        self.P = Parser()
        self.MP = MessageParser()
        self.MBP = MemberParser()
        self.SP = GuildParser()
        self.CFP = ConfigParser()
        self.CP = ChannelParser()
        self.RP = RoleParser()
        self.EP = EmojiParser()

    def createTables(self):
        """Creates the tables"""

        self.DBC.query(
            self.createDataTable.format(PRE=self.DB)
        )
        self.DBC.query(
            self.createMetaTable.format(PRE=self.DB)
        )

    def exists(self, item):
        """Checks if the item exists

        Parameters
        ----------
        message: discord.Object
            The object to be checked if it exists"""

        result = self.DBC.queryOne(
            "SELECT * FROM {PRE}_{TAB}s WHERE `{TAB}_id`={MID};".format(
                PRE=self.DB,
                TAB=self.table.lower(),
                MID=item.id
            )
        )
        if not result:
            return False
        else:
            return True


    def _update(self, before, after):
        """OVERWRITE

        Parameters
        ----------
        before
            The object before the update
        after
            The updated object"""
        pass

    def update(self, before, after):
        """Update an object

        Parameters
        ----------
        before
            The object before the change
        after
            The object after the change"""

        if self.exists(after):
            return self._update(before, after)
        else:
            if not self.create(before):
                raise DBError.CouldNotCreate("Object could not be created!")
            else:
                if self.exists(after):
                    return self._update(before, after) #Why do I double check? because I must
                else:
                    raise DBError.DoesNotExist("Object Doesn't Exists!")

class MessageDB(DB):
    """Message Database!

    Parameters
    ----------
    DBC: DBC
        The SQL Connection
    DB: str
        The Table Prefix"""

    table = "message"

    createDataTable = cTableIfNot+" {PRE}_messages ("+cID+", "+cMessageID+" UNIQUE, "+cGuildID+", "+cGuildChannelID+", "+cAuthorID+", "+cCreatedAt+", "+PKID+");"

    createMetaTable = cTableIfNot+" {PRE}_messages_meta ("+cID+", "+cMessageID+", "+cKey+", "+cValue+", "+PKID+");"

    insertMessageData = iInto+" {PRE}_messages (`message_id`, `guild_id`, `channel_id`, `author_id`, `created_at`) VALUES ('{MID}', '{SID}', '{CID}', '{AID}', '{CAT}');"

    insertMessageMeta = iInto+" {PRE}_messages_meta (`message_id`, `key`, `value`) VALUES ('{MID}', '{KEY}', '{VAL}');"

    insertMessageMetaV = iInto+" {PRE}_messages_meta (`message_id`, `key`, `value`) VALUES {VALUES};"

    insertMessageMetaW = iInto+" {PRE}_messages_meta (`message_id`, `key`, `value`) VALUES ('{MID}', '{KEY}', '{VAL}') WHERE {WHERE};"

    selectMessageValue = "SELECT value FROM {PRE}_messages_meta WHERE `message_id`='{MID}' AND `key`='{KEY}';"
    print("Data Table:", createDataTable)

    def create(self, message: discord.Message):
        """Create a entry to the SQL of an message

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""

        print("Creating Message")
        if self.exists(message):  # Raise an error if the message already exists
            print("Message Exists")
            #raise DBError.Exists("Message Already Exists")
            return False
        msg = "{}"
        if message.type == discord.MessageType.default: #Check if the message is a normal message
            print("Message Type: Message")
            msg = self.MP.Parse(message.content)
            msg = '{"content":[{"content":"'+msg+'", "timestamp":"'+str(message.timestamp.utcnow())+'"}]}'
        elif message.type == discord.MessageType.pins_add:
            print("Message Type: Pin")
            msg = '{"content":[{"content":"{author} pinned a message to this channel.", "timestamp":"{timestamp}"}]}'.format(
                author=message.author.name,
                timestamp=str(message.timestamp.utcnow())
            )
        else:
            print("Message Type: Unknown")
            #raise DBError.UnknownType("Unknown message type: {}".format(message.type.__name__))
            return False
        try:
            self.DBC.query(
                self.insertMessageData.format(
                    PRE=self.DB,
                    MID=message.id,
                    SID=message.guild.id,
                    CID=message.channel.id,
                    AID=message.author.id,
                    CAT=message.timestamp
                )
            )
        except Exception as e:
            raise e

        try:
            self.DBC.query(
                self.insertMessageMetaV.format(
                    PRE=self.DB,
                    VALUES="""('{MID}', 'content', '{CON}'),
                    ('{MID}', 'mentions', '{MENS}'),
                    ('{MID}', 'attachments', '{ATTCHS}')""".format(
                        MID=message.id,
                        CON=msg,
                        MENS=str(self.MP.MessageMentions(message)).replace("'", "\""),
                        ATTCHS=json.dumps(message.attachments[0]).replace("'", "\\\"") if len(message.attachments) >= 1 else "{}"
                    )
                )
            )
        except Exception as E:
            raise E

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
                "SELECT value FROM {PRE}_messages_meta WHERE `message_id`={MID} AND `key`='{UP}';".format(
                    PRE=self.DB,
                    MID=after.id,
                    UP=updates[0]
                )
            )
            search = updates[0]
            if search is 'content':
                json_data = json.loads(results[0])
            elif search is 'pinned':
                return self.DBC.query(
                    "INSERT INTO {PRE}_messages_meta (message_id, key, value) VALUES('{MID}', '{KEY}', '{VAL}') ON DUPLICATE KEY UPDATE value='{VAL}';".format(
                        PRE=self.DB,
                        PIN=str(after.pinned),
                        MID=after.id
                    )
                )
            json_update = self.MP.MessageUpdate(after, json_data, updates)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET `{KEY}`='{VAL}' WHERE `message_id`='{MID}';".format(
                    PRE=self.DB,
                    KEY=search,
                    VAL=self.MP.Parse(str(json_update).replace("'", '"')),
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
                "SELECT {KEY} FROM {PRE}_messages WHERE `message_id`='{MID}'".format(
                    KEY=search,
                    PRE=self.DB,
                    MID=after.id
                )
            )
            string_data = self.MP.MessageUpdate(after, results, updates)
            return self.DBC.query(
                "UPDATE `{PRE}_messages` SET {DATA} WHERE `message_id`='{MID}';".format(
                    PRE=self.DB,
                    DATA=string_data,
                    MID=after.id
                )
            )

    def delete(self, message: discord.Message, time):
        """Called when a message is deleted.

        Parameters
        ----------
        message: discord.Message
            The discord message that was deleted
        time: datetime.datetime.utcnow()
            UTC Time when message was deleted"""

        if self.exists(message):
            results = self.DBC.queryOne(
                "SELECT value FROM {PRE}_messages_meta WHERE `message_id`='{MID}' AND `key`='content'".format(
                    PRE=self.DB,
                    MID=message.id
                )
            )
            data = json.loads(results[0])
            json_data = self.MP.MessageDelete(data, time)
            try:
                self.DBC.query(
                    "UPDATE `{PRE}_messages_meta` SET `value`='{VAL}' WHERE `message_id`='{MID}' AND `key`='content';".format(
                        PRE=self.DB,
                        VAL=str(json_data).replace("'", '"').replace("None", "null"),
                        MID=message.id
                    )
                )
            except Exception as E:
                raise E
        else:
            #raise DBError.DoesNotExists("Message doesn't exists")
            return False

    def addReaction(self, reaction: discord.Reaction, user):
        """Called when a reaction is added

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""

        if self.exists(reaction.message):
            results = self.DBC.queryOne(
                self.selectMessageValue.format(
                    PRE=self.DB,
                    MID=reaction.message.id,
                    KEY='reactions'
                )
            )
            if results:
                print(results[0])
                data = json.loads(results[0])
                print(data)
                return self.DBC.query(
                    "UPDATE `{PRE}_messages_meta` SET `value`='{VAL}' WHERE `message_id`='{MID}' AND `key`='reactions';".format(
                        PRE=self.DB,
                        VAL=self.MP.AddReaction(reaction, user, data).replace("'", '"'),
                        MID=reaction.message.id
                    )
                )
            else:
                self.DBC.query(
                    self.insertMessageMeta.format(
                        PRE=self.DB,
                        MID=reaction.message.id,
                        KEY='reactions',
                        VAL=self.MP.AddReaction(reaction, user).replace("'", '"')
                    )
                )
        else:
            #raise DBError.DoesNotExists("Message doesn't exists")
            return False

    def deleteReaction(self, reaction: discord.Reaction, user):
        """Called when a reaction is deleted

        Parameters
        ----------
        reaction: discord.Reaction
            The reaction
        user: discord.User
            The User"""

        if self.exists(reaction.message):
            results = self.DBC.queryOne(
                self.selectMessageValue.format(
                    PRE=self.DB,
                    MID=reaction.message.id,
                    KEY='reactions'
                )
            )
            if results:
                print(results[0])
                data = json.loads(results[0])
                print(data)
                return self.DBC.query(
                    "UPDATE `{PRE}_messages_meta` SET `value`='{VAL}' WHERE `message_id`='{MID}' AND `key`='reactions';".format(
                        PRE=self.DB,
                        VAL=self.MP.RemoveReaction(reaction, user, data).replace("'", '"'),
                        MID=reaction.message.id
                    )
                )
            else:
                #raise DBError.DoesNotExist("Reactions dont exists for this message")
                return False
        else:
            #raise DBError.DoesNotExists("Message doesn't exists")
            return False

    def clearReactions(self, message: discord.Message):
        """Called when all reactions on a message is deleted

        Parameters
        ----------
        message: discord.Message
            The message that had all the reactions cleared"""

        if self.exists(message):
            if not self.DBC.queryOne(
                "SELECT value FROM {PRE}_messages_meta WHERE `message_id`={MID} AND `key`='reactions';".format(
                    PRE=self.DB,
                    MID=message.id
                )
            ):
                return True
            else:
                return self.DBC.query(
                    "UPDATE `{PRE}_messages_meta` SET `value`='{}' WHERE `message_id`={MID} AND `key`='reactions';".format(
                        PRE=self.DB,
                        MID=message.id
                    )
                )
        else:
            #raise DBError.DoesNotExists("Message doesn't exists")
            return False

class GuildDB(DB):
    """Guild Databases, contains details for all the channels and config

    Parameters
    ----------
    DBC: DBC
        This is the DBC(DataBase Connection) that the bot uses
    DB: str
        This is the table prefix to denote whether we are running in dev mode or not!"""

    table = "guild"

    createDataTable = cTableIfNot+" {PRE}_guilds ("+cID+", "+cGuildID+" UNIQUE, "+cOwnerID+", "+cCreatedAt+", "+PKID+");"

    createMetaTable = cTableIfNot+" {PRE}_guilds_meta ("+cID+", "+cGuildID+", "+cKey+", "+cValue+", "+PKID+");"

    insertGuildData = iInto+" {PRE}_guilds (`guild_id`, `owner_id`, `created_at`) VALUES('{SID}', '{OID}', '{CAT}')"

    def __update(self, before, after):
        """Updates data inside the guild

        Used to update or add data

        Parameters
        ----------
        data: [discord.Role, discord:Member, discord.abc.GuildChannel, discord.Emoji]
            The new data"""

        key = ""
        CurrentParser = self.P

        if isinstance(data, discord.Role):
            key = "roles"
            CurrentParser = self.RP
        elif isinstance(data, discord.abc.GuildChannel):
            key = "channels"
            CurrentParser = self.CP
        elif isinstance(data, discord.Emoji):
            key = "emojis"
            CurrentParser = self.EP
        elif isinstance(data, discord.Member):
            key = "members"
            CurrentParser = self.MBP
        else:
            raise Exception("You failed to provide the appropiate data")

        results = self.DBC.queryOne("SELECT {KEY} FROM {PRE}_guilds WHERE `id`={SID};".format(
            KEY=key,
            PRE=self.DB,
            SID=data.guild.id
        ))
        data_dict = json.loads(results[0])
        if data.id in data_dict:
            data_dict[data.id] = CurrentParser.Guild(data)[data.id]
            return self.DBC.query(
                "UPDATE `{PRE}_guilds` SET `{KEY}`='{DATA}' WHERE `id`={SID};".format(
                    KEY=key,
                    PRE=self.DB,
                    DATA=str(json.dumps(data_dict)).replace(
                        "None", "null"
                    ).replace(
                        "False", "false"
                    ).replace(
                        "'", '"'
                    ),
                    SID=data.guild.id
                )
            )
        else:
            data_dict[role.id] = CurrentParser.Guild(data)[data.id]
            return self.DBC.query(
                "UPDATE `{PRE}_guilds` SET `{KEY}`='{DATA}' WHERE `id`={SID};".format(
                    KEY=key,
                    PRE=self.DB,
                    DATA=str(json.dumps(data_dict)).replace(
                        "None", "null"
                    ).replace(
                        "False", "false"
                    ).replace(
                        "'", '"'
                    ),
                    SID=data.guild.id
                )
            )

    def update(self, before, after):
        """"""
        pass
    def exists(self, obj):
        """Check if the object exists in the guild database

        Parameters
        ----------
        guild: discord.Object
            The Guild"""

        results = self.DBC.queryOne("SELECT * FROM {PRE}_guilds WHERE `id`={SID};".format(
            PRE=self.DB,
            SID=int(guild.id)
        ))
        if not results:
            return False
        else:
            return True

    def create(self, obj):
        """Adds the object to the guild database

        Parameters
        ----------
        guild: discord.Object
            The Object to be created"""

        if self.exists(obj): return False;

        if isinstance(obj, discord.Guild):
            members = json.dumps(self.MBP.Guilds(guild.members)).replace("'", '"')
            roles = json.dumps(self.RP.Guilds(guild.roles)).replace("'", '"')
            emojis = json.dumps(self.EP.Guilds(guild.emojis)).replace("'", '"')
            channels = json.dumps(self.CP.Guilds(guild.channels)).replace("'", '"')
            config = {

            }
            try:
                self.DBC.query(
                    self.insertGuildData.format(
                        PRE = self.DB,
                        SID = guild.id,
                        OWN = guild.owner.id,
                        CAT = guild.created_at
                    )
                )
            except:
                return False
        elif isinstance(obj, discord.Member):
            return
        elif isinstance(obj, discord.abc.GuildChannel):
            return
        elif isinstance(obj, list):
            """Check for difference in emojis"""
            return
        else:
            return False

    def delete(self, obj):
        """Remove the object from the guild database

        Parameters
        ----------
        guild: discord.Object
            The Object That was removed"""

        if isinstance(obj, discord.Guild):
            return self.DBC.query("DELETE FROM %s_guilds WHERE `id`=%s"%(self.DB, int(guild.id)))
        elif isinstance(obj, discord.Member):
            return False
        elif isinstance(obj, discord.Role):
            return False
        elif isinstance(obj, discord.abc.GuildChannel):
            return False
        elif isinstance(obj, discord.Emoji):
            return False
        else:
            return False

class UserDB(DB):
    """Members Database Class

    Parameters
    ----------
    DBC: DBC
        This is the DBC(DataBase Connection) that the bot uses
    DB: str
        This is the table prefix to denote whether we are running in dev mode or not!"""

    table = "member"

    createDataTable = cTableIfNot+" {PRE}_members ("+cID+", "+cUserID+" UNIQUE, "+cGuildID+", "+cCreatedAt+", "+PKID+");"

    createMetaTable = cTableIfNot+" {PRE}_guilds_meta ("+cID+", "+cUserID+", "+cKey+", "+cValue+", "+PKID+");"

    createMember = "INSERT INTO {PRE}_members(`id`, `username`, `discriminator`, `avatar_url`, `default_url`, `guilds`, `status`, `game`, `guilds`, `confs`, `created_at`) VALUES({MID}, '{MUN}', {DIS}, '{ARL}', '{DRL}', '{STS}', '{GME}', '{SVR}', '{CON}', '{CAT}');"

    def exists(self, user):
        """Checks if user/member exists in the table

        Parameters
        ----------
        user : [int, discord.User, discord.Member]
            If int or discord.User then searches for that user in general
            but if discord.Member then checks if that member exists in the database"""

        results = False

        if isinstance(user, int):
            results = self.DBC.queryOne(
                "SELECT * FROM {PRE}_members WHERE `id` = {MID};".format(
                    PRE=self.DB,
                    MID=user
                )
            )
        elif isinstance(user, discord.User):
            results = self.DBC.queryOne(
                "SELECT * FROM {PRE}_members WHERE `id` = {MID};".format(
                    PRE=self.DB,
                    MID=int(user.id)
                )
            )
        elif isinstance(user, discord.Member):
            results = self.DBC.queryOne(
                "SELECT `guilds` FROM {PRE}_members WHERE `id` = {MID};".format(
                    PRE=self.DB,
                    MID=int(user.id)
                )
            )
            data = json.loads(results[0])
            results = member.guild.id in data

        else:
            raise Exception("Incorrect Data Type")

        if not results:
            return False
        else:
            return True

    def create(self, member: discord.Member):
        """Adds a member to the database

        Parameters
        ----------
        member: discord.Member
            The Member to be added"""
        if self.exists(member):
            return True
        return self.DBC.query(self.createMember.format(
            PRE=self.DB,
            MID=member.id,
            MUN=member.name,
            DIS=member.discriminator,
            ARL=member.avatar_url,
            DRL=member.default_avatar_url,
            STS=self.MBP.getStatus(member.status),
            GME=self.MBP.getGame(member.game),
            SVR='null',  #NOTE: Remember to find a good way to go through all the guilds in the mysql database to find all the guilds this person is in and get the configs from that
            CON='{}',
            CAT=member.created_at
        ))

    def _update(self, before: discord.Member, after: discord.Member):
        pass

    def update(self, before: discord.Member, after: discord.Member):
        """Update a Member

        Parameters
        ----------
        before : discord.Member
            The Discord Member before the update.
        after : discord.Member
            The Discord Member after the update."""

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
        """This deletes a member from the database

        Parameters
        ----------
        member: discord.Member
            The member you want removed"""
        pass

    def ban(self, member: discord.Member):
        """Ban a user from a guild

        .. note::
            Bans will overwrite the full ``guilds`` to replace the
            current guilds data with {"banned": true}

        Parameters
        ----------
        member: discord.Member
            Thbe Member that was banned"""
        pass

    def unban(self, guild: discord.Guild, user: discord.User):
        """Unban a user from a guild

        .. note::
            Bans will overwrite the full ``guilds`` to remove the
            current guilds data!

        Parameters
        ----------
        guild: discord.Guild
            The guild from which the user was unbanned
        user: discord.User
            The user that was unbanned"""
        pass

class TeamDB(DB):
    """Team Database!

    Parameters
    ----------
    DBC: DBC
        The SQL Connection
    DB: str
        The Table Prefix"""

    createDataTable = cTableIfNot+" {PRE}_teams ("+cID+", "+PKID+");"

    createMetaTable = cTableIfNot+" {PRE}_teams ("+cID+", "+PKID+");"

    createTeamMetaTable = cTableIfNot+" {PRE}_messages ("+cID+""",
    """+cKey+", "+cValue+", "+PKID+");"
    def createTable(self):
        """Used to create the table"""
        self.DBC.query(
            self.createTeamTable.format(PRE=self.DB),
            self.createTeamMetaTable.format(PRE=self.DB)
        )

    def exists(self, team):
        """Checks if the message exists

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        pass

    def create(self, team):
        """Create a entry to the SQL of an message

        Parameters
        ----------
        message: discord.Message
            The message that was sent"""
        pass

    def update(self, before, after):
        """Update a message

        Parameters
        ----------
        before: discord.Message
        after: discord.Message"""
        pass

    def delete(self, team, time):
        """Called when a message is deleted.

        Parameters
        ----------
        message: discord.Message
            The discord message that was deleted
        time: datetime.datetime.utcnow()
            UTC Time when message was deleted"""
        pass

class ConfigDB(DB):
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

    def getGuildConfig(self, guild: discord.Guild, setting: str):
        """Get Guild Config

        Parameters
        ----------
        guild: discord.Guild

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setGuildConfig(self, guild: discord.Guild, setting: str, value):
        """Set Guild Config

        Parameters
        ----------
        guild: discord.Guild

        setting: str

        value
            """
        pass

    def getGuildPermission(self, guild: discord.Guild, permission: str):
        """Get Guild Permission

        Parameters
        ----------
        guild: discord.Guild

        permission: str
            """
        pass

    def setGuildPermission(self, guild: discord.Guild, permission: str, value):
        """Set Guild Permission

        Parameters
        ----------
        guild: discord.Guild

        permission: str

        value
            """
        pass

    def getChannelConfig(self, guild: discord.abc.GuildChannel, setting: str):
        """Get Channel Config

        Parameters
        ----------
        guild: discord.abc.GuildChannel

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setChannelConfig(self, guild: discord.abc.GuildChannel, setting: str, value):
        """Set Channel Config

        Parameters
        ----------
        guild: discord.abc.GuildChannel

        setting: str

        value
            """
        pass

    def getChannelPermission(self, guild: discord.abc.GuildChannel, permission: str):
        """Get Channel Permission

        Parameters
        ----------
        guild: discord.abc.GuildChannel

        permission: str
            """
        pass

    def setChannelPermission(self, guild: discord.abc.GuildChannel, permission: str, value):
        """Set Channel Permission

        Parameters
        ----------
        guild: discord.abc.GuildChannel

        permission: str

        value
            """
        pass

    def getMemberConfig(self, guild: discord.Member, setting: str):
        """Get Member Config

        Parameters
        ----------
        guild: discord.Member

        setting: str
            """
        if self.DBC.query("NOT EXISTS"):
            return

    def setMemberConfig(self, guild: discord.Member, setting: str, value):
        """Set Member Config

        Parameters
        ----------
        guild: discord.Member

        setting: str

        value
            """
        pass

    def getMemberPermission(self, guild: discord.Member, permission: str):
        """Get Member Permission

        Parameters
        ----------
        guild: discord.Member

        permission: str
            """
        pass

    def setMemberPermission(self, guild: discord.Member, permission: str, value):
        """Set Member Permission

        Parameters
        ----------
        guild: discord.Member

        permission: str

        value
            """
        pass
