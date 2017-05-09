import io, os, shutil, discord
import PIL
from PIL import ImageFont, Image, ImageDraw
from urllib.request import Request, urlopen, URLopener

class Splash():
    """Splash Creation And Management API"""

    def __init__(self, WebsitePath, BotPath):
        self.WebsitePath = WebsitePath
        self.BotPath = BotPath

    def update(self, uid: str, un: str, au: str, ga: str, st: str, rc):
        """Used to update and create Splashes"""
        default = self.BotPath+"/cogs/utils/default"
        os.chdir(default)
        if len(ga) > 25:
            ga = ga[:22]+"..."
        if len(un) > 28:
            un = un[:28]+"..."
        if isinstance(st, discord.Status):
            print("True")
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
        # Output
        out = Image.alpha_composite(banner, txt)
        os.chdir(self.WebsitePath+"/members")
        out.save(uid+".png")

        # Save Storage
        if au is None:
            os.chdir(default)
            os.remove(uid+".png")
        return uid+".png"

    def remove(self, userID):
        os.chdir(self.WebsitePath+"/members")
        os.remove(userID+".png")

#TESTS!!!!!!!
def testDONOTRUNUNLESSMAIN():
    os.chdir("./default")
    default = os.getcwd()

    au = None
    au = "https://images.discordapp.net/avatars/179891973795086336/8dd27f5aee2f81cd480f11929a517233.webp?size=1024"
    uid = "179891973795086336"
    if au is not None:
        au = au.replace("webp", "png")
    st = "Online"
    un = "TagnumElite TagnumElite TagnumElite TagnumElite"
    ga = "Massive Effective Testive Extreme Digital Deluxe Ultimate Version"
    rc = (255, 186, 0)
    if len(ga) > 25:
        ga = ga[:22]+"..."
    if len(un) > 36:
        ga = ga[:22]+"..."
    if isinstance(st, discord.Status):
        print("True")
    # Font
    textFnt = ImageFont.truetype('font.ttf', 16)
    textFntB = ImageFont.truetype('font_bold.ttf', 16)
    textFntI = ImageFont.truetype('font_italic.ttf', 16)
    # Banner
    banner = Image.open("banner.png")
    banner_w, banner_h = banner.size
    #Text
    txt = Image.new('RGBA', banner.size, (255, 255, 255, 0))
    text = ImageDraw.Draw(txt)
    text.line((80, 16, 380, 16), fill=(0, 0, 0, 175), width=20)
    text.text((85,8), un, font=textFntB, fill=(rc[0], rc[1], rc[2], 255))
    text.line((80, 58, 270, 58), fill=(0, 0, 0, 175), width=20)
    text.text((84,50), ga, font=textFntI, fill=(255, 255, 255, 255))
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
    # Status
    statusEllipse = ImageDraw.Draw(txt)
    if st == "Online":
        statusEllipse.ellipse((0, 0, avatar_w+10, avatar_h+10), (0, 221, 17), (67, 67, 67))
        print("online")
    elif st == "Offline":
        statusEllipse.ellipse((10, 10,7, 80), (114, 114, 114), (67, 67, 67))
        print("offline")
    elif st == "Idle":
        statusEllipse.ellipse((10, 10, 80, 80), (234, 149, 32), (67, 67, 67))
        print("idle")
    elif st == "DnD":
        statusEllipse.ellipse((10, 10, 80, 80), (227, 0, 0), (67, 67, 67))
        print("dnd")
    else:
        statusEllipse.ellipse((5, 5, 80, 80), (67, 67, 67))
        print("error")
    app = Image.alpha_composite(banner, txt)
    app.paste(background, (0, 0), background)
    out = app.resize((splashS[0], splashS[1]), Image.ANTIALIAS)
    # Output
    out.save("test.png")

    # Save Storage
    if au is None:
        os.chdir(default)
        os.remove(uid+".png")
    return uid+".png"

if __name__ == "__main__":
    testDONOTRUNUNLESSMAIN()
