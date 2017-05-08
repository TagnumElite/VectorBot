from discord.ext import commands
from datetime import datetime
import discord
from .utils import checks
import aiohttp
from urllib.parse import parse_qs
from lxml import etree
import random

def date(argument):
    formats = (
        '%Y/%m/%d',
        '%Y-%m-%d',
    )

    for fmt in formats:
        try:
            return datetime.strptime(argument, fmt)
        except ValueError:
            continue

    raise commands.BadArgument('Cannot convert to date. Expected YYYY/MM/DD or YYYY-MM-DD.')

class Buttons:
    """Buttons that make you feel."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def feelgood(self):
        """press"""
        await self.bot.say('*pressed*')

    @commands.command(hidden=True)
    async def feelbad(self):
        """depress"""
        await self.bot.say('*depressed*')

    @commands.command()
    async def love(self):
        """What is love?"""
        x = random.choice(['https://www.youtube.com/watch?v=HEXWRTEbj1I', 'http://i.imgur.com/JthwtGA.png'])
        await self.bot.say(x)

    @commands.command(hidden=True)
    async def bored(self):
        """boredom looms"""
        await self.bot.say('http://i.imgur.com/BuTKSzf.png')

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def nostalgia(self, ctx, date: date, *, channel: discord.Channel = None):
        """Pins an old message from a specific date.

        If a channel is not given, then pins from the channel the
        command was ran on.

        The format of the date must be either YYYY-MM-DD or YYYY/MM/DD.
        """

        if channel is None:
            channel = ctx.message.channel

        async for m in self.bot.logs_from(channel, after=date, limit=1):
            try:
                await self.bot.pin_message(m)
            except:
                await self.bot.say('\N{THUMBS DOWN SIGN} Could not pin message.')
            else:
                await self.bot.say('\N{THUMBS UP SIGN} Successfully pinned message.')

    @nostalgia.error
    async def nostalgia_error(self, error, ctx):
        if type(error) is commands.BadArgument:
            await self.bot.say(error)

    def parse_google_card(self, node):
        if node is None:
            return None

        e = discord.Embed(colour=0x738bd7)

        # check if it's a calculator card:
        calculator = node.find(".//table/tr/td/span[@class='nobr']/h2[@class='r']")
        if calculator is not None:
            e.title = 'Calculator'
            e.description = ''.join(calculator.itertext())
            return e

        parent = node.getparent()

        # check for unit conversion card
        unit = parent.find(".//ol//div[@class='_Tsb']")
        if unit is not None:
            e.title = 'Unit Conversion'
            e.description = ''.join(''.join(n.itertext()) for n in unit)
            return e

        # check for currency conversion card
        currency = parent.find(".//ol/table[@class='std _tLi']/tr/td/h2")
        if currency is not None:
            e.title = 'Currency Conversion'
            e.description = ''.join(currency.itertext())
            return e

        # check for release date card
        release = parent.find(".//div[@id='_vBb']")
        if release is not None:
            try:
                e.description = ''.join(release[0].itertext()).strip()
                e.title = ''.join(release[1].itertext()).strip()
                return e
            except:
                return None

        # check for definition card
        words = parent.find(".//ol/div[@class='g']/div/h3[@class='r']/div")
        if words is not None:
            try:
                definition_info = words.getparent().getparent()[1] # yikes
            except:
                pass
            else:
                try:
                    # inside is a <div> with two <span>
                    # the first is the actual word, the second is the pronunciation
                    e.title = words[0].text
                    e.description = words[1].text
                except:
                    return None

                # inside the table there's the actual definitions
                # they're separated as noun/verb/adjective with a list
                # of definitions
                for row in definition_info:
                    if len(row.attrib) != 0:
                        # definitions are empty <tr>
                        # if there is something in the <tr> then we're done
                        # with the definitions
                        break

                    try:
                        data = row[0]
                        lexical_category = data[0].text
                        body = []
                        for index, definition in enumerate(data[1], 1):
                            body.append('%s. %s' % (index, definition.text))

                        e.add_field(name=lexical_category, value='\n'.join(body), inline=False)
                    except:
                        continue

                return e

        # check for "time in" card
        time_in = parent.find(".//ol//div[@class='_Tsb _HOb _Qeb']")
        if time_in is not None:
            try:
                time_place = ''.join(time_in.find("span[@class='_HOb _Qeb']").itertext()).strip()
                the_time = ''.join(time_in.find("div[@class='_rkc _Peb']").itertext()).strip()
                the_date = ''.join(time_in.find("div[@class='_HOb _Qeb']").itertext()).strip()
            except:
                return None
            else:
                e.title = time_place
                e.description = '%s\n%s' % (the_time, the_date)
                return e

        # check for weather card
        # this one is the most complicated of the group lol
        # everything is under a <div class="e"> which has a
        # <h3>{{ weather for place }}</h3>
        # string, the rest is fucking table fuckery.
        weather = parent.find(".//ol//div[@class='e']")
        if weather is None:
            return None

        location = weather.find('h3')
        if location is None:
            return None

        e.title = ''.join(location.itertext())

        table = weather.find('table')
        if table is None:
            return None

        # This is gonna be a bit fucky.
        # So the part we care about is on the second data
        # column of the first tr
        try:
            tr = table[0]
            img = tr[0].find('img')
            category = img.get('alt')
            image = 'https:' + img.get('src')
            temperature = tr[1].xpath("./span[@class='wob_t']//text()")[0]
        except:
            return None # RIP
        else:
            e.set_thumbnail(url=image)
            e.description = '*%s*' % category
            e.add_field(name='Temperature', value=temperature)

        # On the 4th column it tells us our wind speeds
        try:
            wind = ''.join(table[3].itertext()).replace('Wind: ', '')
        except:
            return None
        else:
            e.add_field(name='Wind', value=wind)

        # On the 5th column it tells us our humidity
        try:
            humidity = ''.join(table[4][0].itertext()).replace('Humidity: ', '')
        except:
            return None
        else:
            e.add_field(name='Humidity', value=humidity)

        return e

    async def get_google_entries(self, query):
        params = {
            'q': query,
            'safe': 'on'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
        }

        # list of URLs
        entries = []

        # the result of a google card, an embed
        card = None

        async with aiohttp.get('https://www.google.com/search', params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google somehow failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            # with open('google.html', 'w', encoding='utf-8') as f:
            #     f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))

            """
            Tree looks like this.. sort of..

            <div class="g">
                ...
                <h3>
                    <a href="/url?q=<url>" ...>title</a>
                </h3>
                ...
                <span class="st">
                    <span class="f">date here</span>
                    summary here, can contain <em>tag</em>
                </span>
            </div>
            """

            card_node = root.find(".//div[@id='topstuff']")
            card = self.parse_google_card(card_node)

            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue

                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue

                url = parse_qs(url[5:])['q'][0] # get the URL from ?q query string

                # if I ever cared about the description, this is how
                entries.append(url)

                # short = node.find(".//span[@class='st']")
                # if short is None:
                #     entries.append((url, ''))
                # else:
                #     text = ''.join(short.itertext())
                #     entries.append((url, text.replace('...', '')))

        return card, entries

    @commands.command(aliases=['google'])
    async def g(self, *, query):
        """Searches google and gives you top result."""
        await self.bot.type()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await self.bot.say(str(e))
        else:
            if card:
                value = '\n'.join(entries[:3])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await self.bot.say(embed=card)

            if len(entries) == 0:
                return await self.bot.say('No results found... sorry.')

            next_two = entries[1:3]
            if next_two:
                formatted = '\n'.join(map(lambda x: '<%s>' % x, next_two))
                msg = '{}\n\n**See also:**\n{}'.format(entries[0], formatted)
            else:
                msg = entries[0]

            await self.bot.say(msg)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=60.0, type=commands.BucketType.user)
    async def feedback(self, ctx, *, content: str):
        """Gives feedback about the bot.

        This is a quick way to request features or bug fixes
        without being in the bot's server.

        The bot will communicate with you via PM about the status
        of your request if possible.

        You can only request feedback once a minute.
        """

        e = discord.Embed(title='Feedback', colour=0x738bd7)
        msg = ctx.message

        channel = self.bot.get_channel('263814407191134218')
        if channel is None:
            return

        e.set_author(name=str(msg.author), icon_url=msg.author.avatar_url or msg.author.default_avatar_url)
        e.description = content
        e.timestamp = msg.timestamp

        if msg.server is not None:
            e.add_field(name='Server', value='{0.name} (ID: {0.id})'.format(msg.server), inline=False)

        e.add_field(name='Channel', value='{0} (ID: {0.id})'.format(msg.channel), inline=False)
        e.set_footer(text='Author ID: ' + msg.author.id)

        await self.bot.send_message(channel, embed=e)
        await self.bot.send_message(msg.channel, 'Successfully sent feedback \u2705')

    @commands.command()
    @checks.is_owner()
    async def pm(self, user_id: str, *, content: str):
        user = await self.bot.get_user_info(user_id)

        try:
            await self.bot.send_message(user, content)
        except:
            await self.bot.say('Could not PM user by ID ' + user_id)
        else:
            await self.bot.say('PM successfully sent.')

def setup(bot):
    bot.add_cog(Buttons(bot))



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
        if after.voice.deaf:
            beforeVoice = "Server Deaf"
        elif after.voice.mute:
            beforeVoice = "Server Mute"
        elif after.voice.self_mute:
            beforeVoice = "Self Mute"
        elif after.voice.self_deaf:
            beforeVoice = "Self Deaf"
        elif after.voice.is_afk:
            beforeVoice = "AFK"
        else:
            beforeVoice = "ERROR"

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
        else:
            afterVoice = "ERROR"

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
