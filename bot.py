from discord.ext import commands
import discord
from cogs.utils import checks
import datetime, re
import json, asyncio
import copy
import logging
import traceback
import sys
import discord.errors
from collections import Counter

description = """
Hello! I am VectorBot
"""

devBot = False

botToken = ""
devToken = ""

botLog = ""
devLog = ""

botWelcome = ""
devWelcome = ""

botNotification = ""
devNotification = ""

if devBot == False:
    currentWelcome = botWelcome
    currentLog = botLog
    currentToken = botToken
    currentNotification = botNotification
else:
    currentWelcome = devWelcome
    currentLog = devLog
    currentToken = devToken
    currentNotification = devNotification

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

einitial_extensions = [
    'cogs.meta',
    'cogs.splatoon',
    'cogs.rng',
    'cogs.mod',
    'cogs.profile',
    'cogs.tags',
    'cogs.lounge',
    'cogs.repl',
    'cogs.carbonitex',
    'cogs.mentions',
    'cogs.api',
    'cogs.stars',
    'cogs.buttons',
    'cogs.pokemon',
    'cogs.permissions',
    'cogs.stats',
]

initial_extensions = [
    'cogs.admin',
    'cogs.feeds',
    'cogs.misc',
    'cogs.utilities',
    'cogs.profile',
]

#discord_logger = logging.getLogger('discord')
#discord_logger.setLevel(logging.CRITICAL)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='vectordev %s.log' % (datetime.datetime.utcnow()), encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#log.addHandler(handler)

help_attrs = dict(hidden=True)

prefix = ['v!', 'V!', '\N{HEAVY EXCLAMATION MARK SYMBOL}']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=True, help_attrs=help_attrs)

async def log_message(message, timeOfMessage=datetime.datetime.utcnow()):
    print(message)
    channel = discord.Object(id=currentLog)
    await bot.send_message(channel, message + " | " + str(timeOfMessage))

async def twitch_notification():
    await bot.wait_until_ready()
    counter = 0
    channel = discord.Object(id=currentNotification)
    while not bot.is_closed:
        counter += 1
        await bot.send_message(channel, counter)
        await asyncio.sleep(60) # task runs every 60 seconds

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)

@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    await log_message("Started:")
    await bot.change_presence(game=discord.Game(name='V!help'))
    bot.currentLog = currentLog
    bot.currentWelcome = currentWelcome
    bot.currentNotification = currentNotification

@bot.event
async def on_resumed():
    await log_message("Resumed...")

@bot.event
async def on_message(message):
    msg = message.content
    author = message.author
    server = message.server
    channel = message.channel
    if message.author.id == bot.user.id:
        return
    if channel.id == currentLog:
        return
    await log_message("(%s | %s) Message: \"%s\" Server: (\"%s\" | %s) Channel: (\"%s\" | %s)" % (author, author.id, message.content, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    if len(msg.split()) > 1:
        msg = msg.split(maxsplit=1)
        msg[0] = msg[0].lower()
        content = " ".join(msg)
        message.content = content
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)
    if message.content.lower().startswith("v!help") or message.content.startswith("\N{HEAVY EXCLAMATION MARK SYMBOL}help"):
        try:
            await bot.delete_message(message)
        except discord.errors.Forbidden():
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id))
        except ValueError:
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: Could not convert data to an integer""" % (author, author.id, server, server.id, channel, channel.id))
        except:
            await log_message("""Error deleteing command `help` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id))

@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def do(ctx, times : int, *, command):
    """Repeats a command a specified number of times."""
    msg = copy.copy(ctx.message)
    msg.content = command
    for i in range(times):
        await bot.process_commands(msg)

@bot.command(pass_context=True, hidden=True)
@checks.admin_or_permissions(manage_server=True)
async def logout(ctx):
    """Logs Bot out of Discord"""
    await log_message("Logging Out!", datetime.datetime.utcnow())
    await bot.say("Logging Out")
    await bot.logout()

