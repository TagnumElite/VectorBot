"""
Because JSON
@author: TagnumElite
"""

import json
import discord


class Parser():
    """A Normal Parser

    I have to put something here later but I forgot what!"""

    def jsonToDB(self, to: dict):
        """I don't remember what this was for....
        but is esentially just ``json.dumps(to)``

        Parameters
        ----------
        to: dict
            Turns the dict into a string"""
        return json.dumps(to)

class MemberParser(Parser):
    """Member Parser: Parser

    This a parser mostly for discord.Member related things"""

    def getStatus(self, status):
        """Gets a string from the status.

        Parameters
        ---------
        status: str or discord.Status
            If a string is put in it will return the string."""
        if isinstance(status, str):
            return status
        else:
            if status is discord.Status.online:
                return "Online"
            elif status is discord.Status.offline:
                return "Offline"
            elif status is discord.Status.idle:
                return "IDLE"
            elif status is discord.Status.dnd:
                return "DND"
            elif status is discord.Status.do_not_disturb:
                return "Do Not Disturb"
            elif status is discord.Status.invisible:
                return "Invisible"
            else:
                return "Error"


    def Server(self, member: discord.Member):
        """Returns a dict with the member's details

        Parameters
        ----------
        member: discord.Member"""
        data = {}
        data[member.id] = {
            "nick": member.nick,
            "roles": [None],
            "joined_at": str(member.joined_at),
            "status": self.getStatus(member.status),
            "top_role": member.top_role.id,
            "perms": {},  # Usage explained in RTD FAQ!
            "confs": {}  # Explained in RTD FAQ!
        }
        data[member.id]["roles"] = []
        for role in member.roles:
            data[member.id]["roles"].append(role.id)
        return data

    def Servers(self, members):
        """Returns a dict with the members and their details

        Parameters
        ----------
        members: list[discord.Member]"""
        data = {}
        for member in members:
            data[member.id] = self.Server(member)[member.id]
        return data

