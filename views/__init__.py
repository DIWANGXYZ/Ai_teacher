from flask import Blueprint

bp = Blueprint('views', __name__)

from . import order, payment, product, purchased_book, user


