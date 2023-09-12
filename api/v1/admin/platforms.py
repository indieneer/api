from flask import Blueprint, request
from pymongo.errors import ServerSelectionTimeoutError

from middlewares.requires_auth import requires_auth
from services.database import Database as dbs
from slugify import slugify
from tools.http_utils import respond_success, respond_error

platforms_controller = Blueprint('platforms', __name__, url_prefix='/platforms')

PLATFORM_FIELDS = [
    "slug",
    "name",
    "enabled",
    "icon_url",
    "url"
]


@platforms_controller.route('/', methods=["POST"])
@requires_auth
def create_platform():
    db = dbs.client.get_database("indieneer")
    platforms = db["platforms"]

    data = request.get_json()

    new_platform = {key: data.get(key) for key in PLATFORM_FIELDS}
    new_platform["slug"] = slugify(new_platform["name"])

    try:
        result = platforms.insert_one(new_platform)
    except ServerSelectionTimeoutError as e:
        return respond_error(str(e), 500)

    new_platform["_id"] = str(result.inserted_id)

    return respond_success(new_platform, None, 201)
