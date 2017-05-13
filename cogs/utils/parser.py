import json
import discord

#MessageDB
def MessageDBReplace(content):
    content.replace("\\", "\\\\\\\\") #This should work but because of reasons I don't know why it doesn't so if you know how to fix this please!
    content.replace('\'', '\\\'')
    content.replace("\"", "\\\"")
    return content

def jsonToDB(to: dict):
    return json.dumps(to)

def getReactionsJSON(reactions):
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

def messageDBDelete(data, time):
    """Appends {"content":None, "timestamp":"%s" % (time)}"""
    data['content'].append({"content":None, "timestamp":"%s" % (time)})
    return data

def messageDBUpdate(message: discord.Message, results, updates):
    """NO DOC YET"""
    length = len(updates)
    if length == 1:
        if updates[0] == "content":
            print(message.content, str(message.edited_timestamp))
            results['content'].append({"content":"%s"% (MessageDBReplace(message.content)), "timestamp":"%s" % (str(message.edited_timestamp))})
            return results
        elif updates[0] == "pinned":
            return int(message.pinned)
        else:
            return False
    else:
        content = {"content":[]}
        mention_everyone = 0
        mentions = {"mentions":[]}
        channel_mentions = {"channels":[]}
        role_mentions = {"roles":[]}
        attachments = {}
        query = ""
        if 'content' in updates:
            idx = updates.index('content')
            before = json.loads(results[idx])
            before['content'].append({"content":"%s"% (MessageDBReplace(message.content)), "timestamp":"%s" % (str(message.edited_timestamp))})
            content = before
        for idx, value in enumerate(message.mentions):
            mentions['mentions'].append(value.id)
        for idx, value in enumerate(message.channel_mentions):
            channel_mentions['channels'].append(value.id)
        for idx, value in enumerate(message.role_mentions):
            role_mentions['roles'].append(value.id)
        if "content" in updates:
            query = "`content`='%s'" % (str(content).replace("'", "\""))
        if "mention_everyone" in updates:
            if "content" in updates:
                query += ", `mention_everyone`='%s'" % (mention_everyone)
            else:
                print("ERROR IN LINE 83 parser.py")
        if "mentions" in updates:
            if "content" in updates:
                query += ", `mentions`='%s'" % (str(mentions).replace("'", "\""))
        if "channel_mentions" in updates:
            if "content" in updates:
                query += ", `channel_mentions`='%s'" % (str(channel_mentions).replace("'", "\""))
        if "role_mentions" in updates:
            if "content" in updates:
                query += ", `role_mentions`='%s'"%(str(role_mentions).replace("'", "\""))
        if "attachments" in updates:
            if "content" in updates:
                query += ", `attachments`='%s'"%(str(attachments).replace("'", "\""))
            else:
                query = "`attachments`='%s'"%(str(attachments).replace("'", "\""))
        return query

#ServerDB

