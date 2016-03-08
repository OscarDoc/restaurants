import os
import random
import string
from daos import UserDAO, RestaurantDAO, MenuItemDAO
from flask import Flask, render_template, request, redirect, url_for, flash, session as login_session, make_response
from werkzeug import SharedDataMiddleware, secure_filename
from project_api_endpoints import api_json, api_atom
from project_oauth import oauth

# App constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILES = set(['png', 'jpg', 'jpeg', 'gif'])


# Initialize app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 # 1 Megabyte
app.add_url_rule('/uploads/<filename>', 'uploaded_file', build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})
# Register blueprints from project_api_endpoint.py and project_oauth.py
app.register_blueprint(api_json)
app.register_blueprint(api_atom)
app.register_blueprint(oauth)


# Instantiate our Data Access Objects
usr_dao = UserDAO()
rst_dao = RestaurantDAO()
mnu_dao = MenuItemDAO()


# Helper functions


def is_logged():
	return 'username' in login_session


def is_owners_session(obj):
	return is_logged() and obj.user_id == login_session['user_id']


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_FILES


# Web routes

# Login route
@app.route('/login')
def show_login():
	# Redirect users who are already logged but go to the login page
	if is_logged():
		return redirect(url_for('show_restaurants'))

	# Create anti-forgery state token
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)


# Our index, shows a list of all the restaurants, plus restaurant create/edit/delete links
@app.route('/')
@app.route('/restaurants')
def show_restaurants():
	restaurants = rst_dao.get_all_restaurants()

	if not is_logged():
		return render_template(
			'publicrestaurants.html',
			restaurants = restaurants)
	else:
		return render_template(
			'restaurants.html',
			restaurants = restaurants,
			username = login_session['username'])


# Form to create a new restaurant
@app.route('/restaurants/new',
	methods=['GET', 'POST'])
def new_restaurant():
	if not is_logged():
		return redirect('login')

	if request.method == 'GET':
		return render_template('newrestaurant.html',
			username = login_session['username'])

	# Else: it's a POST
	new_name = request.form['name'].strip()
	rst_dao.add_restaurant(new_name, login_session['user_id'])
	flash('Restaurant %s succesfully added' % new_name, 'success')
	return redirect(url_for('show_restaurants'))


