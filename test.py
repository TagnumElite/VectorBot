#!/usr/bin/python3.6
# TESTY TESTY!!!
# This file will change over time because I test things here. DUH

import sys, getopt
import io
import os
import shutil
import discord
import PIL
from PIL import ImageFont, Image, ImageDraw
from urllib.request import Request, urlopen, URLopener
from operator import attrgetter
from pathlib import Path

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

def main():
    pass

if __name__ == "__main__":
    draw()
    main()
