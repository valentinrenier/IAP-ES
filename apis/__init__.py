from flask import Blueprint
from flask_restx import Api, Namespace

from .api import api as api
from .ui import api as ui
from .auth import api as auth

blueprint = Blueprint('endpoints', __name__)

api = Api(version="1.0", title="IAP API", description="API for the IAP", prefix="/")

api.add_namespace(api)
api.add_namespace(ui)
api.add_namespace(auth)