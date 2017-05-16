"""
Drawing Module

I need to cleanup a lot of the code here as well improve my understanding of pillow.
That way in the future I can make this more resource efficient
"""
import io
import os
import shutil
import discord
import PIL
from PIL import ImageFont, Image, ImageDraw
from urllib.request import Request, urlopen, URLopener
from operator import attrgetter
from pathlib import Path

def getS(status: discord.Status):
    """Returns a str of the Status

    Parameters
    ----------
    status: discord.Status
        The Discord Status"""
    if status == discord.Status.online:
        return "Online"
    elif status == discord.Status.idle:
        return "Idle"
    elif status == discord.Status.do_not_disturb:
        return "DnD"
    else:
        return "Offline"

def getG(game: discord.Game):
    """Returns a str of the Status

    Parameters
    ----------
    game: discord.Game
        The Discord Game"""
    if game is None:
        return "Not Playing Anything"
    else:
        return game

def getR(role: discord.Role, default: discord.Role):
    """Returns a (r, g, b) of the role

    Parameters
    ----------
    role: discord.Role
        The Users role
    default: discord.Role
        The Servers Default Role"""
    if role == default:
        return (
            255,
            255,
            255,
            255
        )
    else:
        return (
            role.colour.r,
            role.colour.g,
            role.colour.b,
            255
        )