class MessageParser(Parser):
    """Message Parser: Parser

    This a parser mostly for discord.Message related things"""

    def MessageDBReplace(self, content):
        """Replaces the contents ``\`` ``"`` ``'`` to something more
        understandable by MySQL"""
        content.replace("\\", "\\\\\\\\")  # This should work but because of reasons I don't know why it doesn't so if you know how to fix this please!
        content.replace('\'', '\\\'')
        content.replace("\"", "\\\"")
        return content

    def MessageReactions(self, reactions):
        """Turns reactions on a message to MySQL readable json

        Parameters
        ----------
        reactions: list[discord.Reaction]
            An iterable of reactions that get converted into json data"""
        json_data = {'reactions':[]}
        for idx, value in enumerate(reactions):
            data = {"emoji":reactions.emoji.id, "custom":int(reactions.custom_emoji), "count":str(reactions.count)}
            json_data['reaction'].append(data)

    def ReactionDB(self, reaction: discord.Reaction, results: dict, user=None, add: bool=True):
        """If no user is added it automatically assumes the reactions were cleared even if add bool is parsed.
        If add is false will remove reaction and reaction doesn't exists returns orginal results

        Parameters
        ----------
        reaction: discord.Reaction
            Reaction
        results: dict

        user: discord.User/Member
            Default: None
        add: bool
            Default: True."""
        exists = False
        if user is not None:
            for key, value in results.items():
                if key == reaction.emoji.name:
                    exists = True
                    for x in value:
                        if x == user.id:
                            return False
                        else:
                            if add:
                                results[key].append(user.id)
                                return results
                            else:
                                index = results[key].index(user.id)
                                del results[key][index]
                                return results
                else:
                    if add:
                        results[reaction.emoji.name] = [user.id]
                        return results
                    else:
                        return results
        else:
            return "{}"

    def MessageMentions(self, message: discord.Message):
        """Converts mentions into a dict

        Parameters
        ----------
        message: discord.Message
            The message that was recieved"""

        users = message.mentions
        channels = message.channel_mentions
        roles = message.role_mentions
        everyone = message.mention_everyone

        data = {
            "everyone": False,
            "users": [],
            "channels": [],
            "roles": []
        }

        data["everyone"] = everyone
        if len(users) > 0:
            for user in users:
                data["users"].append(user.id)
        if len(channels) > 0:
            for channel in channels:
                data["channels"].append(channel.id)
        if len(roles) > 0:
            for role in roles:
                data["roles"].append(role.id)
        return json.dumps(data).replace("True", "true").replace("False", "false")
    def MessageDelete(self, data: dict, time):
        """Appends ``{"content":None, "timestamp":"%s" % (time)}``

        Parameters
        ----------
        data: dict
            The current existing data
        time: datetime or str
            The time of when the message was deleted"""
        return data['content'].append({"content":None, "timestamp":"%s" % (str(time))})

    def MessageUpdate(self, message: discord.Message, results, updates):
        """This updates the message using the originally stored on the Database and
        the new one updated one.

        Parameters
        ---------
        message: discord.Message
            The Message
        results: dict
            Original Data
        updates: list
            The things that were updated"""
        length = len(updates)
        if length == 1:
            if updates[0] == "content":
                print(message.content, str(message.edited_timestamp))
                results['content'].append(
                    {
                        "content":"%s"% (self.MessageDBReplace(message.content)),
                        "timestamp":"%s" % (str(message.edited_timestamp))
                    }
                )
                return results
            elif updates[0] == "pinned":
                return int(message.pinned)
            else:
                return False
        else:
            content = {"content":[]}
            mentions = {}
            attachments = {}
            query = ""
            if 'content' in updates:
                idx = updates.index('content')
                before = json.loads(results[idx])
                before['content'].append({"content":"%s"% (self.MessageDBReplace(message.content)), "timestamp":"%s" % (str(message.edited_timestamp))})
                content = before
            if "content" in updates:
                query = "`content`='%s'" % (str(content).replace("'", "\""))
            if "attachments" in updates:
                if "content" in updates:
                    query += ", `attachments`='%s'"%(str(attachments).replace("'", "\""))
                else:
                    query = "`attachments`='%s'"%(str(attachments).replace("'", "\""))
            if "mentions" in updates:
                if "content" in updates:
                    query += ", `mentions`='%s'"%(str(self.MessageMentions(message)).replace("'", '"'))
                else:
                    query = "`mentions'='%s'"%(str(self.MessageMentions(message)).replace("'", '"'))
            return query