@bot.event
async def on_message_delete(message):
    await log_message("Message: (%s | \"%s\") by %s(%s) was deleted" % (message.id, message.content, message.author, message.author.id), datetime.datetime.utcnow())

@bot.event
async def on_message_edit(before, after):
    await log_message("Message: (%s) by %s(%s) was changed from \"%s\" to \"%s\"" % (after.id, after.author, after.author.id, before.content, after.content), after.edited_timestamp)

@bot.event
async def on_member_update(before, after):
    updates = {}
    if before.nick != after.nick:
        updates['nick'] = '%s to %s' % (before.nick, after.nick)
    if before.avatar != after.avatar:
        updates['avatar'] = '%s to %s' % (before.avatar_url, after.avatar_url)
    if before.game != after.game:
        if not before.game:
            beforeGameName = "None"
        else:
            beforeGameName = before.game.name

        if not after.game:
            afterGameName = "None"
        else:
            afterGameName = after.game.name

        updates['game'] = '%s to %s' % (beforeGameName, afterGameName)
    if before.status != after.status:
        if before.status == discord.Status.online:
            beforeStatus = "Online"
        elif before.status == discord.Status.offline:
            beforeStatus = "Offline"
        elif before.status == discord.Status.idle:
            beforeStatus = "IDLE"
        elif before.status == discord.Status.do_not_disturb:
            beforeStatus = "Do Not Disturb"
        elif before.status == discord.Status.invisible:
            beforeStatus = "Invisible"
        else:
            beforeStatus = "ERROR"

        if after.status == discord.Status.online:
            afterStatus = "Online"
        elif after.status == discord.Status.offline:
            afterStatus = "Offline"
        elif after.status == discord.Status.idle:
            afterStatus = "IDLE"
        elif after.status == discord.Status.do_not_disturb:
            afterStatus = "Do Not Disturb"
        elif after.status == discord.Status.invisible:
            afterStatus = "Invisible"
        else:
            afterStatus = "ERROR"

        updates['status'] = '%s to %s' % (beforeStatus, afterStatus)
    if before.voice != after.voice:
        if before.voice.deaf:
            beforeVoice = "Server Deaf"
        elif before.voice.mute:
            beforeVoice = "Server Mute"
        elif before.voice.self_mute:
            beforeVoice = "Self Mute"
        elif before.voice.self_deaf:
            beforeVoice = "Self Deaf"
        elif before.voice.is_afk:
            beforeVoice = "AFK"
        elif hasattr(before.voice, "voice_channel"):
            beforeVoice = "Connected"
        else:
            beforeVoice = "Disconnected"

        if after.voice.deaf:
            afterVoice = "Server Deaf"
        elif after.voice.mute:
            afterVoice = "Server Mute"
        elif after.voice.self_mute:
            afterVoice = "Self Mute"
        elif after.voice.self_deaf:
            afterVoice = "Self Deaf"
        elif after.voice.is_afk:
            afterVoice = "AFK"
        elif hasattr(after.voice, "voice_channel"):
            afterVoice = "Connected"
        else:
            afterVoice = "Disconnected"

        updates['voice'] = '%s to %s' % (beforeVoice, afterVoice)
    if before.roles != after.roles:
        beforeRoles = []
        for role in before.roles:
            if role.name == "@everyone":
                beforeRoles.append("everyone")
            else:
                beforeRoles.append(role.name)


        afterRoles = []
        for role in after.roles:
            if role.name == "@everyone":
                afterRoles.append("everyone")
            else:
                afterRoles.append(role.name)

        updates['roles'] = '%s to %s' % (beforeRoles, afterRoles)

    updateString = ""
    for k, x in updates.items():
        updateString = updateString + k + " : " + x + """
"""

    await log_message("Member: %s(%s) updated: \n%s" % (after, after.id, updateString), datetime.datetime.utcnow())


