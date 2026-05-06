from flask import Blueprint
bp = Blueprint('reception', __name__)
from app.reception import routes
