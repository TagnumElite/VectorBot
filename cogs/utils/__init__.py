"""VectorBot Utils
-----------------
This is just for documentation!"""

from .checks import Checks
from .databases import DBC, MessageDB, GuildDB, UserDB, TeamDB, ConfigDB
from .draw import Splash
from .emailmanager import Email
#from .formats import * # I have not uploaded this yet
#from .maps import * # I have not uploaded this yet
#from .paginator import * # I have not uploaded this yet
from .parser import Parser, MemberParser, MessageParser, GuildParser, ConfigParser, ChannelParser, RoleParser, EmojiParser
#from .salt import * # I have not uploaded this yet
from .steammanager import Player, SteamRep, SteamY

class Exceptions(Exception):
    """"""
    pass

class DBError(Exceptions):
    """Base Error Class"""

class DoesNotExists(DBError):
    """Object doesn't exists"""
    pass

class Exists(DBError):
    """Object Exists"""
    pass

class CouldNotCreate(DBError):
    """Object could not be created error"""
    pass