class ServerParser(Parser):
    """Server Parser: Parser

    This a parser mostly for discord.Server related things"""

    def getRegion(self, region):
        """Gets a Verification Level and returns a string.

        Parameters
        ---------
        VerificationLevel: str or discord.VerificationLevel
            If a string is put in it will return the string."""
        if isinstance(region, str):
            return region
        else:
            if region is discord.ServerRegion.us_west:
                return "US West"
            elif region is discord.ServerRegion.us_east:
                return "US East"
            elif region is discord.ServerRegion.us_central:
                return "US Central"
            elif region is discord.ServerRegion.eu_west:
                return "Western Europe"
            elif region is discord.ServerRegion.eu_central:
                return "Central Europe"
            elif region is discord.ServerRegion.singapore:
                return "Singapore"
            elif region is discord.ServerRegion.london:
                return "London"
            elif region is discord.ServerRegion.sydney:
                return "Sydney"
            elif region is discord.ServerRegion.amsterdam:
                return "Amsterdam"
            elif region is discord.ServerRegion.frankfurt:
                return "Frankfurt"
            elif region is discord.ServerRegion.brazil:
                return "Brazil"
            elif region is discord.ServerRegion.vip_us_east:
                return "VIP US East"
            elif region is discord.ServerRegion.vip_us_west:
                return "VIP US West"
            elif region is discord.ServerRegion.vip_amsterdam:
                return "VIP Amsterdam"

    def getVLV(self, VerificationLevel):
        """Gets a Verification Level and returns a string.

        Parameters
        ---------
        VerificationLevel: str or discord.VerificationLevel
            If a string is put in it will return the string."""
        if isinstance(VerificationLevel, str):
            return VerificationLevel
        else:
            if VerificationLevel is discord.VerificationLevel.none:
                return "None"
            elif VerificationLevel is discord.VerificationLevel.low:
                return "Low"
            elif VerificationLevel is discord.VerificationLevel.medium:
                return "Meduim"
            elif VerificationLevel is discord.VerificationLevel.high:
                return "High"
            elif VerificationLevel is discord.VerificationLevel.table_flip:
                return "Table Flip"

    def getUpdates(self, before: discord.Server, after: discord.Server):
        """Returns a list of string with what has changed

        Parameter
        ---------
        before: discord.Server
            Before the updat
        after: discord.Server
            After the update"""
        updates = []
        if before.name is not after.name:
            updates.append("name")
        if before.region is not after.region:
            updates.append("region")
        if before.afk_timeout is not after.afk_timeout:
            updates.append("afk_timeout")
        if before.afk_channel is not after.afk_channel:
            updates.append("afk_channel")
        if before.icon_url is not after.icon_url:
            updates.append("icon")
        if before.owner is not after.owner:
            updates.append("owner")
        if before.large is not after.large:
            updates.append("large")
        if before.mfa_level is not after.mfa_level:
            updates.append("mfa_level")
        if before.verification_level is not after.verification_level:
            updates.append("verification_level")
        if before.splash_url is not after.splash_url:
            updates.append("splash")
        if before.default_role is not after.default_role:
            updates.append("default_role")
        if before.default_channel is not after.default_channel:
            updates.append("default_channel")
        if before.member_count is not after.member_count:
            updates.append("size")
        return updates

    def ServerUpdate(self, server: discord.Server, updates):
        """Returns MySQL syntax friendly string

        Parameters
        ---------
        server: discord.Server
            The New Server
        updates: list
            The things that were updated"""

        query = ""

        if "name" in updates:
            if len(query) is 0:
                query = "`name`='%s'" % (server.name)
            else:
                query += ", `name`='%s'" % (server.name)
        if "region" in updates:
            if len(query) is 0:
                "`region`='%s'" % (self.getRegion(server.region))
            else:
                query += ", `region`='%s'" % (self.getRegion(server.region))
        if "afk_timeout" in updates:
            if len(query) is 0:
                query = "`afk_timeout`=%s" % (server.afk_timeout)
            else:
                query += ", `afk_timeout`=%s" % (server.afk_timeout)
        if "afk_channel" in updates:
            if len(query) is 0:
                query = "`afk_channel`='%s'" % (server.afk_channel.id)
            else:
                query += ", `name`='%s'" % (server.afk_channel.id)
        if "icon" in updates:
            if len(query) is 0:
                query = "`icon_url`='%s'" % (server.icon_url)
            else:
                query += ", `icon_url`='%s'" % (server.icon_url)
        if "owner" in updates:
            if len(query) is 0:
                query = "`owner`='%s'" % (server.owner.id)
            else:
                query += ", `owner`='%s'" % (server.owner.id)
        #if "large" in updates:
        #    if len(query) is 0:
        #        query = "`large`=%s" % (int(server.large))
        #    else:
        #        query += ", `large`=%s" % (int(server.large))
        if "mfa_level" in updates:
            if len(query) is 0:
                query = "`mfa`=%s" % (server.mfa_level)
            else:
                query += ", `mfa`=%s" % (server.mfa_level)
        if "verification_level" in updates:
            if len(query) is 0:
                "`verification_level`='%s'" % (self.getVLV(server.verification_level))
            else:
                query += ", `verification_level`='%s'" % (self.getVLV(server.verification_level))
        if "splash" in updates:
            if len(query) is 0:
                query = "`splash`='%s'" % (server.splash_url)
            else:
                query += ", `splash`='%s'" % (server.splash_url)
        if "default_role" in updates:
            if len(query) is 0:
                query = "`default_role`='%s'" % (server.default_role.id)
            else:
                query += ", `default_role`='%s'" % (server.default_role.id)
        if "default_channel" in updates:
            if len(query) is 0:
                query = "`default_channel`='%s'" % (server.default_channel.id)
            else:
                query += ", `default_channel`='%s'" % (server.default_channel.id)
        if "size" in updates:
            if len(query) is 0:
                query = "`size`=%s" % (server.member_count)
            else:
                query += ", `size`=%s" % (server.member_count)
        return query

