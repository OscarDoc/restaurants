from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from puppies import *
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# EXERCICE 2
# 2.1. Query all of the puppies and return the results in ascending alphabetical order
def get_all_puppies():
    return session.query(Puppy).order_by(asc(Puppy.name)).all()

# 2.2. Query all of the puppies that are less than 6 months old, youngest first
def get_young_puppies():
    today = datetime.date.today()
    before = today - datetime.timedelta(days = 180)
    return session.query(Puppy).filter(Puppy.dateOfBirth.between(before, today))\
            .order_by(desc(Puppy.dateOfBirth))\
            .all()

# 2.3. Query all puppies by ascending weight
def get_puppies_by_weight():
    today = datetime.date.today()
    before = today - datetime.timedelta(days = 180)
    return session.query(Puppy).filter(Puppy.dateOfBirth.between(before, today))\
            .order_by(desc(Puppy.dateOfBirth))\
            .all()

# 2.4. Query all puppies grouped by the shelter in which they are staying
def get_shelters():
    return session.query(Shelter).order_by(asc(Shelter.name)).all()

def get_puppies_in_shelter(shelter):
    return session.query(Puppy).filter(Puppy.shelter == shelter)\
            .order_by(Puppy.name)\
            .all()

# EXERCISE 3 (associations)
# 3.1. Puppy have profiles
def get_puppy_profile(puppy):
    return session.query(PuppyProfile).filter(PuppyProfile.puppy == puppy).one()

# 3.2. Puppies can be adopted
def adopt_puppy(puppy_id, adopter_list_ids):
    puppy = session.query(Puppy).filter(Puppy.id == puppy_id).one()
    puppy.shelter_id = None

    for adopter in adopter_list_ids:
        adoption_link = PuppyAdopterLink(adopter_id = adopter, puppy_id = puppy.id)
        session.add(adoption_link)
    session.add(puppy)
    session.commit()

    print puppy.name, "adopted by:"
    for link in puppy.adopters:
        adopter = session.query(Adopter).filter(Adopter.id == link.adopter_id).one()
        print " -", adopter.name


# EXERCISE 4 (shelter occupancy)
def get_shelter_occupancy(shelter_id):
	return session.query(Puppy, Shelter).join(Shelter).filter(Shelter.id == shelter_id).count()

def get_shelter_capacity(shelter_id):
	return session.query(Shelter.maximum_capacity).filter(Shelter.id == shelter_id).one()


# EXERCISE 5 (add puppies to shelters checking occupancy)
def add_puppy_to_shelter(puppy_id, shelter_id):
    occupancy = get_shelter_occupancy(shelter_id)
    capacity = get_shelter_capacity(shelter_id)
    if(occupancy < capacity):
        sheltered_puppy = session.query(Puppy).filter(Puppy.id == puppy_id).one()
        sheltered_puppy.shelter_id = shelter_id
        session.add(sheltered_puppy)
        session.commit()
        print "Puppy added to shelter."
    else:
        unsheletered_puppy = session.query(Puppy).filter(Puppy.id == puppy_id).one()
        print '%s has been put to sleep.' % unsheletered_puppy.name
        session.delete(unsheletered_puppy)
        session.commit()


print "1. All puppies in alphabetical order:"
for puppy in get_all_puppies():
    print puppy.name

print "2. Puppies less than 6 months old in age order:"
for puppy in get_young_puppies():
    print puppy.name, puppy.dateOfBirth

print "3. All puppies in weight order:"
for puppy in get_puppies_by_weight():
    print puppy.name, puppy.weight

print "4. Puppies grouped by shelter:"
for shelter in get_shelters():
    print shelter.name
    for puppy in get_puppies_in_shelter(shelter):
        print " -", puppy.name

print "5. Puppies with profiles"
for puppy in get_all_puppies():
    profile = get_puppy_profile(puppy)
    print puppy.name, profile.picture

print "7. Shelter occupancies BEFORE adoptions:"
for shelter in get_shelters():
    print shelter.name, ":", get_shelter_occupancy(shelter.id)

print "6. Adopted puppies"
adopt_puppy(1, [1])
adopt_puppy(2, [2,3,4])
adopt_puppy(3, [2,3,4])
adopt_puppy(4, [5])
adopt_puppy(5, [6])

print "7. Shelter occupancies AFTER adoptions:"
for shelter in get_shelters():
    print shelter.name, ":", get_shelter_occupancy(shelter.id)

add_puppy_to_shelter(2,1)
print "7. Shelter occupancies AFTER adding puppy to shelter:"
for shelter in get_shelters():
    print shelter.name, ":", get_shelter_occupancy(shelter.id)
