from discord.ext import commands
from difflib import SequenceMatcher
import datetime
import discord.utils

def similarSeq(a, b):
    return SequenceMatcher(None, a, b).ratio()

def similar(w1, w2):
    w1 = w1 + ' ' * (len(w2) - len(w1))
    w2 = w2 + ' ' * (len(w1) - len(w2))
    return sum(1 if i == j else 0 for i, j in zip(w1, w2)) / float(len(w1))

def is_owner_check(message):
    return message.author.id == '80088516616269824'

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# If these checks fail, then there are two fallbacks.
# A role with the name of Bot Mod and a role with the name of Bot Admin.
# Having these roles provides you access to certain commands without actually having
# the permissions required for them.
# Of course, the owner will always be able to execute commands.

def check_permissions(ctx, perms):
    msg = ctx.message
    if is_owner_check(msg):
        return True

    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    if ch.is_private:
        return False # can't have roles in PMs

    role = discord.utils.find(check, author.roles)
    return role is not None

def mod_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name in ('Bot Mod', 'Bot Admin'), **perms)

    return commands.check(predicate)

def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name == 'Bot Admin', **perms)

    return commands.check(predicate)

def is_in_servers(*server_ids):
    def predicate(ctx):
        server = ctx.message.server
        if server is None:
            return False
        return server.id in server_ids
    return commands.check(predicate)

def is_lounge_cpp():
    return is_in_servers('145079846832308224')

def find_user(username, members):
    usernames = []
    nicknames = []
    for mem in members:
        usernames.append(mem.name)
        nicknames.append(mem.nick)

    similarUsers = []
    for userNa in usernames:
        similarUsers.append(similar(username, userNa))

    similarNicks = []
    for nickNa in nicknames:
        if nickNa != None:
            similarNicks.append(similar(username, nickNa))
    try:
        highestUser = max(similarUsers)
    except Exception as e:
        print(e)
        highestUser = -1
    if similarNicks != []:
        highestNick = max(similarNicks)
    else:
        highestNick = 0
    if highestUser == -1:
        return members
    else:
        indexNumber = -1
        if highestUser > 0.6:
            if highestUser > highestNick:
                indexNumber = similarUsers.index(highestUser)
            else:
                if highestNick > highestUser:
                    if highestNick > 0.6:
                        indexNumber = similarNicks.index(highestNick)
        elif highestNick > 0.6:
            indexNumber = similarNicks.index(highestNick)
        else:
            indexNumber = -1

    if indexNumber == -1:
        return False
    else:
        return list(members)[indexNumber]

async def log_message(message, bot, timeOfMessage=datetime.datetime.utcnow()):
    print(message)
    channel = discord.Object(id=bot.currentLog)
    await bot.send_message(channel, message + " | " + str(timeOfMessage))

async def get_different_perms(before, after):
    updates = {}
    if before.create_instant_invite != after.create_instant_invite:
        updates['create_instant_invite'] = "%s -> %s" % (before.create_instant_invite, after.create_instant_invite)
    if before.kick_members != after.kick_members:
        updates['kick_members'] = "%s -> %s" % (before.kick_members, after.kick_members)
    if before.ban_members != after.ban_members:
        updates['ban_members'] = "%s -> %s" % (before.ban_members, after.ban_members)
    if before.administrator != after.administrator:
        updates['administrator'] = "%s -> %s" % (before.administrator, after.administrator)
    if before.manage_channels != after.manage_channels:
        updates['manage_channels'] = "%s -> %s" % (before.manage_channels, after.manage_channels)
    if before.manage_server != after.manage_server:
        updates['manage_server'] = "%s -> %s" % (before.manage_server, after.manage_server)
    if before.add_reactions != after.add_reactions:
        updates['add_reactions'] = "%s -> %s" % (before.add_reactions, after.add_reactions)
    if before.read_messages != after.read_messages:
        updates['read_messages'] = "%s -> %s" % (before.read_messages, after.read_messages)
    if before.send_messages != after.send_messages:
        updates['send_messages'] = "%s -> %s" % (before.send_messages, after.send_messages)
    if before.send_tts_messages != after.send_tts_messages:
        updates['send_tts_messages'] = "%s -> %s" % (before.send_tts_messages, after.send_tts_messages)
    if before.manage_messages != after.manage_messages:
        updates['manage_messages'] = "%s -> %s" % (before.manage_messages, after.manage_messages)
    if before.embed_links != after.embed_links:
        updates['embed_links'] = "%s -> %s" % (before.embed_links, after.embed_links)
    if before.attach_files != after.attach_files:
        updates['attach_files'] = "%s -> %s" % (before.attach_files, after.attach_files)
    if before.read_message_history != after.read_message_history:
        updates['read_message_history'] = "%s -> %s" % (before.read_message_history, after.read_message_history)
    if before.mention_everyone != after.mention_everyone:
        updates['mention_everyone'] = "%s -> %s" % (before.mention_everyone, after.mention_everyone)
    if before.external_emojis != after.external_emojis:
        updates['external_emojis'] = "%s -> %s" % (before.external_emojis, after.external_emojis)
    if before.connect != after.connect:
        updates['connect'] = "%s -> %s" % (before.connect, after.connect)
    if before.speak != after.speak:
        updates['speak'] = "%s -> %s" % (before.speak, after.speak)
    if before.mute_members != after.mute_members:
        updates['mute_members'] = "%s -> %s" % (before.mute_members, after.mute_members)
    if before.deafen_members != after.deafen_members:
        updates['deafen_members'] = "%s -> %s" % (before.deafen_members, after.deafen_members)
    if before.move_members != after.move_members:
        updates['move_members'] = "%s -> %s" % (before.move_members, after.move_members)
    if before.use_voice_activation != after.use_voice_activation:
        updates['use_voice_activation'] = "%s -> %s" % (before.use_voice_activation, after.use_voice_activation)
    if before.change_nickname != after.change_nickname:
        updates['change_nickname'] = "%s -> %s" % (before.change_nickname, after.change_nickname)
    if before.manage_nicknames != after.manage_nicknames:
        updates['manage_nicknames'] = "%s -> %s" % (before.manage_nicknames, after.manage_nicknames)
    if before.manage_roles != after.manage_roles:
        updates['manage_roles'] = "%s -> %s" % (before.manage_roles, after.manage_roles)
    if before.manage_webhooks != after.manage_webhooks:
        updates['manage_webhooks'] = "%s -> %s" % (before.manage_webhooks, after.manage_webhooks)
    if before.manage_emojis != after.manage_emojis:
        updates['manage_emojis'] = "%s -> %s" % (before.manage_emojis, after.manage_emojis)

    updateString = ""
    for k, x in updates.items():
        updateString = updateString + k + " : " + x + """
"""

    return updateStringasync

