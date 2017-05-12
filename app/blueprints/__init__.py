from flask import Blueprint
bp = Blueprint("bp", __name__)
from . import views
