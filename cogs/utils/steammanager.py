"""
What?
No.
What do you mean it escaped?
Yes.
Damnit Yes/No Buttom! TELL ME!
No.
ARRRRRRRRRRRGGGG
"""

import discord, asyncio
import random, steam
import json, socket
from steam import WebAPI, SteamID
from discord.ext import commands
import urllib, requests

class Player():
    """Preperation!"""

    def __init__(self, username):
        self.username = username

class SteamRep():
    """A Object that imports data from SteamRep.com!
    This functionality is not setup yet.

    Parameters
    ----------
    api_key : str (Optional)
        API Key from SteamRep!"""
    url = ""

    def __init__(self, APIKey=None):
        self.API_KEY = APIKey

    def getUser(self, user):
        """Gets the user from the SteamRep Website"""
        userSafe = urllib.parse.quote(user, safe='')
        r = requests.get('https://steamrep.com/search?q={}'.format(userSafe))
        pass


class SteamY:
    """Steam Functionality"""

    def __init__(self, api="LOL NO"):
        self.api = WebAPI(key=api)

    def getID64(self, string):
        return SteamID(string).as_64

    def getID32(self, string):
        return SteamID(string).as_32

    def getID(self, string):
        return SteamID(string).id

    def getBans(self, ID64):
        """Returns JSON formated PlayerBans"""
        if self.api is None:
            return False
        else:
            return self.api.ISteamUser.GetPlayerBans(steamids=ID64)['players'][0]

    def getUsername(self, ID64):
        """Returns Player Persona Name from a Steam ID 64"""
        if self.api is None:
            return False
        else:
            return self.api.ISteamUser.GetPlayerSummaries(steamids=ID64)['response']['players'][0]['personaname']

    def getProfile(self, ID64):
        """Returns Player Persona Name from a Steam ID 64"""
        if self.api is None:
            return False
        else:
            return self.api.ISteamUser.GetPlayerSummaries(steamids=ID64)['response']['players'][0]

    def getFriends(self, ID64):
        """Returns Player Persona Name from a Steam ID 64"""
        if self.api is None:
            return False
        else:
            return self.api.ISteamUser.GetFriendList(steamid=ID64)['friendslist']['friends']

    def hasBeenVACBanned(self, ID64):
        """Checks if player has an VAC banned"""
        if self.getBans(ID64)['NumberOfVACBans'] > 0:
            return True
        else:
            return False

    def hasBeenGameBanned(self, ID64):
        """Checks if player has a game banned"""
        if self.getBans(ID64)['NumberOfGameBans'] > 0:
            return True
        else:
            return False

    def hasBeenEcoBanned(self, ID64):
        """Checks if player has an Economy banned"""
        if self.getBans(ID64)['EconomyBan'] != 'none':
            return True
        else:
            return False

    def isComBaned(self, ID64):
        """Checks if player is Community Banned"""
        return self.getBans(ID64)['CommunityBanned']

    def isVACBaned(self, ID64):
        """Checks if player is VAC Banned"""
        return self.getBans(ID64)['VACBanned']

    def bannedFriends(self, ID64):
        """Returns an array of banned friends!"""
        print("getting banned friends")
        friends = self.getFriends(ID64)
        banned = []
        counter = 0
        for friend in friends:
            counter = counter + 1
            print(counter)
            if self.hasBeenVACBanned(friend['steamid']):
                banned.append(friend['steamid'])
        return banned
