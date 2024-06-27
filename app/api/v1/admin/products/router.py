from flask import Blueprint

products_controller = Blueprint('products', __name__, url_prefix='/products')
comments_controller = Blueprint('comments', __name__, url_prefix='/comments')