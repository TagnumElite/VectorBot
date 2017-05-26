#!/usr/bin/python3.6
# TESTY TESTY!!!
# This file will change over time because I test things here. DUH

import sys, getopt
import io
import os
import shutil
import discord
import asyncio
import PIL
from PIL import ImageFont, Image, ImageDraw
from urllib.request import Request, urlopen, URLopener
from operator import attrgetter
from pathlib import Path

bot = discord.Client()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_server_update(before, after):
    print("Server Updated")

@bot.event
async def on_member_join(member):
    print("Member Joined")

@bot.event
async def on_member_remove(member):
    print("Nember Left")

def getS(status):
    """Make shift get status function"""
    return status

def getG(game):
    """Make shift get game function"""
    if game is None:
        return "Not Playing Anything"
    else:
        return game

def getR(role, default=None):
    """Make shift role"""
    return (
        role.colour.r,
        role.colour.g,
        role.colour.b,
        255
    )
class Colour():
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

class Role():
    """Make shift Role Class"""

    def __init__(self, name: str, color: Colour, position: int):
        self.name = name
        self.colour = color
        self.position = position

class Game():
    """Make shift Game Class"""
    def __init__(self, name: str):
        self.name = name

class Server():
    def __init__(self):
        self.default_role = Role("@everyone", (255, 255, 255), 0)
class Member():
    def __init__(self, name: str, id: str, avatar_url: str, roles, status: str, game: Game):
        self.name = name
        self.id = id
        self.avatar_url = avatar_url
        self.roles = roles
        self.status = status
        self.game = game
        self.server = Server()
        self.top_role = sorted(roles, key=attrgetter('position'))
        self.top_role = self.top_role[len(self.top_role)-1]
        print(self.top_role.name)