def getServerDif(before, after):
    updates = {}
    if before.create_instant_invite != after.create_instant_invite:
        updates['create_instant_invite'] = "%s -> %s" % (before.create_instant_invite, after.create_instant_invite)
    if before.kick_members != after.kick_members:
        updates['kick_members'] = "%s -> %s" % (before.kick_members, after.kick_members)
    if before.ban_members != after.ban_members:
        updates['ban_members'] = "%s -> %s" % (before.ban_members, after.ban_members)
    if before.administrator != after.administrator:
        updates['administrator'] = "%s -> %s" % (before.administrator, after.administrator)
    if before.manage_channels != after.manage_channels:
        updates['manage_channels'] = "%s -> %s" % (before.manage_channels, after.manage_channels)
    if before.manage_server != after.manage_server:
        updates['manage_server'] = "%s -> %s" % (before.manage_server, after.manage_server)
    if before.add_reactions != after.add_reactions:
        updates['add_reactions'] = "%s -> %s" % (before.add_reactions, after.add_reactions)
    if before.read_messages != after.read_messages:
        updates['read_messages'] = "%s -> %s" % (before.read_messages, after.read_messages)
    if before.send_messages != after.send_messages:
        updates['send_messages'] = "%s -> %s" % (before.send_messages, after.send_messages)
    if before.send_tts_messages != after.send_tts_messages:
        updates['send_tts_messages'] = "%s -> %s" % (before.send_tts_messages, after.send_tts_messages)
    if before.manage_messages != after.manage_messages:
        updates['manage_messages'] = "%s -> %s" % (before.manage_messages, after.manage_messages)
    if before.embed_links != after.embed_links:
        updates['embed_links'] = "%s -> %s" % (before.embed_links, after.embed_links)
    if before.attach_files != after.attach_files:
        updates['attach_files'] = "%s -> %s" % (before.attach_files, after.attach_files)
    if before.read_message_history != after.read_message_history:
        updates['read_message_history'] = "%s -> %s" % (before.read_message_history, after.read_message_history)
    if before.mention_everyone != after.mention_everyone:
        updates['mention_everyone'] = "%s -> %s" % (before.mention_everyone, after.mention_everyone)
    if before.external_emojis != after.external_emojis:
        updates['external_emojis'] = "%s -> %s" % (before.external_emojis, after.external_emojis)
    if before.connect != after.connect:
        updates['connect'] = "%s -> %s" % (before.connect, after.connect)
    if before.speak != after.speak:
        updates['speak'] = "%s -> %s" % (before.speak, after.speak)
    if before.mute_members != after.mute_members:
        updates['mute_members'] = "%s -> %s" % (before.mute_members, after.mute_members)
    if before.deafen_members != after.deafen_members:
        updates['deafen_members'] = "%s -> %s" % (before.deafen_members, after.deafen_members)
    if before.move_members != after.move_members:
        updates['move_members'] = "%s -> %s" % (before.move_members, after.move_members)
    if before.use_voice_activation != after.use_voice_activation:
        updates['use_voice_activation'] = "%s -> %s" % (before.use_voice_activation, after.use_voice_activation)
    if before.change_nickname != after.change_nickname:
        updates['change_nickname'] = "%s -> %s" % (before.change_nickname, after.change_nickname)
    if before.manage_nicknames != after.manage_nicknames:
        updates['manage_nicknames'] = "%s -> %s" % (before.manage_nicknames, after.manage_nicknames)
    if before.manage_roles != after.manage_roles:
        updates['manage_roles'] = "%s -> %s" % (before.manage_roles, after.manage_roles)
    if before.manage_webhooks != after.manage_webhooks:
        updates['manage_webhooks'] = "%s -> %s" % (before.manage_webhooks, after.manage_webhooks)
    if before.manage_emojis != after.manage_emojis:
        updates['manage_emojis'] = "%s -> %s" % (before.manage_emojis, after.manage_emojis)
    return "updates"

def getVerficationLevel(ver):
    if ver == discord.VerificationLevel.none:
        return "None"
    elif ver == discord.VerificationLevel.low:
        return "Low"
    elif ver == discord.VerificationLevel.medium:
        return "Medium"
    elif ver == discord.VerificationLevel.high:
        return "High"
    elif ver == discord.VerificationLevel.table_flip:
        return "High"
    else:
        return "ERROR"
