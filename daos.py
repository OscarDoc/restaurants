from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User


class GenericDAO():
    """This class implements common functionalities for all Data-Access
    Objects"""

    def __init__(self):
        """Initializes a session to our sqlite database"""

        engine = create_engine('sqlite:///restaurantmenu.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()


    def close(self):
        """Closes the connection opened when the instance was initialized. The
        object can't be used afterwards.
        """

        self.session.close()


    def persist(self, obj):
        """Commits to the database the changes made to the obj Object.
        
        Args:
            obj: Object instance to be committed
        """

        self.session.add(obj)
        self.session.commit()


    def discontinue(self, obj):
        """Deletes an object from the database.
        
        Args:
            obj: Object to be removed from the DB
        """

        self.session.delete(obj)
        self.session.commit()



class UserDAO(GenericDAO):

    def get_user(self, user_id):
        """Gets the user with the primary key user_id.
        
        Args:
            user_id: Id (PK) of the user to retrieve

        Returns:
            The instance that represents the user
        """

        return self.session.query(User).filter_by(id = user_id).one()


    def get_user_id(self, email):
        """Gets the id (PK) of the user with the email parameter.
        
        Args:
            email: email of the user to retrieve. Note that emails are unique.

        Returns:
            The DB id of the row with the user info.
        """

        try:
            return self.session.query(User).filter_by(email = email).one().id
        except:
            return None


    def add_user(self, name, email, picture):
        """Creates a user with the parameters passed
        
        Args:
            name: name of the user
            email: email of the user. Note that emails are unique.
            picture: picture of the user

        Returns:
            The DB id of the row with the user info.
        """

        new_user = User(name = name, email = email, picture = picture)
        self.persist(new_user)
        return self.get_user_id(email)



class RestaurantDAO(GenericDAO):

    def get_restaurant(self, rest_id):
        """Gets the restaurant with the primary key rest_id.
        
        Args:
            rest_id: Id (PK) of the restaurant to retrieve

        Returns:
            The instance that represents the restaurant.
        """

        return self.session.query(Restaurant).filter_by(id = rest_id).one()


    def get_first_restaurant(self):
        """Retrieves the first restaurant found in the DB.

        Returns:
            The instance that represents the restaurant.
        """
        return self.session.query(Restaurant).first()


    def get_all_restaurants(self):
        """Retrieves all the restaurants stored in the DB.

        Returns:
            A list with all the restaurants, in no particular order.
        """

        return self.session.query(Restaurant).all()


    def set_restaurant_name(self, rest_id, new_name):
        """Updates a restaurant's name.
        
        Args:            
            rest_id: id of the restaurant to modify
            new_name: new name of the restaurant
        """

        restaurant = self.get_restaurant(rest_id)
        if restaurant:
            restaurant.name = new_name
            self.persist(restaurant)


    def add_restaurant(self, new_name, user_id):
        """Creates a restaurant with the parameters passed
        
        Args:
            new_name: name of the restaurant
            user_id: owner of the restaurant. Foreign Key of Users.
        """

        new_restaurant = Restaurant(name = new_name, user_id = user_id)
        self.persist(new_restaurant)


    def delete_restaurant(self, rest_id):
        """Deletes a restaurant from the DB.
        
        Args:            
            rest_id: id of the restaurant to delete
        """

        restaurant = self.get_restaurant(rest_id)
        if restaurant:
            self.discontinue(restaurant)



class MenuItemDAO(GenericDAO):

    def get_menu(self, menu_id):
        """Gets the menu item with the primary key menu_id.
        
        Args:
            menu_id: Id (PK) of the menu item to retrieve

        Returns:
            The instance that represents the menu item.
        """

        return self.session.query(MenuItem).filter_by(id=menu_id).one()


    def get_menu_by_restaurant(self, rest_id):
        """Retrieves the menu of a restaurant.
        
        Args:
            rest_id: Id of the restaurant to filter the results

        Returns:
            A list with all the menu items of the restaurant, in no particular
            ordering.
        """

        return self.session.query(MenuItem).filter_by(restaurant_id = rest_id).all()


    def get_menu_name(self, menu_id):
        """Retrieves the name of the menu item with the id passed.
        
        Args:
            menu_id: Id of the menu item to find

        Returns:
            The instance that represents the menu item.
        """

        menu = self.get_menu(menu_id)
        return menu.name


    def get_menu_description(self, menu_id):
        """Retrieves the description of the menu item with the id passed.
        
        Args:
            menu_id: Id of the menu item to find

        Returns:
            The instance that represents the menu item.
        """

        menu = self.get_menu(menu_id)
        return menu.description


    def get_menu_price(self, menu_id):
        """Retrieves the price of the menu item with the id passed.
        
        Args:
            menu_id: Id of the menu item to find

        Returns:
            The instance that represents the menu item.
        """

        menu = self.get_menu(menu_id)
        return menu.price


    def get_menu_course(self, menu_id):
        """Retrieves the course of the menu item with the id passed.
        
        Args:
            menu_id: Id of the menu item to find

        Returns:
            The instance that represents the menu item.
        """

        menu = self.get_menu(menu_id)
        return menu.course


    def get_menu_image(self, menu_id):
        """Retrieves the image filename of the menu item with the id passed.
        
        Args:
            menu_id: Id of the menu item to find

        Returns:
            The instance that represents the menu item.
        """

        menu = self.get_menu(menu_id)
        return menu.filename


    def set_menu_name(self, menu_id, new_name):
        """Updates a menu item's image.
        
        Args:            
            menu_id: id of the menu item to modify
            new_name: new name of the menu item
        """

        menu = self.get_menu(menu_id)
        if menu:
            menu.name = new_name
            self.persist(menu)


    def set_menu_description(self, menu_id, new_description):
        """Updates a menu item's description.
        
        Args:            
            menu_id: id of the menu item to modify
            new_description: new description of the menu item
        """

        menu = self.get_menu(menu_id)
        if menu:
            menu.description = new_description
            self.persist(menu)


    def set_menu_price(self, menu_id, new_price):
        """Updates a menu item's price.
        
        Args:            
            menu_id: id of the menu item to modify
            new_price: new price of the menu item
        """

        menu = self.get_menu(menu_id)
        if menu:
            menu.price = new_price
            self.persist(menu)


    def set_menu_course(self, menu_id, new_course):
        """Updates a menu item's course field.
        
        Args:            
            menu_id: id of the menu item to modify
            new_course: new course value of the item
        """

        menu = self.get_menu(menu_id)
        if menu:
            menu.course = new_course
            self.persist(menu)


    def set_menu_image(self, menu_id, filename):
        """Updates a menu item's image.
        
        Args:            
            menu_id: id of the menu item to modify
            filename: new filename of the menu item
        """

        menu = self.get_menu(menu_id)
        if menu:
            menu.image = filename
            self.persist(menu)


    def add_menu_item(self, rest_id, new_name, user_id):
        """Creates a menu item with the parameters passed.
        
        Args:
            rest_id: id of the restaurant where the item belongs. Foreign Key
                on Restaurants
            new_name: name of the menu item
            user_id: owner of the menu item. Foreign Key on Users.
        """

        new_menu = MenuItem(name = new_name, restaurant_id = rest_id, user_id = user_id)
        self.persist(new_menu)


    def delete_menu(self, menu_id):
        """Deletes a menu item from the DB.
        
        Args:            
            menu_id: id of the menu item to delete
        """

        menu = self.get_menu(menu_id)
        if menu:
            self.discontinue(menu)