@bot.event
async def on_member_join(member):
    await log_message("Member: %s(%s) has gone joined the server %s(%s)" % (member.name, member.id, member.server.name, member.server.id), datetime.datetime.utcnow())
    channel = discord.Object(id=currentWelcome)
    em = discord.Embed(title='Welcome to %s!' % (member.server.name), description="""
Use these commands %s!
- V!help to get a PM about my commands!
- V!rules to see the rules!""" % (member.mention), color=0x2ecc71)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    em.set_thumbnail(url=member.avatar_url)
    await bot.send_message(channel, embed=em)

@bot.event
async def on_member_remove(member):
    await log_message("Member: %s(%s) has been removed from the server" % (member, member.id), datetime.datetime.utcnow())

@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    await log_message("Member: %s(%s) has added reaction %s to %s" % (user, user.id, reaction.emoji, message.id), datetime.datetime.utcnow())

@bot.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    await log_message("Member: %s(%s) has removed reaction %s from %s" % (user, user.id, reaction.emoji, message.id), datetime.datetime.utcnow())

@bot.event
async def on_reaction_clear(message, reactions):
    await log_message("Message (%s) has had reactions %s cleared" % (message.id, reactions), datetime.datetime.utcnow())

@bot.event
async def on_channel_delete(channel):
    await log_message("Channel (%s) has been deleted on Server %s(%s)" % (channel.name, channel.id, channel.server.name, channel.server.id), datetime.datetime.utcnow())

@bot.event
async def on_channel_create(channel):
    await log_message("Channel (%s) has been created on Server %s(%s)" % (channel.name, channel.id, channel.server.name, channel.server.id), datetime.datetime.utcnow())

@bot.event
async def on_channel_update(before, after):
    updates = {} #tel = {'jack': 4098, 'sape': 4139}
    if before.name != after.name:
        updates['name'] = '`%s to %s`' % (before.name, after.name)
    if before.id != after.id:
        updates['id'] = '`%s` to `%s`' % (before.id, after.id)
    if before.topic != after.topic:
        if not before.topic:
            beforeTopic = "`NONE`"
        else:
            beforeTopic = "`%s`" % (before.topic)
        if not after.topic:
            afterTopic = "`NONE`"
        else:
            afterTopic = "`%s`" % (after.topic)
        updates['topic'] = '%s to %s' % (beforeTopic, afterTopic)
    if before.position != after.position:
        updates['position'] = '%s to %s' % (before.position, after.position)
    if after.type == discord.ChannelType.voice:
        if before.bitrate != after.bitrate:
            updates['bitrate'] = '%skbps to %skbps' % (before.bitrate, after.bitrate)
        if before.voice_members != after.voice_members:
            updates['voice_members'] = '%s to %s' % (before.voice_members, after.voice_members)
        if before.user_limit != after.user_limit:
            updates['user_limit'] = '%s to %s' % (before.user_limit, after.user_limit)
    if before.changed_roles != after.changed_roles:
        beforeRoles = []
        for role in before.changed_roles:
            if role.name == "@everyone":
                beforeRoles.append("everyone")
            else:
                beforeRoles.append(role.name)

        afterRoles = []
        for role in after.changed_roles:
            if role.name == "@everyone":
                afterRoles.append("everyone")
            else:
                afterRoles.append(role.name)

        updates['roles'] = '%s to %s' % (beforeRoles, afterRoles)
    if before.overwrites != after.overwrites:
        updates['overwrites'] = ""
        #for changed in before.overwrites:
            #updates["B: " + changed[0].name] = changed[1]
        #for changed in after.overwrites:
            #updates["A: " + changed[0].name] = changed[1]
    updateString = ""
    for k, x in updates.items():
        updateString = updateString + k + " : " + x + """
"""

    await log_message("Channel: %s(%s) updated %s" % (after, after.id, updateString), datetime.datetime.utcnow())

