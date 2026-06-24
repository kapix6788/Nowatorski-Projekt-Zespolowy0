from flask import Blueprint
bp = Blueprint('boss', __name__)
from app.boss import routes