class Splash():
    """Splash Creation And Management API

    Paramaters
    ----------
    WebsitePath: str
        Configs["Splash Site"]
    BotPath: str
        self.bot.currentDIR"""

    def __init__(self, WebsitePath, BotPath, StatusColors={"online": (0, 221, 17), "offline": (114, 114, 114), "idle": (234, 149, 32), "dnd": (227, 0, 0), "outline": (67, 67, 67)}):
        self.WebsitePath = WebsitePath
        self.BotPath = BotPath
        self.SES = (62, 62, 74, 74)
        self.SC = StatusColors

    def Update(self, member: discord.Member):
        """Updates Splash

        .. note::
            I would not let all servers use this and only your main server.
            The reason why is memory usage will be extremely high.
            Also MultiServer Splash Support is not planned and won't be.

        Parameters
        ----------
        member: discord.Member
            The member that was updated/created"""

        # Set Directory To Default
        default = self.BotPath+"/files/"
        os.chdir(default)

        # Stop the letters from carrying on over off the banner
        # Members Name
        name = member.name
        if len(name) > 28:
            name = name[:28]+"..."
        # Members Games Name
        game = getG(member.game.name) if member.game is not None else ""
        if len(game) > 25:
            game = game[:22]+"..."

        # Setup Vars
        avatar = None
        banner = None
        fontName = None
        fontGame = None

        # First lets sorts the roles by ranking just incase!
        roles = sorted(member.roles, key=attrgetter('position'))
        # Run roles in reverse so that the highest ranking role goes first
        for role in reversed(roles):
            if role is not member.server.default_role:
                fontNameP = Path(default+role.name.lower()+"_font_name.ttf")
                fontGameP = Path(default+role.name.lower()+"_font_game.ttf")
                bannerP = Path(default+role.name.lower()+"_banner.png")
                avatarP = Path(default+role.name.lower()+"_avatar.png")
                # Check if there is a custom font for the name
                if fontNameP.exists() and fontName is None:
                    fontName = ImageFont.truetype(role.name.lower()+"_font_name.ttf", 16)
                # Check if there is a custom font for the game
                if fontGameP.exists() and fontGame is None:
                    fontGame = ImageFont.truetype(role.name.lower()+"_font_game.ttf", 16)
                # Check if there is a custom banner
                if bannerP.exists() and banner is None:
                    banner = Image.open(role.name.lower()+"_banner.png")
                # Check if there is a custom avatar
                if avatarP.exists() and avatar is None:
                    avatar = Image.open(role.name.lower()+"_avatar.png")
            else: # We have hit the last role. Let's make sure everything is working
                # If there isn't a custom avatar set default
                if avatar is None:
                    avatar = Image.open("default_avatar.png")
                # If there isn't a custom banner set default
                if banner is None:
                    banner = Image.open("default_banner.png")
                # If there isn't a custom name font set default
                if fontName is None:
                    fontName = ImageFont.truetype("default_font_name.ttf", 16)
                # If there isn't a custom game font set default
                if fontGame is None:
                    fontGame = ImageFont.truetype("default_font_game.ttf", 16)

        avatarSize = (70, 70)
        maskSize = (avatarSize[0]*3, avatarSize[1]*3)
        if member.avatar_url is not "":
            avreq = Request(member.avatar_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(avreq) as response, open(member.id+".png", 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            avatar = Image.open(member.id+".png")

        #background
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
        if game is not "":
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
        statusEllipse = ImageDraw.Draw(txt)
        st = getS(member.status)
        if st == "Online":
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["online"],
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
            statusEllipse.ellipse(
                xy=self.SES,
                fill=self.SC["offline"],
                outline=self.SC["outline"]
            )

        # Output
        out = Image.alpha_composite(banner, txt)

        # Check if the Path leads to a working directory if not, create one
        if os.path.exists(self.WebsitePath+"/members/") and os.path.isdir(self.WebsitePath+"/members/"):
            try:
                os.chdir(self.WebsitePath+"/members/")
            except Exception as E:
                print("{}".format(E))
        else:
            try: # Python3
                os.makedirs(name=self.WebsitePath+"/members/", exist_ok=True)
            except:
                try: # Python2
                    os.makedirs(name=self.WebsitePath+"/members/")
                except Exception as E:
                    print("ERROR: CREATING SPLASH SITE DIR: {}".format(E))
                    pass
                else:
                    os.chdir(self.WebsitePath+"/members/")
            else:
                print("DIR3: CREATED")
                os.chdir(self.WebsitePath+"/members/")

        # Save Splash
        try:
            os.chdir(self.WebsitePath+"/members/")
            out.save(member.id+".png")
        except Exception as E:
            print("{}".format(E))

        # Save Storage
        if member.avatar_url is not "":
            os.chdir(default)
            os.remove(member.id+".png")
        return member.id+".png"

    def Check(member: discord.Member):
        """Checks if the user has changed details since the last run

        .. warning::
            NOT SETUP

        Parameters
        ----------
        member: discord.Member
            The Discord Member"""
        return(member.id+".png") # For return this so that no problems are caused!

    def Remove(self, userID):
        os.chdir(self.WebsitePath+"/members")
        os.remove(userID+".png")

    def UpdateOld(self, uid: str, un: str, au: str, ga: str, st: str, rc):
        """Used to update and create Splashes

        Parameters
        ----------
        uid: str
            User ID
        un: str
            User Name
        au: str
            Avatar URL
        ga: str
            Game
        st: str
            Status
        rc: (r, g, b)
            Role Colour"""

        default = self.BotPath+"/cogs/utils/default"
        os.chdir(default)
        if len(ga) > 25:
            ga = ga[:22]+"..."
        if len(un) > 32:
            un = un[:32]+"..."
        # Font
        textFnt = ImageFont.truetype('font.ttf', 16)
        textFntB = ImageFont.truetype('font_bold.ttf', 16)
        textFntI = ImageFont.truetype('font_italic.ttf', 16)
        # Banner
        banner = Image.open("banner.png")
        banner_w, banner_h = banner.size
        #background
        background = Image.new('RGBA', banner.size, (0, 0, 0, 0))
        # Avatar
        avatarSize = (70, 70)
        maskSize = (avatarSize[0]*3, avatarSize[1]*3)
        if au is None:
            avatar = Image.open("avatar.png")
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
        text.line((80, 16, 380, 16), fill=(0, 0, 0, 175), width=20)
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
        os.chdir(self.WebsitePath+"/members")
        out.save(uid+".png")

        # Save Storage
        if au is not None:
            os.chdir(default)
            os.remove(uid+".png")
        return uid+".png"