def draw():
    os.chdir("./files")
    default = os.getcwd()

    au = None
    au = "https://images.discordapp.net/avatars/179891973795086336/8dd27f5aee2f81cd480f11929a517233.webp?size=1024"
    uid = "179891973795086336"
    if au is not None:
        au = au.replace("webp", "png")
    st = "Online"
    un = "TagnumElite TagnumElite TagnumElite TagnumElite"
    ga = "Massive Effective Testive Extreme Digital Deluxe Ultimate Version"
    role = "admin"
    rc = (255, 186, 0)
    if len(ga) > 25:
        ga = ga[:22]+"..."
    if len(un) > 35:
        un = un[:32]+"..."
    # Font
    textFnt = ImageFont.truetype('default_font_name.ttf', 16)
    textFntB = ImageFont.truetype('default_font_name.ttf', 16)
    textFntI = ImageFont.truetype('default_font_game.ttf', 16)
    # Banner
    banner = None
    if role is not None:
        banner = Image.open(role.lower()+"_banner.png")
    else:
        banner = Image.open("default_banner.png")
    banner_w, banner_h = banner.size
    #background
    background = Image.new('RGBA', banner.size, (0, 0, 0, 0))
    # Avatar
    avatarSize = (70, 70)
    maskSize = (avatarSize[0]*3, avatarSize[1]*3)
    if au is None:
        avatar = Image.open("default_avatar.png")
        avatar.thumbnail(avatarSize, Image.ANTIALIAS)
        avatar_w, avatar_h = avatar.size
    else:
        avreq = Request(au, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(avreq) as response, open(uid+".png", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        avatar = Image.open(uid+".png")
    mask = Image.new('L',  maskSize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + maskSize, fill=255)
    mask = mask.resize(avatar.size, Image.ANTIALIAS)
    avatar.putalpha(mask)
    avatar.thumbnail(avatarSize, Image.ANTIALIAS)
    avatar_w, avatar_h = avatar.size
    a_offset = (int(5), int((banner_h-avatar_h)/2))
    background.paste(avatar, a_offset)
    banner.paste(background, (0, 0), background)
    #Text
    txt = Image.new('RGBA', banner.size, (255, 255, 255, 0))
    text = ImageDraw.Draw(txt)
    text.line((80, 17, 360, 17), fill=(0, 0, 0, 175), width=25)
    text.text((85,8), un, font=textFntB, fill=(rc[0], rc[1], rc[2], 255))
    text.line((80, 58, 270, 58), fill=(0, 0, 0, 175), width=20)
    text.text((84,50), ga, font=textFntI, fill=(255, 255, 255, 255))
    # Status
    statusEllipse = ImageDraw.Draw(txt)
    if st == "Online":
        statusEllipse.ellipse((62, 62, 74, 74), (0, 221, 17), (67, 67, 67))
        print("online")
    elif st == "Offline":
        statusEllipse.ellipse((62, 62, 74, 74), (114, 114, 114), (67, 67, 67))
        print("offline")
    elif st == "Idle":
        statusEllipse.ellipse((62, 62, 74, 74), (234, 149, 32), (67, 67, 67))
        print("idle")
    elif st == "DnD":
        statusEllipse.ellipse((62, 62, 74, 74), (227, 0, 0), (67, 67, 67))
        print("dnd")
    else:
        statusEllipse.ellipse((60, 60, 76, 76), (67, 67, 67))
        print("error")
    out = Image.alpha_composite(banner, txt)
    # Remember to check if directory exists and do stuff from that
    out.save("test.png")

    # Save Storage
    if au is not None:
        os.chdir(default)
        os.remove(uid+".png")
    return uid+".png"

def draw2(member):
        print("Splash: Update")
        """Updates Splash

        .. note::
            I would not let all servers use this and only your main server.
            The reason why is memory usage will be extremely high.
            Also MultiServer Splash Support is not planned and won't be.

        Parameters
        ----------
        member: discord.Member
            The member that was updated/created"""

        class Self():
            def __init__(self, StatusColors={"online": (0, 221, 17), "offline": (114, 114, 114), "idle": (234, 149, 32), "dnd": (227, 0, 0), "outline": (67, 67, 67)}):
                self.SES = (62, 62, 74, 74)
                self.SC = StatusColors

        self = Self()

        # Set Directory To Default
        default = os.getcwd()+"/files/"
        os.chdir(default)

        # Stop the letters from carrying on over off the banner
        name = member.name
        game = getG(member.game.name)
        if len(getG(member.game.name)) > 25:
            game = game[:22]+"..."
            print("Game: ", game)
        if len(member.name) > 28:
            name = name[:28]+"..."
            print("Name: ", name)

        # Setup Vars
        avatar = None
        banner = None
        fontName = None
        fontGame = None
        print("Splash: Setup Vars")

        # Check if the user has more that the default role
        # First lets sorts the roles by ranking just incase!
        print("Splash: Sort Roles")
        roles = sorted(member.roles, key=attrgetter('position'))
        print("Splash: Set Vars")
        # Run roles in reverse so that the highest ranking role goes first
        print("Roles: ", len(member.roles))
        print("Roles: ", roles)
        for role in reversed(roles):
            if role.position is not 0:
                print("Role: ", role.name)
                fontNameP = Path(default+role.name.lower()+"_font_name.ttf")
                fontGameP = Path(default+role.name.lower()+"_font_game.ttf")
                bannerP = Path(default+role.name.lower()+"_banner.png")
                avatarP = Path(default+role.name.lower()+"_avatar.png")
                # Check if there is a custom font for the name
                if fontNameP.exists() and fontName is None:
                    fontName = ImageFont.truetype(role.name.lower()+"_font_name.ttf", 16)
                    print("Splash: Font Name: Exists")
                # Check if there is a custom font for the game
                if fontGameP.exists() and fontGame is None:
                    fontGame = ImageFont.truetype(role.name.lower()+"_font_game.ttf", 16)
                    print("Splash: Font Game: Exists")
                # Check if there is a custom banner
                if bannerP.exists() and banner is None:
                    banner = Image.open(role.name.lower()+"_banner.png")
                    print("Splash: Banner: Exists")
                # Check if there is a custom avatar
                if avatarP.exists() and avatar is None:
                    avatar = Image.open(role.name.lower()+"_avatar.png")
                    print("Splash: Avatar: Exists")
            else: # We have hit the last role. Let's make sure everything is working
                print("Role: Default")
                # If there isn't a custom avatar set default
                if avatar is None:
                    avatar = Image.open("default_avatar.png")
                    print("Splash: Avatar: Default")
                # If there isn't a custom banner set default
                if banner is None:
                    banner = Image.open("default_banner.png")
                    print("Splash: Banner: Default")
                # If there isn't a custom name font set default
                if fontName is None:
                    fontName = ImageFont.truetype("default_font_name.ttf", 16)
                    print("Splash: Font Name: Default")
                # If there isn't a custom game font set default
                if fontGame is None:
                    fontGame = ImageFont.truetype("default_font_game.ttf", 16)
                    print("Splash: Font Game: Default")

        avatarSize = (70, 70)
        maskSize = (avatarSize[0]*3, avatarSize[1]*3)
        print("Splash: Setup Avatar")
        if member.avatar_url is not "":
            avreq = Request(member.avatar_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(avreq) as response, open(member.id+".png", 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            avatar = Image.open(member.id+".png")

        #background
        print("Splash: Setup Background")
        background = Image.new('RGBA', banner.size, (0, 0, 0, 0))
        banner_w, banner_h = banner.size
        mask = Image.new('L',  maskSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + maskSize, fill=255)
        mask = mask.resize(avatar.size, Image.ANTIALIAS)
        avatar.putalpha(mask)
        avatar.thumbnail(avatarSize, Image.ANTIALIAS)
        avatar_w, avatar_h = avatar.size
        a_offset = (int(5), int((banner_h-avatar_h)/2))
        background.paste(avatar, a_offset)
        banner.paste(background, (0, 0), background)

        #Text
        print("Splash: Text")
        txt = Image.new('RGBA', banner.size, (255, 255, 255, 0))
        text = ImageDraw.Draw(txt)
        text.line(
            (80, 17, 360, 17),
            fill=(0, 0, 0, 175),
            width=25
        )
        text.text(
            (85,8),
            name,
            font=fontName,
            fill=getR(
                member.top_role,
                member.server.default_role
            )
        )
        text.line(
            (80, 58, 270, 58),
            fill=(0, 0, 0, 175),
            width=20
        )
        text.text(
            (84,50),
            game,
            font=fontGame,
            fill=(255, 255, 255, 255)
        )

        # Status
        print("Splash: Status")
        statusEllipse = ImageDraw.Draw(txt)
        st = getS(member.status)
        if st == "Online":
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["online"],
                outline=self.SC["outline"]
            )
        elif st == "Offline":
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["offline"],
                outline=self.SC["outline"]
            )
        elif st == "Idle":
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["idle"],
                outline=self.SC["outline"]
            )
        elif st == "DnD":
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["dnd"],
                outline=self.SC["outline"]
            )
        else:
            statusEllipse.ellipse(xy=(60, 60, 76, 76), fill=self.SC["outline"])

        # Output
        print("Splash: Output")
        out = Image.alpha_composite(banner, txt)

        # Check if the Path leads to a working directory if not, create one
        if os.path.exists("tests") and os.path.isdir("tests"):
            os.chdir("tests")
        else:
            try: # Python3
                os.makedirs(name="tests", exist_ok=True)
            except:
                try: # Python2
                    os.makedirs(name="tests")
                except:
                    print("ERROR: CREATING SPLASH SITE DIR")
                    pass
                else:
                    os.chdir("tests")
            else:
                os.chdir("tests")

        # Save Splash
        out.save(member.id+".png")

        # Save Storage
        if member.avatar_url is not "":
            os.chdir(default)
            os.remove(member.id+".png")
        return member.id+".png"

def main():
    #bot.run('')

if __name__ == "__main__":
    #draw()
    #draw2(Member(
    #    name="TagnumElite",
    #    id="179891973795086336",
    #    avatar_url="https://images.discordapp.net/avatars/179891973795086336/8dd27f5aee2f81cd480f11929a517233.webp?size=1024",
    #    roles=[
    #        Role("it support", Colour(25, 25, 25), 1),
    #        Role("admin", Colour(25, 25, 25), 2),
    #        Role("bot master", Colour(25, 25, 25), 3),
    #        Role("bot masters", Colour(25, 25, 25), 4),
    #        Role("senior member", Colour(25, 25, 25), 5),
    #        Role("exco", Colour(25, 25, 25), 6),
    #        Role("@everyone", Colour(255, 255, 255), 0)
    #    ],
    #    status = "Online",
    #    game=Game("TEsty TeSt TeST ReST")
    #))
    main()
