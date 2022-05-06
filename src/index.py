
from flask import Blueprint, app,redirect,url_for

_index = Blueprint("_index", __name__,)

@_index.route('/')
def index_page():
    return redirect(url_for('auth.login'))