from flask import Flask, g
from flask_babel import Babel, gettext
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from geopy.geocoders import GoogleV3, Nominatim

from constants.app_config import SECRET_KEY, DB_URL, GROUPS_ENABLED
from constants.config import GOOGLE_API
from constants.constants import DayOfWeek
from libs.SecureAdmin import get_admin
from src.misc import format_date_time, is_admin, get_cookie, format_time
from flask_googlemaps import GoogleMaps


def get_app(name: str) -> Flask:
    res = Flask(name)
    res.config['SECRET_KEY'] = SECRET_KEY
    res.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    res.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    res.config['GOOGLEMAPS_KEY'] = GOOGLE_API

    # jinja env variables
    res.jinja_env.globals.update(format_date_time=format_date_time)
    res.jinja_env.globals.update(groups_enabled=GROUPS_ENABLED)
    res.jinja_env.globals.update(format_time=format_time)
    res.jinja_env.globals.update(get_day_of_week=DayOfWeek.get_name)
    res.jinja_env.globals.update(len=len)
    res.jinja_env.globals.update(is_admin=is_admin)
    res.jinja_env.globals.update(set=set)
    res.jinja_env.globals.update(get_cookie=get_cookie)

    return res


app = get_app(__name__)

bootstrap = Bootstrap(app)

db = SQLAlchemy(app)

google_api = GoogleV3(api_key=GOOGLE_API)
nominatim = Nominatim(user_agent="sport")

login_manager = LoginManager(app)
login_manager.login_view = 'login_route'
login_manager.login_message_category = 'warning'
login_manager.login_message = gettext("Please log in to view this page.")
login_manager.localize_callback = gettext

babel = Babel(app)

socketIO = SocketIO(app)

admin = get_admin(app, db)

sessions = {}

google_maps = GoogleMaps(app)


@babel.localeselector
def get_locale():
    return get_cookie('language', 'ru')


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


def create_tables():
    # these are necessary imports for db to register
    from libs.models.Chat import Chat
    from libs.models.ChatMember import ChatMember
    from libs.models.ChatNotification import ChatNotification
    from libs.models.Event import Event
    from libs.models.EventMember import EventMember
    from libs.models.Friend import Friend
    from libs.models.Group import Group
    from libs.models.GroupMember import GroupMember
    from libs.models.Invitation import Invitation
    from libs.models.Message import Message
    from libs.models.PlayTime import PlayTime
    from libs.models.User import User
    from libs.models.UserVideos import UserVideos
    from libs.models.AddressCaches import Address, Location, LocationToAddress
    from libs.models.EventPlayTimes import EventPlayTimes
    db.create_all()