class ChannelParser(Parser):
    """Channel Parser: Parser

    This a parser mostly for discord.Channel related things"""

    def getChannelType(self, channelType):
        """Gets a channels type and returns a string.

        Parameters
        ---------
        channelType: str or discord.ChannelType
            If a string is put in it will return the string."""
        if isinstance(channelType, str):
            return channelTyle
        else:
            if channelType is discord.ChannelType.text:
                return "Text"
            elif channelType is discord.ChannelType.voice:
                return "Voice"
            elif channelType is discord.ChannelType.private:
                return "Private"
            elif channelType is discord.ChannelType.group:
                return "Group"

    def Server(self, channel: discord.Channel):
        """Returns a dict that is acceptableish by MySQL and the Server Parser

        Parameters
        ----------
        channel: discord.Channel

        Returns
        -------
        dict
            {"223744046720434176": {"Name": "Staff", "Topic": "", "posititon": 2, "type": "Voice", "bitrate": 64, "connected": 3, "user_limit: 0, "default": False, "timestamp": "16-12-1212 16:20", "perms": {}, "confs": {}}}"""
        data = {}
        data[channel.id] = {
            "name": channel.name,
            "topic": channel.topic if channel.topic is not None else "",
            "position": channel.position,
            "type": self.getChannelType(channel.type),
            "bitrate": channel.bitrate,
            "connected": len(channel.voice_members),
            "user_limit": channel.user_limit,
            "default": channel.is_default,
            "timestamp": str(channel.created_at),
            "perms": {},  # Usage explained in RTD FAQ!
            "confs": {}  # Explained in RTD FAQ!
        }
        return data

    def Servers(self, channels):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        channels: list[discord.Channel]"""
        data = {}
        for channel in channels:
            data[channel.id] = self.Server(channel)[channel.id]
        return data

class RoleParser(Parser):
    """Role Parser: Parser

    This a parser mostly for discord.Role related things"""

    def Server(self, role: discord.Role):
        """Returns a dict with the role's details

        Parameters
        ----------
        role: discord.Role"""
        data = {}
        data[role.id] = {
            "name": role.name,
            "colour": role.colour.to_tuple(),
            "hoist": role.hoist,
            "position": role.position,
            "managed": role.managed,
            "default": role.is_everyone,
            "timestamp": str(role.created_at),
            "perms": {},  # Usage explained in RTD FAQ!,  # Usage explained in RTD FAQ!
            "confs": {}  # Explained in RTD FAQ!
        }
        return data

    def Servers(self, roles):
        """Returns a dict with the roles and their details

        Parameters
        ----------
        roles: list[discord.Role]"""
        data = {}
        for role in roles:
            data[role.id] = self.Server(role)[role.id]
        return data

class EmojiParser(Parser):
    """Emoji Parser: Parser

    This a parser mostly for discord.Emoji related things"""

    def Server(self, emoji: discord.Emoji):
        """Returns a dict with the emoji's details

        Parameters
        ----------
        emoji: discord.Emoji"""
        data = {}
        data[emoji.id] = {
            "name": emoji.name,
            "require_colons": emoji.require_colons,
            "managed": emoji.managed,
            "timestamp": str(emoji.created_at),
            "url": str(emoji.url)
        }
        return data

    def Servers(self, emojis):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        emojis: list[discord.Emoji]"""
        data = {}
        for emoji in emojis:
            data[emoji.id] = self.Server(emoji)[emoji.id]
        return data

class ConfigParser(Parser):
    """Config Parser: Parser

    This a parser mostly for config related things"""
    pass
