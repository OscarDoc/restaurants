import os
import random
import string
from daos import UserDAO, RestaurantDAO, MenuItemDAO
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   session as login_session, make_response)

# App constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILES = set(['png', 'jpg', 'jpeg', 'gif'])


# Initialize app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1 Megabyte
app.add_url_rule('/uploads/<filename>', 'uploaded_file', build_only=True)

# Instantiate our Data Access Objects
rst_dao = RestaurantDAO()



@app.route('/')
@app.route('/restaurants')
def show_restaurants():
    """Returns an html page with a listing of all the restaurants.

    Returns:
        If there's a logged user, the returned html contains a link to create
        new restaurants.

    """
    restaurants = rst_dao.get_all_restaurants()
    return restaurants[0].name


app.secret_key = 'super_insecure_key'
app.debug = False