# Form to edit an existing restaurant
@app.route('/restaurants/<int:restaurant_id>/edit',
	methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
	if not is_logged():
		return redirect('login')

	restaurant = rst_dao.get_restaurant(restaurant_id)
	if not is_owners_session(restaurant):
		return "<script>function f(){alert('You are not authorized to edit this restaurant.');};</script><body onload='f()'></body>"

	if request.method == 'GET':
		return render_template('editrestaurant.html', restaurant = restaurant)

	# Else: it's a POST
	new_name = request.form['name'].strip()
	rst_dao.set_restaurant_name(restaurant_id, new_name)
	flash('Restaurant name succesfully changed to %s' %new_name, 'success')
	return redirect(url_for('show_restaurants'))


# Form to delete a restaurant
@app.route('/restaurants/<int:restaurant_id>/delete',
	methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
	if not is_logged():
		return redirect('login')

	restaurant = rst_dao.get_restaurant(restaurant_id)
	if not is_owners_session(restaurant):
		return "<script>function f(){alert('You are not authorized to delete this restaurant.');};</script><body onload='f()'></body>"

	if request.method == 'GET':		
		return render_template(
			'deleterestaurant.html', 
			restaurant = restaurant, 
			username = login_session['username'])

	# Else: it's a POST
	rst_dao.delete_restaurant(restaurant_id)
	flash('Restaurant %s deleted' %restaurant.name, 'success')
	return redirect(url_for('show_restaurants'))


# List of the menu items in a restaurant, plus item create/edit/delete links
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu')
def show_menu(restaurant_id):
	restaurant = rst_dao.get_restaurant(restaurant_id)
	items = mnu_dao.get_menu_by_restaurant(restaurant_id)
	creator = usr_dao.get_user(restaurant.user_id)

	# If logged user is the creator, show owner's page
	if is_owners_session(restaurant):
		return render_template(
			'menu.html', 
			restaurant = restaurant, 
			items = items,
			creator = creator,
			username = login_session['username'])
	# Else, show public page
	else:
		return render_template(
			'publicmenu.html', 
			restaurant = restaurant, 
			items = items,
			creator = creator)


# Form to create a new menu item in the restaurant
@app.route('/restaurants/<int:restaurant_id>/new/',
	methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
	if not is_logged():
		return redirect('login')

	restaurant = rst_dao.get_restaurant(restaurant_id)
	if not is_owners_session(restaurant):
		return "<script>function f(){alert('You are not authorized to add a menu item.');};</script><body onload='f()'></body>"

	if request.method == 'GET':
		return render_template(
			'newmenuitem.html', 
			restaurant_id = restaurant_id, 
			restaurant_name=restaurant.name,
			username = login_session['username'])
	
	# Else it's a POST
	new_name = request.form['name'].strip()
	mnu_dao.add_menu_item(restaurant_id, new_name, restaurant.user_id)
	flash('New menu item created', 'success')

	return redirect(url_for('show_menu', restaurant_id = restaurant_id))


# Form to edit an existing menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
	methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
	if not is_logged():
		return redirect('login')

	item = mnu_dao.get_menu(menu_id)
	if not is_owners_session(item):
		return "<script>function f(){alert('You are not authorized to edit this menu item.');};</script><body onload='f()'></body>"

	if request.method == 'GET':
		restaurant = rst_dao.get_restaurant(restaurant_id)
		return render_template('editmenuitem.html',
								restaurant = restaurant,
								item = item,
								username = login_session['username'])

	# Else it's a POST
	new_name = request.form['name'].strip()
	cur_name = mnu_dao.get_menu_name(menu_id)
	if new_name != '' and new_name != cur_name:
		mnu_dao.set_menu_name(menu_id, new_name)
		flash('Menu item name succesfully changed to %s' %new_name, 'success')

	new_description = request.form['description'].strip()
	cur_description = mnu_dao.get_menu_description(menu_id)
	if new_description != '' and new_description != cur_description:
		mnu_dao.set_menu_description(menu_id, new_description)
		flash('Menu item description succesfully changed to %s' %new_description, 'success')

	new_price = request.form['price'].strip()
	cur_price = mnu_dao.get_menu_price(menu_id)
	if new_price != '' and new_price != cur_price:
		mnu_dao.set_menu_price(menu_id, new_price)
		flash('Menu item price succesfully changed to %s' %new_price, 'success')

	new_course = request.form['course']
	cur_course = mnu_dao.get_menu_course(menu_id)
	if new_course != '' and new_course != cur_course:
		mnu_dao.set_menu_course(menu_id, new_course)
		flash('Menu item course succesfully changed to %s' %new_course, 'success')

	new_image = request.files['image']
	if new_image and allowed_file(new_image.filename):
		# Prepend the menu_id to the name to make it unique
		filename = `menu_id` + secure_filename(new_image.filename)
		new_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		mnu_dao.set_menu_image(menu_id, filename)
		flash('Menu item image succesfully changed', 'success')
		#return redirect(url_for('uploaded_file', filename=filename))

	return redirect(url_for('show_menu', restaurant_id = restaurant_id))



# Form to delete an existing menu item
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
	methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
	if not is_logged():
		return redirect('login')

	menu = mnu_dao.get_menu(menu_id)
	if not is_owners_session(menu):
		return "<script>function f(){alert('You are not authorized to delete this menu item.');};</script><body onload='f()'></body>"

	if request.method == 'GET':
		rst_name = rst_dao.get_restaurant(restaurant_id).name
		return render_template(
			'deletemenuitem.html',
			menu = menu, 
			restaurant_name = rst_name,
			username = login_session['username'])

	# Else it's a POST
	mnu_dao.delete_menu(menu_id)
	flash('Menu item deleted', 'success')
	return redirect(url_for('show_menu', restaurant_id = restaurant_id))


#if __name__ == '__main__':
app.secret_key = 'super_insecure_key'
app.debug = True
#app.run(host = '0.0.0.0', port = 5000)