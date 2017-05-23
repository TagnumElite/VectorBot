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
    #MessageDB
    def MessageDBReplace(content):
        """Replaces the contents `\` `"` `'` to something more
        understandable by MySQL"""
        content.replace("\\", "\\\\\\\\") #This should work but because of reasons I don't know why it doesn't so if you know how to fix this please!
        content.replace('\'', '\\\'')
        content.replace("\"", "\\\"")
        return content

    def jsonToDB(to: dict):
        """I don't remember what this was for...."""
        return json.dumps(to)

    def getReactionsJSON(reactions):
        """YOU HEARD ME

        .. note::
            Write Docs like they weren't jokes"""
        json_data = {'reactions':[]}
        for idx, value in enumerate(reactions):
            data = {"emoji":reactions.emoji.id, "custom":int(reactions.custom_emoji), "count":str(reactions.count)}
            json_data['reaction'].append(data)

    def reactionDB(reaction: discord.Reaction, results: dict, user = None, add: bool = True):
        """If no user is added it automatically assumes the reactions were cleared even if add bool is parsed.
        If add is false will remove reaction and reaction doesn't exists returns orginal results"""
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
        return data
    def messageDBDelete(data, time):
        """Appends {"content":None, "timestamp":"%s" % (time)}"""
        return data['content'].append({"content":None, "timestamp":"%s" % (time)})

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
                results['content'].append({"content":"%s"% (self.MessageDBReplace(message.content)), "timestamp":"%s" % (str(message.edited_timestamp))})
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
                query += ", `menstions`='%s'"%(str(self.MessageMentions(message)))
            else:
                query = "`mentions'='%s'"%(str(self.MessageMentions(message)))
            if "attachments" in updates:
                if "content" in updates:
                    query += ", `attachments`='%s'"%(str(attachments).replace("'", "\""))
                else:
                    query = "`attachments`='%s'"%(str(attachments).replace("'", "\""))
            return query

#ServerDB

