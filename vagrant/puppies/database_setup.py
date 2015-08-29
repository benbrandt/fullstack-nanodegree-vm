import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Shelter(Base):

    __tablename__ = 'shelter'

    name = Column(String(80), nullable = False)
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(12))
    email = Column(String(80))
    id = Column(Integer, primary_key = True)

class Puppy(Base):

    __tablename__ = 'puppy'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    date_of_birth = Column(Date)
    breed = Column(String(80))
    gender = Column(String(8))
    weight = Column(Integer)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    restaurant = relationship(Shelter)

engine = create_engine('sqlite:///puppies.db')
Base.metadata.create_all(engine)
