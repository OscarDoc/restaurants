import os
import random
import string
from daos import UserDAO, RestaurantDAO, MenuItemDAO
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   session as login_session, make_response)
from werkzeug import SharedDataMiddleware, secure_filename

# App constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILES = set(['png', 'jpg', 'jpeg', 'gif'])


# Initialize app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1 Megabyte
app.add_url_rule('/uploads/<filename>', 'uploaded_file', build_only=True)
app.wsgi_app = SharedDataMiddleware(
    app.wsgi_app, {'/uploads': app.config['UPLOAD_FOLDER']})

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
    return render_template(
        'publicrestaurants.html',
        restaurants=restaurants)


app.secret_key = 'super_insecure_key'
app.debug = False
if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000)
