"""VectorBot Cogs
-----------------
This is just for documentation!"""

import .checks
from .config import Config, ServerConfig
from .databases import DBC, updateTypes, errorType, MessageDB, UserDB, ServerDB, EmojisDB, RolesDB, MembersDB, ChannelsDB, ConfigDB
from .draw import Splash
from .emailmanager import Email
#from .formats import *
#from .maps import *
#from .paginator import *
import .parser
#from .salt import *
from .steammanager import Player, SteamRep, SteamY
