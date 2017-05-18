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
        return game.name

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
        self.bot.currentDIR
    StatusColors: Optional[dict]
        Default: {
            "online": (0, 221, 17),
            "offline": (114, 114, 114),
            "idle": (234, 149, 32),
            "dnd": (227, 0, 0),
            "outline": (67, 67, 67)}"""

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
        
        To make custom roles splashes create files named:
        `admin_avatar.png` | `admin_banner.png`
        `admin_font_name.ttf` | `admin_font_game.ttf`
        
        To make Custom Users splashes files have to be named:
        `tagnumelite__avatar.png` | `tagnumelite__banner.png`
        `tagnumelite__font__name.ttf` | `tagnumelite__font__game.ttf`
        Or even better:
        `tagnumelite__9339__avatar.png` | `tagnumelite__9339__banner.png`
        `tagnumelite__9339__font__name.ttf` | `tagnumelite__9339__font__game.ttf`
        
        .. note::
            Files must be in lowercase otherwise it fails to find it!

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
        game = getG(member.game)
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
                avatarP = Path(default+role.name.lower()+"_avatar.png")
                bannerP = Path(default+role.name.lower()+"_banner.png")
                fontNameP = Path(default+role.name.lower()+"_font_name.ttf")
                fontGameP = Path(default+role.name.lower()+"_font_game.ttf")
                # Check if there is a custom avatar for the role
                if avatarP.exists() and avatar is None:
                    avatar = Image.open(role.name.lower()+"_avatar.png")
                # Check if there is a custom banner for the role
                if bannerP.exists() and banner is None:
                    banner = Image.open(role.name.lower()+"_banner.png")
                # Check if there is a custom font for the name for the role
                if fontNameP.exists() and fontName is None:
                    fontName = ImageFont.truetype(role.name.lower()+"_font_name.ttf", 16)
                # Check if there is a custom font for the game for the role
                if fontGameP.exists() and fontGame is None:
                    fontGame = ImageFont.truetype(role.name.lower()+"_font_game.ttf", 16)
            else: # We have hit the last role. Let's make sure everything is working
                # Now we check if a user themself has a custom splash
                # NOTE: Custom banners to each users must have two __ instead of one _
                # This is to stop users from getting the the custom role splashes by
                # changing their name!
                avatarP = Path(default+member.name.lower()+"__avatar.png")
                bannerP = Path(default+member.name.lower()+"__banner.png")
                fontNameP = Path(default+member.name.lower()+"__font_name.ttf")
                fontGameP = Path(default+member.name.lower()+"__font_game.ttf")
                # Check if the user is using a discriminator
                avatarDP = Path(
                    default+member.name.lower()+"__"+member.discriminator+"__avatar.png"
                )
                bannerDP = Path(
                    default+member.name.lower()+"__"+member.discriminator+"__banner.png"
                )
                fontNameDP = Path(
                    default+member.name.lower()+"__"+member.discriminator+"__font_name.ttf"
                )
                fontGameDP = Path(
                    default+member.name.lower()+"__"+member.discriminator+"__font_game.ttf"
                )
                # Check if there is a custom avatar for the member
                if avatarP.exists():
                    avatar = Image.open(member.name.lower()+"__avatar.png")
                elif avatarDP.exists():
                    avatar = Image.open(member.name.lower()+"__"+member.discriminator+"__avatar.png")
                elif avatar is None: # If there isn't a custom avatar set default
                    avatar = Image.open("default_avatar.png")
                # Check if there is a custom banner for the member
                if bannerP.exists():
                    banner = Image.open(member.name.lower()+"__banner.png")
                elif bannerDP.exists():
                    banner = Image.open(member.name.lower()+"__"+member.discriminator+"__banner.png")
                elif banner is None: # If there isn't a custom banner set default
                    banner = Image.open("default_banner.png")
                # Check if there is a custom name font for the member
                if fontNameP.exists():
                    fontName = ImageFont.truetype(member.name.lower()+"__font_name.ttf", 16)
                elif fontNameDP.exists():
                    fontName = ImageFont.truetype(member.name.lower()+"__"+member.discriminator+"__font_name.ttf", 16)
                elif fontName is None: # If there isn't a custom name font set default
                    fontName = ImageFont.truetype("default_font_name.ttf", 16)
                # Check if there is a custom game font for the member
                if fontGameP.exists():
                    fontGame = ImageFont.truetype(member.name.lower()+"__font_game.ttf", 16)
                elif fontGameDP.exists():
                    fontGame = ImageFont.truetype(member.name.lower()+"__"+member.discriminator+"__font_game.ttf", 16)
                elif fontGame is None: # If there isn't a custom game font set default
                    fontGame = ImageFont.truetype("default_font_game.ttf", 16)
        #
        avatarSize = (70, 70)
        maskSize = (avatarSize[0]*3, avatarSize[1]*3)

        # If the member has an avatar get that instead!
        if member.avatar_url is not "":
            avreq = Request(member.avatar_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(avreq) as response, open(member.id+".png", 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            avatar = Image.open(member.id+".png")

        #background
        background = Image.new('RGBA', banner.size, (0, 0, 0, 0))
        banner_w, banner_h = banner.size
        #
        mask = Image.new('L',  maskSize, 0)
        #
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + maskSize, fill=255)
        #
        mask = mask.resize(avatar.size, Image.ANTIALIAS)
        #
        avatar.putalpha(mask)
        avatar.thumbnail(avatarSize, Image.ANTIALIAS)
        avatar_w, avatar_h = avatar.size
        #
        a_offset = (int(5), int((banner_h-avatar_h)/2))
        #
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
        text.line(
            (80, 58, 270, 58),
            fill=(0, 0, 0, 175),
            width=20
        )
        text.text(
            (84,50),
            game if getS(member.status) is not "Offline" else "Currently Offline",
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

        # Delete the members avatar if we no longer need it!
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

    def Remove(self, userID: int):
        """Removes a users banner/splash

        Parameters
        ----------

        userID: str
            The ID of the user"""
        os.chdir(self.WebsitePath+"/members")
        os.remove(userID+".png")