@bot.event
async def on_server_update(before, after):
    updates = {} #tel = {'jack': 4098, 'sape': 4139}
    if before.name != after.name:
        updates['name'] = '%s to %s' %s (before.name, after.name)
    if before.afk_channel != after.afk_channel:
        updates['afk_channel'] = '%s to %s' %s (before.afk_channel.name, after.afk_channel.name)
    if before.roles != after.roles:
        beforeRoles = []
        for role in before.roles:
            if role.name == "@everyone":
                beforeRoles.append("everyone")
            else:
                beforeRoles.append(role.name)

        afterRoles = []
        for role in after.roles:
            if role.name == "@everyone":
                afterRoles.append("everyone")
            else:
                afterRoles.append(role.name)

        updates['roles'] = '%s to %s' % (beforeRoles, afterRoles)
    if before.region != after.region:
        updates['region'] = '%s to %s' %s (before.region, after.region)
    if before.emojis != after.emojis:
        updates['emojis'] = 'was changed'
    if before.afk_timeout != after.afk_timeout:
        updates['afk_timeout'] = '%s to %s' %s (before.aft_timeout, after.afk_timeout)
    if before.members != after.members:
        updates['members'] = '%s to %s' %s (before.members, after.members)
    if before.channels != after.channels:
        updates['channels'] = '%s to %s' %s (before.channels, after.channels)
    if before.icon != after.icon:
        updates['icon'] = '%s to %s' %s (before.icon_url, after.icon_url)
    if before.id != after.id:
        updates['id'] = '%s to %s' %s (before.id, after.id)
    if before.owner != after.owner:
        updates['owner'] = '%s(%s) to %s(%s)' %s (before.owner, before.owner.id, after.owner, after.owner.id)
    if before.mfa_level != after.mfa_level:
        await log_message("Server %s(%s) MFA level was changed from %s to %s" % (after.name, after.id, before.mfa_level, after.mfa_level), datetime.datetime.utcnow())
    if before.verification_level != after.verification_level:
        if before.verification_level == discord.VerificationLevel.none:
            beforeLevel = "None"
        elif before.verification_level == discord.VerificationLevel.low:
            beforeLevel = "Low"
        elif before.verification_level == discord.VerificationLevel.medium:
            beforeLevel = "Medium"
        elif before.verification_level == discord.VerificationLevel.high:
            beforeLevel = "High"
        else:
            beforeLevel = "Error"

        if after.verification_level == discord.VerificationLevel.none:
            afterLevel = "None"
        elif after.verification_level == discord.VerificationLevel.low:
            afterLevel = "Low"
        elif after.verification_level == discord.VerificationLevel.medium:
            afterLevel = "Medium"
        elif after.verification_level == discord.VerificationLevel.high:
            afterLevel = "High"
        else:
            afterLevel = "Error"

        updates['verification_level'] = '%s to %s' %s (beforeLevel, afterLevel)
    if before.role_hierarchy != after.role_hierarchy:
        updates['role_hierarchy'] = 'was changed'

    updateString = ""
    for k, x in updates.items():
        updateString = updateString + k + " : " + x + """
"""

    await log_message("Server: %s(%s) updated %s" % (after, after.id, updateString), datetime.datetime.utcnow())

@bot.event
async def on_member_ban(member):
    await log_message("User %s(%s) was banned from server %s(%s)" % (member, member.id, member.server.name, member.server.id), datetime.datetime.utcnow())

@bot.event
async def on_member_unban(member):
    await log_message("User %s(%s) was unbanned from server %s(%s)" % (member, member.id, member.server.name, member.server.id), datetime.datetime.utcnow())

@bot.event
async def on_server_role_create(role):
    await log_message("Role %s(%s) was created on server %s(%s)" % (role.name, role.id, role.server.name, role.server.id), datetime.datetime.utcnow())

@bot.event
async def on_server_role_delete(role):
    await log_message("Role %s(%s) was removed on server %s(%s)" % (role.name, role.id, role.server.name, role.server.id), datetime.datetime.utcnow())

