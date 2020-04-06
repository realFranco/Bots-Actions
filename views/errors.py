# bot_actions/views/errors.py

from flask import Blueprint, render_template


errors = Blueprint('errors', __name__)

@errors.errorhandler(404)
def page_not_found():
    # note that we set the 404 status explicitly
    # print(e)
    return render_template('errors/error.html'), 404
