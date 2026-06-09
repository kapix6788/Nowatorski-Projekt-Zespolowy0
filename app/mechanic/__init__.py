from flask import Blueprint
bp = Blueprint('mechanic', __name__)
from app.mechanic import routes