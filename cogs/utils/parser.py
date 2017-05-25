"""
Because JSON
@author: TagnumElite
@broken: because I am scrub and is too lazy to carry one coding today.
@todo: FIX THE DAMN CODE AND MAKE IT WORK!
"""

import json
import discord


class Parser():
    """PARSER!"""
    """MemberDB Parsing"""
    def getStatus(status):
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
    """MessageDB Parsing"""
    def MessageDBReplace(content):
        """Replaces the contents `\` `"` `'` to something more
        understandable by MySQL"""
        content.replace("\\", "\\\\\\\\")  # This should work but because of reasons I don't know why it doesn't so if you know how to fix this please!
        content.replace('\'', '\\\'')
        content.replace("\"", "\\\"")
        return content

    def jsonToDB(to: dict):
        """I don't remember what this was for....
        but is esentially just `json.dumps(to)`

        Parameters
        ----------
        to: dict
            Turns the dict into a string"""
        return json.dumps(to)

    def getReactionsJSON(reactions):
        """Turns reactions on a message to MySQL readable json

        Parameters
        ----------
        reactions: list of reactions
            An iterable of reactions that get converted into json data"""
        json_data = {'reactions':[]}
        for idx, value in enumerate(reactions):
            data = {"emoji":reactions.emoji.id, "custom":int(reactions.custom_emoji), "count":str(reactions.count)}
            json_data['reaction'].append(data)

    def reactionDB(reaction: discord.Reaction, results: dict, user = None, add: bool = True):
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

    def MessageMentions(message: discord.Message):
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
    def messageDBDelete(data: dict, time):
        """Appends {"content":None, "timestamp":"%s" % (time)}

        Parameters
        ----------
        data: dict
            The current existing data
        time: datetime or str
            The time of when the message was deleted"""
        return data['content'].append({"content":None, "timestamp":"%s" % (str(time))})

    def messageDBUpdate(message: discord.Message, results, updates):
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
    """ServerDB Parsing"""
    def getChannelType(channelType):
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

    def ServerMembers(members):
        """Returns a dict with the members and their details

        Parameters
        ----------
        members: list of discord.Member"""
        data = {}
        for member in members:
            data[member.id] = {
                "nick": member.nick,
                "roles": [None],
                "joined_at": str(member.joined_at),
                "status": self.getStatus(member.status),
                "game": member.game.name,
                "top_role": member.top_role.id,
                "perms": {}  # Usage explained in RTD FAQ!
            }
            data[member.id]["roles"] = []
            for role in member.roles:
                data[member.id]["roles"].append(role.id)
        return data

    def ServerRoles(roles):
        """Returns a dict with the roles and their details

        Parameters
        ----------
        roles: list of discord.Role"""
        data = {}
        for role in roles:
            data[role.id] = {
                "name": role.name,
                "perms": {},  # Usage explained in RTD FAQ!
                "colour": role.colour.to_tuple(),
                "hoist": role.hoist,
                "position": role.position,
                "managed": role.managed,
                "default": role.is_everyone,
                "timestamp": str(role.created_at)
            }
        return data

    def ServerEmojis(emojis):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        emojis: list of discord.Emoji"""
        data = {}
        for emoji in emojis:
            data[emoji.id] = {
                "name": emoji.name,
                "require_colons": emoji.require_colons,
                "managed": emoji.managed,
                "timestamp": str(emoji.created_at),
                "url": str(emoji.url)
            }
        return data

    def ServerChannels(channels):
        """Returns a dict with the channels and their details

        Parameters
        ----------
        channels: list of discord.Channel"""
        data = {}
        for channel in channels:
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
                "perms": {}  # Usage explained in RTD FAQ!
            }
        return data
