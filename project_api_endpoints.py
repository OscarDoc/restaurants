from flask import Blueprint, render_template, abort, jsonify, request, url_for
from werkzeug.contrib.atom import AtomFeed
from daos import UserDAO, RestaurantDAO, MenuItemDAO
from datetime import datetime


# Create blueprints to access them from project.py
api_json = Blueprint('api_json', __name__, template_folder='templates')
api_atom = Blueprint('api_atom', __name__, template_folder='templates')



usr_dao = UserDAO()
rst_dao = RestaurantDAO()
mnu_dao = MenuItemDAO()


# JSON Endpoints 

@api_json.route('/restaurants/JSON')
def restaurants_json():
	restaurants = rst_dao.get_all_restaurants()
	return jsonify(Restaurants=[r.serialize for r in restaurants])


@api_json.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurant_menu_json(restaurant_id):
	items = mnu_dao.get_menu_by_restaurant(restaurant_id)
	return jsonify(MenuItems=[i.serialize for i in items])


@api_json.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menu_item_json(restaurant_id, menu_id):
	item = mnu_dao.get_menu(menu_id)
	return jsonify(MenuItem=item.serialize)


# Atom Endpoints

@api_atom.route('/restaurants/ATOM')
def restaurants_atom():
	feed = AtomFeed('Restaurants', feed_url=request.url, url=url_for('show_restaurants'))

	restaurants = rst_dao.get_all_restaurants()
	for r in restaurants:
		feed.add(r.name, unicode(r.name),
                 content_type='html',
                 id=r.id,
                 url=url_for('show_menu', restaurant_id=r.id),
                 updated=datetime.today())
	return feed.get_response()


@api_atom.route('/restaurants/<int:restaurant_id>/menu/ATOM')
def restaurant_menu_atom(restaurant_id):
	restaurant = rst_dao.get_restaurant(restaurant_id)
	feed = AtomFeed('%s menu' %restaurant.name,
		feed_url=request.url,
		url=url_for('show_menu', restaurant_id = restaurant_id))

	items = mnu_dao.get_menu_by_restaurant(restaurant_id)
	for i in items:
		feed.add(i.name, unicode(i.description),
                 content_type='html',
                 id=i.id,
                 url=url_for('show_menu', restaurant_id=restaurant_id),
                 updated=datetime.today())
	return feed.get_response()


@api_atom.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/ATOM')
def menu_item_atom(restaurant_id, menu_id):
	restaurant = rst_dao.get_restaurant(restaurant_id)
	item = mnu_dao.get_menu(menu_id)

	feed = AtomFeed(item.name,
		feed_url=request.url,
		url=url_for('show_menu', restaurant_id = restaurant_id))

	feed.add(item.name, unicode(item.description),
             content_type='html',
             id=item.id,
             url=url_for('show_menu', restaurant_id=restaurant_id),
             updated=datetime.today())
	return feed.get_response()