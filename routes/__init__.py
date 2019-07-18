from flask import Blueprint
routes = Blueprint('routes', __name__)

from .components import *
from .reportees import *