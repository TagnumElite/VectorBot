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


    def ServerMember(self, member: discord.Member):
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

    def ServerMembers(self, members):
        """Returns a dict with the members and their details

        Parameters
        ----------
        members: list of discord.Member"""
        data = {}
        for member in members:
            data[member.id] = self.ServerMember(member)[member.id]
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

    def getReactionsJSON(self, reactions):
        """Turns reactions on a message to MySQL readable json

        Parameters
        ----------
        reactions: list[discord.Reaction]
            An iterable of reactions that get converted into json data"""
        json_data = {'reactions':[]}
        for idx, value in enumerate(reactions):
            data = {"emoji":reactions.emoji.id, "custom":int(reactions.custom_emoji), "count":str(reactions.count)}
            json_data['reaction'].append(data)

    def reactionDB(self, reaction: discord.Reaction, results: dict, user=None, add: bool=True):
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
        return str(data).replace("True", "true").replace("False", "false")
    def messageDBDelete(self, data: dict, time):
        """Appends ``{"content":None, "timestamp":"%s" % (time)}``

        Parameters
        ----------
        data: dict
            The current existing data
        time: datetime or str
            The time of when the message was deleted"""
        return data['content'].append({"content":None, "timestamp":"%s" % (str(time))})

    def messageDBUpdate(self, message: discord.Message, results, updates):
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
                    query += ", `mentions`='%s'"%(str(self.MessageMentions(message)))
                else:
                    query = "`mentions'='%s'"%(self.MessageMentions(message))
            return query

    def reactionDB(self, reaction: discord.Reaction, results: dict, user=None, add: bool=True):
        """If no user is added it automatically assumes the reactions were cleared even if add bool is parsed.
        If add is false will remove reaction and reaction doesn't exists returns orginal results

        Parameters
        ----------
        reaction: discord.Reaction
            Reaction
        results: dict

        user: discord.User or discord.Member
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
        return str(data).replace("True", "true").replace("False", "false")
    def messageDBDelete(self, data: dict, time):
        """Appends ``{"content":None, "timestamp":"%s" % (time)}``

        Parameters
        ----------
        data: dict
            The current existing data
        time: datetime or str
            The time of when the message was deleted"""
        return data['content'].append({"content":None, "timestamp":"%s" % (str(time))})

    def messageDBUpdate(self, message: discord.Message, results, updates):
        """This updates the message using the originally stored on the Database and
        the new one updated one.

        Paramters
        ---------
        message: discord.Message

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
                    query += ", `mentions`='%s'"%(str(self.MessageMentions(message)))
                else:
                    query = "`mentions'='%s'"%(self.MessageMentions(message))
            return query

class ServerParser(Parser):
    """Server Parser: Parser

    This a parser mostly for discord.Server related things"""

    def getRegion(self, region):
        """Gets a Verification Level and returns a string.

        Paramters
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

        Paramters
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

class ChannelParser(Parser):
    """discord.Channel parser!"""
    def getChannelType(self, channelType):
        """Gets a channels type and returns a string.

        Paramters
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

    def ServerChannel(self, channel: discord.Channel):
        """Returns a dict with the channel's details

        Parameters
        ----------
        channel: discord.Channel"""
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

    def ServerChannels(self, channels):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        channels: list of discord.Channel"""
        data = {}
        for channel in channels:
            data[channel.id] = self.ServerChannel(channel)[channel.id]
        return data

class RoleParser(Parser):
    """discord.Role Parser!"""
    def ServerRole(self, role: discord.Role):
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

    def ServerRoles(self, roles):
        """Returns a dict with the roles and their details

        Parameters
        ----------
        roles: list of discord.Role"""
        data = {}
        for role in roles:
            data[role.id] = self.ServerRole(role)[role.id]
        return data

class EmojiParser(Parser):
    """discord.Emoji Parser!"""
    def ServerEmoji(self, emoji: discord.Emoji):
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

    def ServerEmojis(self, emojis):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        emojis: list of discord.Emoji"""
        data = {}
        for emoji in emojis:
            data[emoji.id] = self.ServerEmoji(emoji)[emoji.id]
        return data

class ConfigParser(Parser):
    """Config Parser: Parser

    This a parser mostly for config related things"""
    pass
