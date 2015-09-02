from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import create_engine

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('adopter', Integer, ForeignKey('adopter.id')),
    Column('puppy', Integer, ForeignKey('puppy.id'))
)

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    maximum_capacity = Column(Integer)
    current_occupancy = Column(Integer)

    @hybrid_property
    def get_occupancy(self):
        return self.current_occupancy

    @get_occupancy.setter
    def get_occupancy(self, value):
        self.current_occupancy = value

class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    weight = Column(Numeric(10))
    profile = relationship("Profile", uselist=False, backref="puppy")

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    puppy_id = Column(Integer, ForeignKey('puppy.id'))
    photo_url = Column(String)
    description = Column(String(500))
    special_needs = Column(String(500))

class Adopter(Base):
    __tablename__ = 'adopter'
    id = Column(Integer, primary_key=True)
    puppies = relationship("Puppy", secondary=association_table)
    

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.create_all(engine)
