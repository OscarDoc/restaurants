import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)

    # Owner User
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    menuItems = relationship("MenuItem", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.user.name
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    image = Column(String(80), default=None)

    # Belonging Restaurant
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    # Owner User
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'course': self.course
        }



#engine = create_engine('sqlite:///restaurantmenu.db')
engine = create_engine("postgresql://wqazmtporkwsid:VYePuHFUk3fAS2HOYpl6gcH9g5@ec2-54-235-153-179.compute-1.amazonaws.com:5432/deeehql62re7uk")


Base.metadata.create_all(engine)