@bot.event
async def on_server_role_update(before, after):
    updates = {}
    if before.id != after.id:
        updates['id'] = "%s to %s" % (before.id, after.id)
    if before.name != after.name:
        updates['name'] = "%s to %s" % (before.name, after.name)
    if before.colour != after.colour:
        updates['colour'] = "RGB(%s, %s, %s) to RGB(%s, %s, %s)" % (before.colour.r, before.colour.g, before.colour.b, after.colour.r, after.colour.g, after.colour.b)
    if before.hoist != after.hoist:
        updates['hoist'] = "%s to %s" % (before.hoist, after.hoist)
    if before.position != after.position:
        updates['position'] = "%s to %s" % (before.position, after.position)
    if before.managed != after.managed:
        updates['managed'] = "%s to %s" % (before.managed, after.managed)
    if before.mentionable != after.mentionable:
        updates['mentionable'] = "%s to %s" % (before.mentionable, after.mentionable)
    if before.permissions != after.permissions:
        updates['permissions'] = await checks.get_different_perms(before.permissions, after.permissions)

    updateString = ""
    for k, x in updates.items():
        updateString = """
""" + updateString + k + " : " + x

    await log_message("Role: %s(%s) updated %s" % (after, after.id, updateString), datetime.datetime.utcnow())

@bot.command(pass_context=True)
async def rules(ctx):
    msg = ctx.message
    server = msg.server
    author = msg.author
    channel = msg.channel
    await log_message("User %s(%s) ran command `rules` on server %s(%s) in channel %s(%s)" % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    em = discord.Embed(title='%s\'s rules!' % (server.name), description="""THA RULES""", color=0x992d22)
    try:
        await bot.delete_message(msg)
    except discord.errors.Forbidden():
        await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    except ValueError:
         await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: Could not convert data to an integer""" % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    except:
         await log_message("""Error deleteing command `rules` run by %s(%s) on server %s(%s) in channel %s(%s)
Error: {0}""".format(Forbidden) % (author, author.id, server, server.id, channel, channel.id), datetime.datetime.utcnow())
    await bot.send_message(author, embed=em)

@bot.command(pass_context=True)
async def find(ctx, user=None):
    """Finds User"""
    await log_message("Command `find` was run")
    if user == None:
        await bot.say("Please specify user to find")
        return
    else:
        await bot.say("User is " + str(user))

    server = ctx.message.server
    if server == None:
        await bot.say("Server not found")
        return
    else:
        await bot.say("Server is %s" % (server.name))

    members = server.members
    mems = []
    if members == None:
        await bot.say("Members not found")
        return
    else:
        for member in members:
            mems.append(member.name)
        await bot.say("Members are %s" % (mems))

    #member = checks.find_user(user, members)
    member = server.get_member_named(user)

    if member == None:
        print(member)
        await bot.say("User not found")
        return
    else:
        await bot.say("User %s was found" % (member))

@bot.command(pass_context=True)
async def get(ctx, user: int):
    """Get User By Number"""
    server = ctx.message.server
    if server == None:
        await bot.say("Server not found")
        return
    else:
        await bot.say("Server is %s" % (server.name))

    members = server.members
    mems = []
    if members == None:
        await bot.say("Members not found")
        return
    else:
        for member in members:
            mems.append(member.name)
        await bot.say("Members are %s" % (mems))

    await bot.say("Member is %s" % list(members)[user])

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

if __name__ == '__main__':
    #credentials = load_credentials()
    #debug = any('debug' in arg.lower() for arg in sys.argv)
    #if debug:
    #    bot.command_prefix = '$'
    #    token = credentials.get('debug_token', credentials['token'])
    #else:
    #    token = credentials['token']

    #bot.client_id = credentials['client_id']
    #bot.carbon_key = credentials['carbon_key']
    #bot.bots_key = credentials['bots_key']

    #if debug:
    #    initial_extensions.remove('cogs.carbonitex')

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    #Setup Twitch Notifications
    #bot.loop.create_task(twitch_notification())

    #Run Bot
    bot.currentLog = currentLog
    bot.run(currentToken)

    #handlers = log.handlers[:]
    #for hdlr in handlers:
    #    hdlr.close()
    #log.removeHandler(hdlr)
