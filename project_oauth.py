"""This file creates a Flask Blueprint with our OAuth routes, which are then
imported and mounted by our server."""

import httplib2
import json
import requests
from daos import UserDAO
from flask import (abort, Blueprint, flash, make_response, redirect, request,
                   session as login_session, url_for)
from oauth2client.client import (flow_from_clientsecrets, FlowExchangeError,
                                 OAuth2Credentials)


# Load our Google secrets
CLIENT_ID = json.loads(
    open('client_secrets_gc.json', 'r').read())['web']['client_id']
usr_dao = UserDAO()

# Create blueprint 'oauth' to be mounted from project.py
oauth = Blueprint('oauth', __name__, template_folder='templates')


# Helper functions

def json_response(http_code, text):
    """Creates a response object.

    Args:
        http_code: HTTP status code.
        text: string to be sents as json.

    Returns:
        A response instance with the status 'http_code' and the body 'text'.

    """
    response = make_response(json.dumps(text), http_code)
    response.headers['Content-type'] = 'application/json'
    return response


# Oauth routes

@oauth.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Logins through Facebook's OAuth service.

    Returns:
        An html string with a success message, or an HTTP error.

    """
    if request.args.get('state') != login_session['state']:
        return json_response(401, 'Invalid state paremeter.')

    access_token = request.data

    app_id = json.loads(
        open('client_secrets_fb.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('client_secrets_fb.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.5/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = usr_dao.get_user_id(login_session['email'])
    if not user_id:
        user_id = usr_dao.add_user(
            login_session['username'],
            login_session['email'],
            login_session['picture'])
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are now logged in as %s" % login_session['username'], "success")
    return output


# Login with Google Connect
@oauth.route('/gconnect', methods=['POST'])
def gconnect():
    """Logins through Google's OAuth service.

    Returns:
        An html string with a success message, or an HTTP error.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return json_response(401, 'Invalid state paremeter.')
    code = request.data
    try:
        ouath_flow = flow_from_clientsecrets(
            'client_secrets_gc.json', scope='')
        ouath_flow.redirect_uri = 'postmessage'
        credentials = ouath_flow.step2_exchange(code)
    except FlowExchangeError:
        return json_response(401, 'Failed to upgrade the authorization code.')

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there is an error, abort
    if result.get("error") is not None:
        return json_response(500, result.get("error"))

    # Verify that token is used for the indended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return json_response(401, 'Token and given user IDs don\'t match.')

    # Verify that token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        return json_response(401, 'Token and app client IDs don\'t match.')

    # Check if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None\
            and gplus_id == stored_gplus_id:
        response = json_response(200, 'Current user already connected')

    # Store access token in the session for later use
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists, if not make a new one
    user_id = usr_dao.get_user_id(data['email'])
    if not user_id:
        user_id = usr_dao.add_user(
            data['name'],
            data['email'],
            data['picture'])
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash('You are now logged in as %s' % login_session['username'], 'success')
    return output


# Disconnect based on provider
@oauth.route('/disconnect')
def disconnect():
    """Disconnects the user, removing its session and calling any
    vendor-specific code to revoke the access token.

    Returns:
        A redirect to main page.

    """
    if 'provider' in login_session:
        # First revoke the provider's access token
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        # Then delete the user's session
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_restaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_restaurants'))


# Disconnect Facebook, revoking user's token and ressetting its session
@oauth.route('/fbdisconnect')
def fbdisconnect():
    """Revokes user's Facebook access token."""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    # Call and check everything went fine
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


# Disconnect Google, revoking user's token and ressetting its session
@oauth.route('/gdisconnect')
def gdisconnect():
    """Revokes user's Google access token."""
    # Abort if not connected
    credentials = login_session.get('credentials')
    if credentials is None:
        flash("Current user not connected", "error")
        return json_response("Current user not connected", 401)

    credentials = OAuth2Credentials.from_json(credentials)
    # Execute HTTP GET to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    # Call and check everything went fine
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        flash("Failed to revoke user's token", "error")
        return json_response("Failed to revoke user's token", 400)
